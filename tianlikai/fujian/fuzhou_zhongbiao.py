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

# 福建福州招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "fuzhou_zhongbiao.py"
    allowed_domains = ["fz.fjzfcg.gov.cn"]

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
            "http://fz.fjzfcg.gov.cn/n/fzzfcg/queryPageData.do?page="
        ]
        pages = [112]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num) + "&rows=20&sid=200100&zzxs=jzcg"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://fz.fjzfcg.gov.cn/n/fzzfcg/queryPageData.do?page=6&rows=20&sid=200100&zzxs=jzcg"
    # ]

    def parse(self, response):
        headers = {
            "Host": "fz.fjzfcg.gov.cn"
        }
        data = json.loads(response.body)
        data = data['list']
        urls = []
        names = []
        for i in data:
            urls.append(i['noticeId'])
            names.append(i['title'])
        for i in range(len(names)):
            str = "".join(names[i]) + ',' + "http://fz.fjzfcg.gov.cn/n/fzzfcg/article.do?noticeId=" + "".join(urls[i])
            yield FormRequest(url="http://fz.fjzfcg.gov.cn/n/noticemgr/query-viewcontent.do",
                              formdata={"noticeId": urls[i]},
                              headers=headers,
                              callback=self.parse2, meta={"info": str})

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

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_fujian_FuZhou",
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
