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

# 湖南湘西招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "xiangxi_zhongbiao.py"
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
            "http://ggzyjy.xxz.gov.cn/TenderProject/GetBidderList?page="
            "http://ggzyjy.xxz.gov.cn/TenderProject/GetBidderList?page="
        ]
        urls2=[
            "&records=15&name=&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&publishbegintime=&publishendtime=&IsShowOld=true",
            "&records=15&name=&category=%E5%8C%BB%E7%96%97%E5%99%A8%E6%A2%B0%E9%87%87%E8%B4%AD&publishbegintime=&publishendtime=&IsShowOld=true"
        ]
        pages = [74, 7]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num) + urls2[i]
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://fz.fjzfcg.gov.cn/n/fzzfcg/queryPageData.do?page=6&rows=20&sid=200100&zzxs=jzcg"
    # ]

    def parse(self, response):
        data = json.loads(response.body)
        data = data['json']
        ids = []
        tpids =[]
        names = []
        for i in data:
            ids.append(i['id'])
            tpids.append(i['TpId'])
            names.append(i['Title'])
        for i in range(len(names)):
            url = "http://ggzyjy.xxz.gov.cn/BidderPublic/GetInfosByTpId?tpId="+str(tpids[i])+"&_="+str(ids[i])
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
            "bid_hunan_XiangXi",
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
