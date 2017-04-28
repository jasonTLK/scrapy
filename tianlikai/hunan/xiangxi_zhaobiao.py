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
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "xiangxi_zhaobiao.py"
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
            "http://ggzyjy.xxz.gov.cn/TenderProject/GetTpList?page=",
            "http://ggzyjy.xxz.gov.cn/TenderProject/GetTpList?page=",
        ]
        # url = u"http://ggzyjy.xxz.gov.cn/%E6%96%B0%E6%B5%81%E7%A8%8B/%E6%8B%9B%E6%8A%95%E6%A0%87%E4%BF%A1%E6%81%AF/jyxx_x.aspx?iq=cg&type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&tpid=" + \
        #       ids[i] + u"#title_招标公告"

        urls2=[
            "&records=15&name=&category=政府采购&publishbegintime=&publishendtime=&IsShowOld=true",
            "&records=15&name=&category=医疗器械采购&publishbegintime=&publishendtime=&method=&IsShowOld=true",
        ]
        pages = [48, 6]
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


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
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
