import scrapy

from ..items import JobOpeningItem


class JPMCSpider(scrapy.Spider):
    name = "jpmc"
    company_website = "https://www.jpmorganchase.com/careers"
    allowed_domains = ["jpmc.fa.oraclecloud.com"]
    # start_urls = ["https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions"]
    job_url_template = 'https://jpmc.fa.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder=ById;Id="{}",siteNumber=CX_1001'
    job_url_link = "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions/job/{}"

    def start_requests(self):

        url = (
            "https://jpmc.fa.oraclecloud.com/hcmRestApi/resources/latest/"
            "recruitingCEJobRequisitions?onlyData=true&expand=requisitionList."
            "secondaryLocations,flexFieldsFacet.values,requisitionList."
            "requisitionFlexFields&finder=findReqs;siteNumber=CX_1001,facetsList="
            "LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;"
            "ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS,limit=1000,sortBy=POSTING_DATES_DESC"
        )

        yield scrapy.Request(url=url, callback=self.parse_start_requests)

    def parse_start_requests(self, response):

        json_response = response.json()
        job_ids = [x["Id"] for x in json_response["items"][0]["requisitionList"]]

        for job_id in job_ids:
            yield scrapy.Request(
                url=self.job_url_template.format(job_id), callback=self.parse
            )

    def parse(self, response):
        data = response.json()["items"][0]
        item = JobOpeningItem()
        item["industry"] = "Finance"
        item["function"] = data.get("JobFunction")
        item["company"] = "JP Morgan & Chase"
        item["job_id"] = data.get("Id")
        item["role_name"] = data.get("Title")
        item["locations"] = [
            {
                "country": None,
                "alpha2": data.get("workLocation")[0].get("Country"),
                "city": data.get("workLocation")[0].get("TownOrCity"),
                "region1": data.get("workLocation")[0].get("Region1"),
                "region2": data.get("workLocation")[0].get("Region2"),
                "region3": data.get("workLocation")[0].get("Region3"),
            }
        ]
        item["seniority"] = data.get("RequsitionType")
        item["education"] = []
        item["certificates"] = []
        item["language"] = []
        item["skills"] = []
        item["schedule"] = data.get("JobSchedule")
        item["remote"] = None
        item["travel"] = data.get("InternationalTravelRequired")
        item["salary"] = None
        item["benefits"] = []
        item["job_description"] = "\n".join(
            [
                data.get("ExternalDescriptionStr"),
                data.get("CorporateDescriptionStr"),
                data.get("OrganizationDescriptionStr"),
            ]
        )
        item["short_description"] = data.get("ShortDescriptionStr")
        item["company_website"] = self.company_website
        item["is_professional"] = True
        item["posted_datetime"] = data.get("ExternalPostedStartDate")
        item["expiration_datetime"] = None
        item["start_date"] = None
        item["job_url"] = self.job_url_link.format(data.get("Id"))

        yield item
