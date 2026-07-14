import scrapy

from ..items import JobOpeningItem


class VanguardSpider(scrapy.Spider):
    name = "vanguard"
    company_url = "https://www.vanguardjobs.com"
    api_url = (
        "https://jobsapi-internal.m-cloud.io/api/job?callback=CWS.jobs."
        "jobCallback&sortfield=open_date&sortorder=descending&facet[]="
        "is_internal:External&Limit={:d}&Organization=1938&offset=1&fuzzy="
        "false&useBooleanKeywordSearch=true"
    )

    def start_requests(self):

        yield scrapy.Request(
            url=self.api_url.format(300), callback=self.parse, meta={"query_limit": 300}
        )

    def parse(self, response):
        import json

        data = json.loads(response.text[21:-1])
        total_counts = data["totalHits"]

        if total_counts >= response.meta["query_limit"]:
            query_limit = response.meta["query_limit"] + 100
            yield scrapy.Request(
                url=self.api_url.format(query_limit),
                callback=self.parse,
                meta={"query_limit": query_limit},
                dont_filter=True,
            )

        else:
            for job in data["queryResult"]:
                item = JobOpeningItem()
                item["industry"] = job.get("industry")
                item["function"] = job.get("function")
                item["company"] = job.get("company_name")
                item["job_id"] = job.get("id")
                item["role_name"] = job.get("title")
                locations = []
                locations.append(
                    {
                        "country": None,
                        "alpha2": job.get("primary_country"),
                        "city": job.get("primary_city"),
                        "region1": job.get("primary_state"),
                        "region2": None,
                        "region3": None,
                    }
                )
                for loc in job.get("addtnl_locations"):
                    locations.append(
                        {
                            "country": None,
                            "alpha2": loc.get("addtnl_city"),
                            "city": loc.get("aaddtnl_city"),
                            "region1": loc.get("addtnl_state"),
                            "region2": None,
                            "region3": None,
                        }
                    )
                item["locations"] = locations
                item["seniority"] = job.get("level")
                item["education"] = (
                    job.get("education") if job.get("education") != "" else None
                )
                item["certificates"] = []
                item["language"] = [job.get("language")]
                item["skills"] = []
                item["schedule"] = job.get("employmen_type")
                item["remote"] = job.get("compliment")
                item["travel"] = job.get("travel") if job.get("travel") != "" else None
                item["salary"] = None
                item["benefits"] = []
                item["job_description"] = job.get("description")
                item["short_description"] = None
                item["company_website"] = self.company_url
                item["is_professional"] = job.get("level", "").strip() != "Students"
                item["posted_datetime"] = job.get("update_date")
                item["expiration_datetime"] = None
                item["start_date"] = None

                yield item
