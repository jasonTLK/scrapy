# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.selector import Selector

try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from items.biding import biding_gov
from utils.toDB import *
# 山西临汾招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "linfen_zhaobiao.py"
    allowed_domains = ["www.lfggzyjy.gov.cn"]

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
            "http://www.lfggzyjy.gov.cn/page/index_",
            "http://www.lfggzyjy.gov.cn/page/index_"
        ]
        urls2=[
            ".jspx?type=notice&code=biddingNotice_dyproject",
            ".jspx?type=notice&code=biddingNotice_purchase"
        ]
        u3 =[
            "http://www.lfggzyjy.gov.cn/page/index.jspx?type=notice&code=biddingNotice_dyproject",
            "http://www.lfggzyjy.gov.cn/page/index.jspx?type=notice&code=biddingNotice_purchase"
        ]
        pages = [53, 108]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)+urls2[i]
                num+=1
                # print url
                yield Request(url=url,callback=self.parse,meta={'r': u3[i]})


    def parse(self, response):
        headers = {
            "Cookie": "JSESSIONID=536B60A59F35EBF2F09BFA5A76BF96A8; _gscu_59645108=89455863k27d7t15; _gscs_59645108=90083334i5p1q015|pv:4; _gscbrs_59645108=1; clientlanguage=zh_CN",
            'Referer':response.meta['r'],
            "Host": "www.lfggzyjy.gov.cn"
        }
        selector = Selector(response)
        names = selector.xpath("//div[@class='f-left']//a/@title").extract()
        urls = selector.xpath("//div[@class='f-left']//a/@href").extract()
        for i in range(len(names)):
            url = "http://www.lfggzyjy.gov.cn" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str},headers=headers)

    def parse2(self, response):
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = response.url
        items["name"] = "".join(infos).split(",")[0]
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info)

        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_shanxi_LinFen",
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

