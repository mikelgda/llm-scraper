from collections.abc import Iterable

import scrapy

from ..items import JobOpeningItem


class MorganStanleyGraduatesSpider(scrapy.Spider):
    name = "morgan_stanley_graduates"
    company_url = "https://www.morganstanley.com/people/experienced-professionals"
    url_gradutes = (
        "https://morganstanley.tal.net/vx/lang-en-GB/mobile-0/brand-2/user-"
        "7803981/xf-dd9cde5f40fb/candidate/jobboard/vacancy/1/adv/"
    )
    job_url = "https://morganstanley.tal.net/vx/candidate/apply/{}"

    def start_requests(self):

        for i in range(50):
            if i == 0:
                yield scrapy.Request(
                    url=self.url_gradutes, callback=self.parse_start_requests
                )
            if i > 0:
                yield scrapy.Request(
                    url=self.url_gradutes + f"?start={50 * i}",
                    callback=self.parse_start_requests,
                )

    def parse_start_requests(self, response):

        links = [x.attrib["href"] for x in response.selector.css("a.subject")]

        for link in links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        details = response.selector.css("div[data-type=LOOKUP]")
        description = response.selector.css("div[data-type=LARGETEXT]")

        job_dict = {}

        job_dict["title"] = (
            response.selector.css("div#vac_desc").css("h1::text").get().strip()
        )

        for field in details:
            field_name = (
                field.css("label")
                .css("span::text")
                .get()
                .lower()
                .replace(" ", "_")
                .strip()
            )
            field_value = field.css("div[id*=datafield]::text").get().strip()

            job_dict[field_name] = field_value

        job_dict["job_description"] = "\n".join(
            [
                x.strip()
                for x in description.css("div[id*=datafield] *::text")[:-4].getall()
            ]
        )
        item = JobOpeningItem()

        item["industry"] = "Finance"
        item["function"] = job_dict.get("education_level")
        item["company"] = "Morgan Stanley"
        item["job_id"] = None
        item["role_name"] = job_dict.get("title")
        item["locations"] = [
            {
                "country": None,
                "alpha2": None,
                "city": job_dict.get("city"),
                "region1": None,
                "region2": None,
                "region3": None,
            }
        ]
        item["seniority"] = job_dict.get("job_level")
        item["education"] = []
        item["certificates"] = []
        item["language"] = []
        item["skills"] = []
        item["schedule"] = None
        item["remote"] = None
        item["travel"] = None
        item["salary"] = None
        item["benefits"] = []
        item["job_description"] = job_dict.get("job_description")
        item["short_description"] = None
        item["company_website"] = self.company_url
        item["is_professional"] = False
        item["posted_datetime"] = None
        item["expiration_datetime"] = None
        item["start_date"] = None
        item["job_url"] = response.url

        yield item


class MorganStanleyExperiencedSpider(scrapy.Spider):
    name = "morgan_stanley_experienced"
    company_url = "https://www.morganstanley.com/people/experienced-professionals"
    job_url = "https://morganstanley.eightfold.ai/careers/job/{}"
    page_length = 10
    url_experienced = (
        "https://morganstanley.eightfold.ai/api/apply/v2/jobs?domain="
        "morganstanley.com&start={:d}&num={:d}&sort_by=relevance"
    )
    job_description_url = (
        "https://morganstanley.eightfold.ai/api/apply/v2/jobs/{:d}?domain="
        "morganstanley.com"
    )
    job_insights_url = (
        "https://morganstanley.eightfold.ai/api/apply/v2/jobs/{:d}"
        "/insights?domain=morganstanley.com"
    )

    def start_requests(self):
        yield scrapy.Request(
            url=self.url_experienced.format(0, self.page_length),
            callback=self.parse_start_requests,
        )

    def parse_start_requests(self, response):

        total_count = sum(response.json()["facets"]["Country"].values())

        if total_count % self.page_length == 0:
            start_values = range(total_count // self.page_length)
        else:
            start_values = range(total_count // self.page_length + 1)

        for value in start_values:
            yield scrapy.Request(
                url=self.url_experienced.format(
                    value * self.page_length, self.page_length
                ),
                callback=self.parse_job_list,
                dont_filter=True,
            )

    def parse_job_list(self, response):

        positions = response.json().get("positions")

        for job in positions:
            yield scrapy.Request(
                url=self.job_description_url.format(job["id"]),
                callback=self.parse_job_description,
            )

    def parse_job_description(self, response):
        job_description = response.json()

        job_id = job_description["id"]

        yield scrapy.Request(
            url=self.job_insights_url.format(job_id),
            callback=self.add_job_insights,
            meta={"job_description": job_description},
        )

    def add_job_insights(self, response):

        job_insights = response.json()

        data = response.meta["job_description"]
        # job_description["job_insights"] = job_insights
        item = JobOpeningItem()

        item["industry"] = "Finance"
        item["function"] = data.get("department")
        item["company"] = "Morgan Stanley"
        item["job_id"] = data.get("id")
        item["role_name"] = data.get("name")
        locations = []
        for loc in data.get("locations"):
            try:
                city, region, country = loc.split(",")
            except Exception:
                continue
            locations.append(
                {
                    "country": country,
                    "alpha2": None,
                    "city": city,
                    "region1": region,
                    "region2": None,
                    "region3": None,
                }
            )
        item["locations"] = locations
        item["seniority"] = [get_most_frequent_attribute(job_insights.get("seniority"))]
        item["education"] = [get_most_frequent_attribute(job_insights.get("degrees"))]
        item["certificates"] = []
        item["language"] = [data.get("locale")]
        item["skills"] = list(job_insights.get("skills").keys())
        item["schedule"] = None
        item["remote"] = None
        item["travel"] = None
        item["salary"] = None
        item["benefits"] = None
        item["job_description"] = data.get("job_description")
        item["short_description"] = None
        item["company_website"] = self.company_url
        item["is_professional"] = True
        item["posted_datetime"] = data.get("t_update")
        item["expiration_datetime"] = None
        item["start_date"] = None
        item["job_url"] = self.job_url.format(data.get("id"))

        yield item


def get_most_frequent_attribute(attributes):
    most_frequent_times = 0
    for key, val in attributes.items():
        if val > most_frequent_times:
            most_frequent_times = val

    labels = []
    for key, val in attributes.items():
        if most_frequent_times == val:
            labels.append(key)

    return ", ".join(labels)
