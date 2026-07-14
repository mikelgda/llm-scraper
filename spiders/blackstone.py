import scrapy

from ..items import JobOpeningItem


class BlackstoneExperiencedSpider(scrapy.Spider):
    name = "blackstone_experienced"
    company_website = (
        "https://blackstone.wd1.myworkdayjobs.com/en-US/Blackstone_Careers"
    )
    page_size = 20
    api_url = (
        "https://blackstone.wd1.myworkdayjobs.com/wday/cxs/blackstone/"
        "Blackstone_Careers/jobs"
    )
    job_url = "https://blackstone.wd1.myworkdayjobs.com/wday/cxs/blackstone/Blackstone_Careers/"

    def get_query_body(self, offset=0):
        return {
            "appliedFacets": {},
            "limit": self.page_size,
            "offset": offset,
            "searchText": "",
        }

    def start_requests(self):

        body = self.get_query_body()

        yield scrapy.http.JsonRequest(
            url=self.api_url,
            callback=self.parse_start_requests,
            data=body,
            method="POST",
        )

    def parse_start_requests(self, response):

        json_response = response.json()
        total_counts = json_response["total"]

        if total_counts % self.page_size == 0:
            offset_values = range(total_counts // self.page_size)
        else:
            offset_values = range(total_counts // self.page_size + 1)

        for offset_value in offset_values:
            body = self.get_query_body(offset_value * self.page_size)

            yield scrapy.http.JsonRequest(
                url=self.api_url,
                callback=self.parse_links,
                data=body,
                method="POST",
                dont_filter=True,
            )

    def parse_links(self, response):
        postings = response.json()["jobPostings"]

        links = [self.job_url + x["externalPath"] for x in postings]

        for link in links:
            yield scrapy.Request(url=link, headers={"Accept": "application/json"})

    def parse(self, response):
        data = response.json()["jobPostingInfo"]
        item = JobOpeningItem()
        item["industry"] = "Finance"
        item["function"] = None
        item["company"] = "Blackstone"
        item["job_id"] = data.get("id")
        item["role_name"] = data.get("title")
        item["locations"] = [
            {
                "country": (
                    data.get("jobRequisitionLocation", {})
                    .get("country", {})
                    .get("descriptor")
                ),
                "alpha2": (
                    data.get("jobRequisitionLocation", {})
                    .get("country", {})
                    .get("alpha2Code")
                ),
                "city": data.get("jobRequisitionLocation", {}.get("descriptor")),
                "regon1": None,
                "region2": None,
                "region3": None,
            }
        ]
        item["seniority"] = None
        item["education"] = []
        item["certificates"] = []
        item["language"] = []
        item["skills"] = []
        item["schedule"] = data.get("timeType")
        item["remote"] = None
        item["travel"] = []
        item["salary"] = None
        item["benefits"] = []
        item["job_description"] = data.get("jobDescription")
        item["short_description"] = None
        item["company_website"] = self.company_website
        item["is_professional"] = True
        item["posted_datetime"] = data.get("postedOn")
        item["expiration_datetime"] = None
        item["start_date"] = data.get("startDate")
        item["job_url"] = data.get("externalUrl")

        yield item


class BlackstoneStudentSpider(scrapy.Spider):
    name = "blackstone_students"
    company_website = (
        "https://blackstone.wd1.myworkdayjobs.com/en-US/Blackstone_Campus_Careers"
    )
    page_size = 20
    api_url = (
        "https://blackstone.wd1.myworkdayjobs.com/wday/cxs/blackstone/"
        "Blackstone_Campus_Careers/jobs"
    )
    job_url = "https://blackstone.wd1.myworkdayjobs.com/wday/cxs/blackstone/Blackstone_Campus_Careers/"

    def get_query_body(self, offset=0):
        return {
            "appliedFacets": {},
            "limit": self.page_size,
            "offset": offset,
            "searchText": "",
        }

    def start_requests(self):

        body = self.get_query_body()

        yield scrapy.http.JsonRequest(
            url=self.api_url,
            callback=self.parse_start_requests,
            data=body,
            method="POST",
        )

    def parse_start_requests(self, response):

        json_response = response.json()
        total_counts = json_response["total"]

        if total_counts % self.page_size == 0:
            offset_values = range(total_counts // self.page_size)
        else:
            offset_values = range(total_counts // self.page_size + 1)

        for offset_value in offset_values:
            body = self.get_query_body(offset_value * self.page_size)

            yield scrapy.http.JsonRequest(
                url=self.api_url,
                callback=self.parse_links,
                data=body,
                method="POST",
                dont_filter=True,
            )

    def parse_links(self, response):
        postings = response.json()["jobPostings"]

        links = [self.job_url + x["externalPath"] for x in postings]

        for link in links:
            yield scrapy.Request(url=link, headers={"Accept": "application/json"})

    def parse(self, response):
        data = response.json()["jobPostingInfo"]
        item = JobOpeningItem()
        item["industry"] = "Finance"
        item["function"] = None
        item["company"] = "Blackstone"
        item["job_id"] = data.get("id")
        item["role_name"] = data.get("title")
        item["locations"] = [
            {
                "country": (
                    data.get("jobRequisitionLocation", {})
                    .get("country", {})
                    .get("descriptor")
                ),
                "alpha2": (
                    data.get("jobRequisitionLocation", {})
                    .get("country", {})
                    .get("alpha2Code")
                ),
                "location_city": data.get(
                    "jobRequisitionLocation", {}.get("descriptor")
                ),
                "location_region_1": None,
                "location_region_2": None,
                "location_region_3": None,
            }
        ]
        item["seniority"] = None
        item["education"] = []
        item["certificates"] = []
        item["language"] = []
        item["skills"] = []
        item["schedule"] = data.get("timeType")
        item["remote"] = None
        item["travel"] = []
        item["salary"] = None
        item["benefits"] = []
        item["job_description"] = data.get("jobDescription")
        item["short_description"] = None
        item["company_website"] = self.company_website
        item["is_professional"] = False
        item["posted_datetime"] = data.get("postedOn")
        item["expiration_datetime"] = None
        item["start_date"] = data.get("startDate")
        item["job_url"] = data.get("externalUrl")

        yield item
