# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BailfundScrapyPipeline:
    def process_item(self, item, spider):
        return item

    def file_path(self, request, response=None, info=None):
        url = request.irl
        file_name: str = request.url.split("/")[-1]
        return f"{file_name}.pdf"
