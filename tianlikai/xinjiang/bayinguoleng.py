# -*- coding: utf-8 -*-
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
# 新疆巴州招投标网站
# 其他信息


class LianjiaSpider(CrawlSpider):
    name = "bayinguoleng.py"

    allowed_domains = ["czj.xjbz.gov.cn"]

    start_urls = [
        "http://czj.xjbz.gov.cn/zfcg/news/index.asp?classid=BH7TAUHY1B5Y96G"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*classid=(JQNRJRPDMX24GOD)|(S6N11KK2VFT0265).*',), unique=True), follow=True, callback='parse_item')
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
            "bid_xinjiang_BaYinGuoLeng",
            {
                "url": items["url"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )





















