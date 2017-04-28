# -*- coding: utf-8 -*-
from items.biding import biding_gov
from utils.toDB import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
# 河南周口招投标网站
# 其他信息


class LianjiaSpider(CrawlSpider):
    name = "zhoukou.py"

    allowed_domains = ["zkggzyjy.gov.cn"]

    start_urls = [
        "http://www.zkggzyjy.gov.cn/zkweb/"
    ]

    rules = [
        # 匹配正则表达式,处理下一页
        Rule(LinkExtractor(allow=('',), deny=(r'.*(jyxx)|(00200[1-4])|(cqjy)|(tdjy).*',), unique=True), follow=True, callback='parse_item')
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
        bid_henan_ZhouKou

        Tomogo(
            items["url"],
            items["info"],
            items["create_time"],
            items["update_time"]
        )





















