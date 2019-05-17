# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ZhiwangPipeline(object):
    """
        在此处写保存文件代码
    """
    def process_item(self, item, spider):
        return item
