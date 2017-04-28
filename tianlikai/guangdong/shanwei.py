# -*- coding: utf-8 -*-
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
# 广东汕尾招投标网站
# 其他信息


class LianjiaSpider(CrawlSpider):
    name = "shanwei.py"

    allowed_domains = ["swggzy.cn"]

    start_urls = [
        "http://www.swggzy.cn/"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*(a8950dedd38a4103973c8140784ab4d3)|(4c9864644f2441718b124ff183daf3fd)|(62d94c6d524040fbac4435631d883cbf)|(b7a24351888f44fabcfa6d35b45fc1cc).*',), unique=True), follow=True, callback='parse_item')
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
            "bid_guangdong_ShanWei",
            {
                "url": items["url"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )




















