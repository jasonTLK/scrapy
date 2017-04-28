# -*- coding: utf-8 -*-
#  内蒙古锡林郭勒盟招投标网站
#  其他信息
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime

class LianjiaSpider(CrawlSpider):
    name = "xilinguolemeng_otherInfo.py"

    allowed_domains = ["xmzwggzy.com"]

    start_urls = [
        "http://www.xmzwggzy.com/xmweb/"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*009003[1-5].*',), unique=True), follow=True, callback='parse_item')
    ]

    def parse_item(self, response):
        print response.url
        items = biding_gov()
        items["url"] = response.url
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info).decode('gbk')
        db = MongodbHandle("172.20.3.10 ", 27017, "Bid_Other_info")
        db.get_insert(
            "bid_neimenggu_XiLinGuoLeMeng",
            {
                "url": items["url"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )























