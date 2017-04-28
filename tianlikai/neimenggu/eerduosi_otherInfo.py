# -*- coding: utf-8 -*-
# 内蒙古鄂尔多斯招投标网站
# 其他信息
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime

class LianjiaSpider(CrawlSpider):
    name = "eerduosi_otherInfo.py"

    allowed_domains = ["ordosggzyjy.com"]

    start_urls = [
        "http://www.ordosggzyjy.com/TPFront/"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*(jsgc)|(zfcg)|(tdjy)|(kqjy)|(cqtd)|(jssh)|(showmeikuanginfo)|(tjfx).*',), unique=True), follow=True, callback='parse_item')
    ]

    def parse_item(self, response):
        print response.url
        items = biding_gov()
        items["url"] = response.url
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info)

        db = MongodbHandle("172.20.3.10 ", 27017, "Bid_Other_info")
        db.get_insert(
            "bid_neimenggu_EErDuoSi",
            {
                "url": items["url"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )






















