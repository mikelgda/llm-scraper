import scrapy

from ..items import JobOpeningItem


class GoldmanSachsSpider(scrapy.Spider):
    name = "goldman_sachs"
    company_website = "https://higher.gs.com/"
    db_url = "https://api-higher.gs.com/gateway/api/v1/graphql"
    description_url = "https://higher.gs.com/roles/{}"
    page_size = 10

    def get_query_body(self, page):
        return {
            "operationName": "GetRoles",
            "variables": {
                "searchQueryInput": {
                    "page": {
                        "pageSize": self.page_size,
                        "pageNumber": page,
                    },
                    "sort": {"sortStrategy": "RELEVANCE", "sortOrder": "DESC"},
                    "filters": [],
                    "experiences": ["PROFESSIONAL", "EARLY_CAREER"],
                    "searchTerm": "",
                }
            },
            "query": "query GetRoles($searchQueryInput: RoleSearchQueryInput!) {\n  roleSearch(searchQueryInput: $searchQueryInput) {\n    totalCount\n    items {\n      roleId\n      corporateTitle\n      jobTitle\n      jobFunction\n      locations {\n        primary\n        state\n        country\n        city\n        __typename\n      }\n      status\n      division\n      skills\n      jobType {\n        code\n        description\n        __typename\n      }\n      externalSource {\n        sourceId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
        }

    def start_requests(self):

        body = self.get_query_body(0)

        yield scrapy.http.JsonRequest(
            url=self.db_url,
            callback=self.parse_start_requests,
            data=body,
            method="POST",
        )

    def parse_start_requests(self, response):

        json_response = response.json()
        total_counts = json_response["data"]["roleSearch"]["totalCount"]

        if total_counts % self.page_size == 0:
            page_indices = range(total_counts // self.page_size)
        else:
            page_indices = range(total_counts // self.page_size + 1)

        for i in page_indices:
            body = self.get_query_body(i)

            yield scrapy.http.JsonRequest(
                url=self.db_url,
                callback=self.parse_job_summary,
                data=body,
                method="POST",
                dont_filter=True,
            )

    def parse_job_summary(self, response):
        json_response = response.json()

        for job in json_response["data"]["roleSearch"]["items"]:
            yield scrapy.Request(
                url=self.description_url.format(
                    job.get("externalSource").get("sourceId")
                ),
                callback=self.parse_job_description,
                meta={"summary": job},
            )

    def parse_job_description(self, response):
        data = response.meta["summary"]
        description = "\n".join(
            [
                selector.get()
                for selector in response.selector.css("div.job-description *::text")
            ]
        )
        item = JobOpeningItem()
        item["industry"] = "Finance"
        item["function"] = data.get("division")
        item["company"] = "Goldman Sachs"
        item["job_id"] = data.get("externalSource").get("sourceId")
        item["role_name"] = data.get("corporateTitle")
        item["locations"] = []
        for loc in data.get("locations"):
            item["locations"].append(
                {
                    "country": loc.get("country"),
                    "alpha2": None,
                    "city": loc.get("city"),
                    "region1": loc.get("state"),
                    "region2": None,
                    "region3": None,
                }
            )

        item["seniority"] = None
        item["education"] = []
        item["certificates"] = []
        item["language"] = []
        item["skills"] = []
        item["schedule"] = None
        item["remote"] = None
        item["travel"] = None
        item["salary"] = None
        item["benefits"] = []
        item["job_description"] = description
        item["short_description"] = None
        item["company_website"] = self.company_website
        item["is_professional"] = True
        item["posted_datetime"] = None
        item["expiration_datetime"] = None
        item["start_date"] = None
        item["job_url"] = self.description_url.format(
            data.get("externalSource", {}).get("sourceId")
        )

        yield item
