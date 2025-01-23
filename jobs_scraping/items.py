# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import scrapy.item


class JobOpeningItem(scrapy.Item):
    # define the fields for your item here like:
    industry = scrapy.Field()
    function = scrapy.Field()
    company = scrapy.Field()
    job_id = scrapy.Field()
    role_name = scrapy.Field()
    locations = scrapy.Field()
    seniority = scrapy.Field()
    education = scrapy.Field()
    certificates = scrapy.Field()
    language = scrapy.Field()
    skills = scrapy.Field()
    schedule = scrapy.Field()
    remote = scrapy.Field()
    travel = scrapy.Field()
    salary = scrapy.Field()
    benefits = scrapy.Field()
    job_description = scrapy.Field()
    short_description = scrapy.Field()
    company_website = scrapy.Field()
    is_professional = scrapy.Field()
    posted_datetime = scrapy.Field()
    expiration_datetime = scrapy.Field()
    start_date = scrapy.Field()
    job_url = scrapy.Field()


# item["industry"] =
# item["function"] =
# item["company"] =
# item["job_id"] =
# item["role_name"] =
# item["locations"] =
# item["seniority"] =
# item["education"] =
# item["certificates"] =
# item["language"] =
# item["skills"] =
# item["schedule"] =
# item["remote"] =
# item["travel"] =
# item["salary"] =
# item["benefits"] =
# item["job_description"] =
# item["short_description"] =
# item["company_website"] =
# item["is_professional"] =
# item["posted_datetime"] =
# item["expiration_datetime"] =
# item["start_date"] =
# item["job_url"] =
