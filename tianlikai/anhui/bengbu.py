# -*- coding: utf-8 -*-
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
# 安徽蚌埠招投标网站
# 其他信息


class LianjiaSpider(CrawlSpider):
    name = "bengbu.py"

    allowed_domains = ["bbztb.cn"]

    start_urls = [
        "http://www.bbztb.cn/bbfwweb/default.aspx"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*(jyxx)|(csap)|(zbgs).*',), unique=True), follow=True, callback='parse_item')
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

        db = MongodbHandle("172.20.3.10 ", 27017, "Bid_Other_info")
        db.get_insert(
            "bid_anhui_BengBu",
            {
                "url": items["url"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )




















