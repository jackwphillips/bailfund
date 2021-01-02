import scrapy
import requests
import sys

class DocketViewStateSpider(scrapy.Spider):
    name = 'docketspider-viewstate'
    url = 'https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx'
    start_urls = [url]
    download_delay = 2
    allowed_domains = ['ujsportal.pacourts.us']

    def parse(self, response):
        pat = "captchaAnswer.*'([0-9]+)"
        captcha = response.css('script::text').re_first(pat)
        try:
            yield scrapy.FormRequest(
                self.url,
                formdata={
                "__EVENTTARGET": "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$ddlSearchType",
                "__EVENTARGUMENT": "", 
                "__LASTFOCUS": "", 
                "__VIEWSTATE": response.css('input#__VIEWSTATE::attr(value)').get(),
                "__VIEWSTATEGENERATOR": response.css('input#__VIEWSTATEGENERATOR::attr(value)').get(),
                "__SCROLLPOSITIONX": "0", 
                "__SCROLLPOSITIONY": "0",
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$ddlSearchType": "DateFiled",
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDocketNumber$ddlCounty": "", 
                "ctl00$ctl00$ctl00$ctl07$captchaAnswer": captcha
                },
                callback=self.parse_county
            )
        except:
            print("Something went wrong")
            sys.exit(1)

    def parse_county(self, response):
        print("####IN COUNTY####")
        yield scrapy.FormRequest.from_response(
            response,
            formdata={
            "ctl00$ctl00$ctl00$ScriptManager": "ctl00$ctl00$ctl00$ScriptManager|ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCounty",
            "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCounty": "Montgomery",
            "ASYNCPOST": "true"
            },
            callback=self.parse_judges        
        )

    def parse_judges(self, response):
        print("####IN JUDGES####")
        judges = response.css('#ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_ddlCourtOffice > option ::attr(value)').getall()
        while('' in judges):
            judges.remove('')
        for judge in [judges[0]]:
            yield scrapy.FormRequest(
                self.url,
                formdata={
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "", 
                "__LASTFOCUS": "", 
                "__VIEWSTATE": response.css('input#__VIEWSTATE::attr(value)').get(),
                "__VIEWSTATEGENERATOR": response.css('input#__VIEWSTATEGENERATOR::attr(value)').get(),
                "__SCROLLPOSITIONX": "0", 
                "__SCROLLPOSITIONY": "0",
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$ddlSearchType": "DateFiled",
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDocketNumber$ddlCounty": "Montgomery", 
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCourtOffice": judge,
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$beginDateChildControl$DateTextBox": "12/01/2020",
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$endDateChildControl$DateTextBox": "12/31/2020",
                "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch": "Search",
                "ctl00$ctl00$ctl00$ctl07$captchaAnswer": response.css('input#ctl00_ctl00_ctl00_ctl07_captchaAnswer::attr(value)').get() 
                },
                callback=self.parse_dockets_table
            )

    def parse_test(self, response):
        print("####IN TEST####")
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        yield {'Test': "Passed"}

    def parse_dockets_table(self, response):
        urls = response.xpath('//*[@id="ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket"]//@href').getall()
        while('#' in urls):
            urls.remove('#')
        for url in urls[:3]:
            filename = f'{url}.pdf'
            pdf = requests.get(f'https://ujsportal.pacourts.us/DocketSheets/{url}')
            with open(filename, 'wb') as f:
                f.write(pdf.content)
    
    def parse_results(self, response):
        for quote in response.css("div.quote"):
            yield {
                'quote': quote.css('span.content ::text').extract_first(),
                'author': quote.css('span.author ::text').extract_first(),
                'tag': quote.css('span.tag ::text').extract_first(),
            }
