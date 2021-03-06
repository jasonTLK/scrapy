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

# 湖南益阳招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "yiyang_zhongbiao.py"
    allowed_domains = ["ccgp-hunan.gov.cn"]

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
            "http://www.ccgp-hunan.gov.cn:8080/mvc/getNoticeList4WebCity.do?nType=dealNotices&pType=&prcmPrjName=&prcmItemCode=&prcmOrgName=&startDate=&endDate=&area_id=79&page="
        ]
        pages = [17]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num) + "&pageSize=18"
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
            ids.append(i['NOTICE_ID'])
            names.append(i['NOTICE_TITLE'])
        for i in range(len(names)):
            url = "http://www.ccgp-hunan.gov.cn:8080/mvc/viewNoticeContent.do?noticeId=" + str(ids[i]) + "&area_id=79"
            s = "".join(names[i]) + ',' + url
            print url
            yield Request(url=url, callback=self.parse2, meta={"info": names[i]})

    def parse2(self, response):
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = response.url
        items["name"] = infos
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info)

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_hunan_YiYang",
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
