# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request

from pathlib import Path
import sys

class BailfundScrapyPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x, meta={'filename': item.get('file_name')}) for x in item.get(self.files_urls_field, [])]


    def file_path(self, request, response=None, info=None, *, item=None):
        url = request.url
        return f'{request.meta["filename"]}'

    def close_spider(self, spider):
        print("#####Closing Spider#####")
        #log = spider.crawler.stats.get_value('log_count/CRITICAL')
        #if spider.crawler.stats.get_value('log_count/CRITICAL') > 0:
        #    raise NameError("Error!")
