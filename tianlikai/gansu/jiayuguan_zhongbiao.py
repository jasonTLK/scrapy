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

# 甘肃嘉峪关招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "jiayuguan_zhongbiao.py"
    # allowed_domains = ["120.55.150.93"]

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
            "http://120.55.150.93/InfoPage/InfoListInfo.aspx?SiteItem=28&page=",
            "http://120.55.150.93/InfoPage/InfoListInfo.aspx?SiteItem=35&page=",
        ]
        pages = [5, 4]
        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                url = urls[i] + str(num) + "&query="
                num += 1
                # print url
                yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://120.55.150.93/InfoPage/InfoListInfo.aspx?SiteItem=28&page=1&query="
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//div[@id='showInfos']//a/@href").extract()
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "".join(urls[i]).replace("../", "http://120.55.150.93/")
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str})

    def parse2(self, response):
        selector = Selector(response)
        url = selector.xpath("//iframe[@id='Iframe']/@src").extract()
        yield Request(url="".join(url[0]), callback=self.parse3, meta={"info": response.meta['info']})

    def parse3(self, response):
        page_info = "".join(response.body)
        fileName = "".join(response.meta["info"]).split(',')[0]
        hashName = hash("".join(response.meta['info']).split(',')[0])
        url = "".join(response.meta["info"]).split(',')[1]
        pdfUrl = response.url
        print fileName, hashName, url, pdfUrl
        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_gansu_JiaYuGuan",
            {
                "hashName": hashName,
                "fileName": fileName,
                "url": url,
                "pdfUrl": pdfUrl,
                "create_time": datetime.datetime.now(),
                "update_time": datetime.datetime.now()
            }
        )
        fileContent = page_info
        filePath = "/user/hadoop/bidding/GanSu/JiaYuGuan/"+str(fileName)+".pdf"
        client = ToHdfs(filePath, fileContent)
        client.toHdfs()
        print filePath
