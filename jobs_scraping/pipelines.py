# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import datetime
import re

import pymongo

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from .extractors import RegexExtractor
from .processors import CountryCodeMatcher, remove_html

# conutry code and name


class DescriptionFeatureExtractionPipeline:
    re_extractor = RegexExtractor()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        text = remove_html(adapter["job_description"])
        adapter["skills"].extend(self.re_extractor.extract_it_skills(text))
        adapter["certificates"].extend(self.re_extractor.extract_certificates(text))

        if adapter["salary"] is None:
            adapter["salary"] = self.re_extractor.extract_salary_range(text)

        return item


class DateNormalizationPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        company = adapter["company"]
        if company == "Blackstone":
            if adapter.get("start_date"):
                time = datetime.datetime.strptime(adapter["start_date"], "%Y-%m-%d")
                adapter["start_date"] = time.isoformat()
            if adapter.get("posted_datetime"):
                days_delta = re.findall(
                    r"Posted\s+(\d+)\+?\s+Days\s+Ago", adapter["posted_datetime"]
                )
                if days_delta:
                    days_delta = datetime.timedelta(days=int(days_delta[0]))
                    adapter["posted_datetime"] = (
                        datetime.datetime.now(datetime.timezone.utc) - days_delta
                    ).isoformat()
        elif company == "Goldman Sachs":
            pass
        elif company == "JP Morgan & Chase":
            pass
        elif company == "Morgan Stanley":
            if adapter.get("posted_datetime"):
                time = datetime.datetime.fromtimestamp(adapter["posted_datetime"])

                adapter["posted_datetime"] = time.isoformat()
        elif company == "Vanguard":
            pass

        return item


class LocationCompleterPipeline:
    cc_matcher = CountryCodeMatcher()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        locations = adapter.get("locations")
        new_locations = []
        if locations is not None:
            for loc in locations:
                new_locations.append(self.cc_matcher.complete_location(loc))

            adapter["locations"] = new_locations

            return item
        else:
            return item


class FieldTypeValidationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        for key, value in adapter.items():
            if hasattr(value, "__len__"):
                if len(value) == 0:
                    adapter[key] = None

        return item


class MongoPipeline:
    collection_name = "job_requisitions"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "jobs"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        print(self.mongo_db)
        print(self.mongo_uri)
        return item
