# -*- coding: utf-8 -*-
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
# 浙江宁波招投标网站
# 其他信息



class LianjiaSpider(CrawlSpider):
    name = "ningbo.py"

    allowed_domains = ["bidding.gov.cn"]

    start_urls = [
        "http://www.bidding.gov.cn/zhdh.jhtml"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*jyxx.*',), unique=True), follow=True, callback='parse_item')
    ]

    def parse_item(self, response):
        print response.url
        items = biding_gov()
        items["url"] = response.url
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        try:
            items["info"] = "".join(page_info).decode('gbk')
        except:
            items["info"] = "".join(page_info)
        bid_zhejiang_NingBo

        Tomogo(
            items["url"],
            items["info"],
            items["create_time"],
            items["update_time"]
        )





















