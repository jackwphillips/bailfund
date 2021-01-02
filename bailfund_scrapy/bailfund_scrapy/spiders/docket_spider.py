import scrapy
class DocketViewStateSpider(scrapy.Spider):
    name = 'docketspider-viewstate'
    start_urls = ['https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx']
    download_delay = 1.5

    def parse(self, response):
        for judge in response.css('select#ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCourtOffice > option ::attr(value)').getall():
            yield scrapy.FormRequest(
                start_urls[0],
                formdata={
                    'ctl00%24ctl00%24ctl00%24cphMain%24cphDynamicContent%24ddlSearchType': 'DateFiled',
                    'ctl00%24ctl00%24ctl00%24cphMain%24cphDynamicContent%24cphSearchControls%24udsDateFiled%24ddlCounty': 'Montgomery',
                    'ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$beginDateChildControl$DateTextBox': '12/01/2020',
                    'ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$endDateChildControl$DateTextBox': '12/31/2020',
                    'ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch': 'Search',
                    # 'ctl00$ctl00$ctl00$ctl07$captchaAnswer': '955415469',
                    'ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCourtOffice': judge, 

                    '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').get(),
                    '__VIEWSTATEGENERATOR': response.css('input#__VIEWSTATEGENERATOR::attr(value)').get(),
                    '__SCROLLPOSITIONX': response.css('input#__SCROLLPOSITIONX::attr(value)').get(),
                    '__SCROLLPOSITIONY': response.css('input#__SCROLLPOSITION::attr(value)').get()
                },
                callback=self.parse_dockets_table
            )

    def parse_dockets_table(self, response):
        for docket_row in response.css('#ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket > tbody > tr').extract():
            yield docket_row            
#            yield scrapy.FormRequest(
#                'http://quotes.toscrape.com/filter.aspx',
#                formdata={
#                    'author': response.css(
#                        'select#author > option[selected] ::attr(value)'
#                    ).extract_first(),
#                    'tag': tag,
#                    '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first()
#                },
#                callback=self.parse_results,
#            )

    def parse_results(self, response):
        for quote in response.css("div.quote"):
            yield {
                'quote': quote.css('span.content ::text').extract_first(),
                'author': quote.css('span.author ::text').extract_first(),
                'tag': quote.css('span.tag ::text').extract_first(),
            }
