# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
from scrapy.selector import Selector
import json

try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from items.biding import biding_gov
from utils.toDB import *

# 湖北武汉招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "wuhan_zhaobiao.py"
    allowed_domains = ["jy.whzbtb.com"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'middlewares.useragent_middleware.RandomUserAgent': 400,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
            # 'middlewares.proxy_middleware.ProxyMiddleware': 250,
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'middlewares.retry_middleware.RetryWithProxyMiddleware': 300,
            # 'middlewares.timestamp_middleware.TimestampMiddleware': 120
        }
    }


    def start_requests(self):
        urls = [
            "http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoList.do?page="
        ]
        pages = [384]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num) + "&rows=10"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://fz.fjzfcg.gov.cn/n/fzzfcg/queryPageData.do?page=6&rows=20&sid=200100&zzxs=jzcg"
    # ]

    def parse(self, response):
        data = json.loads(response.body)
        data = data['rows']
        ids = []
        names = []
        for i in data:
            ids.append(i['id'])
            names.append(i['constructionPrjName'])
        for i in range(len(names)):
            url = "http://www.jy.whzbtb.com/V2PRTS/WinningPublicityInfoDetail.do?id=" + "".join(ids[i])
            str = "".join(names[i]) + ',' + url
            print url
            yield Request(url=url, callback=self.parse2, meta={"info": str})

    def parse2(self, response):
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = "".join(infos).split(",")[1]
        items["name"] = "".join(infos).split(",")[0]
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info)


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_hubei_WuHan",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )
        print items["url"]
        print items["name"]
