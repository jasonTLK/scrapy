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


# 甘肃金昌招投标网站
# 中标信息
class hz_gov_Spider(scrapy.Spider):
    name = "jinchang_zhongbiao.py"
    # allowed_domains = ["jcggzy.com"]

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
            "http://www.jcggzy.com/Handlers/InfoPage.ashx?pageIndex=",
            "http://www.jcggzy.com/InfoPage/InfoList.aspx?pageIndex=",
            "http://www.jcggzy.com/Handlers/InfoPage.ashx?pageIndex=",
            "http://www.jcggzy.com/Handlers/InfoPage.ashx?pageIndex="
        ]
        urls2 = [
            "&pageSizes=25&siteItem=73&infoType=6&query=",
            "&pageSizes=25&SiteItem=80&InfoType=6&query=",
            "&pageSizes=25&siteItem=92&infoType=6&query=",
            "&pageSizes=25&siteItem=89&infoType=6&query="
        ]
        pages = [13, 1, 4, 15]
        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                url = urls[i] + str(num) + urls2[i]
                num += 1
                print url
                yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://www.zyggzy.com/Handlers/InfoPageTrade.ashx?pageIndex=1&pageSize=30&siteItem=46&infoType=&query="
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//li[@class='title']//a/@href").extract()
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.jcggzy.com" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str})

    def parse2(self, response):
        selector = Selector(response)
        url = selector.xpath("//iframe[@id='Iframe']/@src").extract()
        print "".join(url[0])
        yield Request(url="".join(url[0]), callback=self.parse3, meta={"info": response.meta['info']})

    def parse3(self, response):
        page_info = "".join(response.body)

        fileName = "".join(response.meta["info"]).split(',')[0]
        hashName = hash("".join(response.meta['info']).split(',')[0])
        url = "".join(response.meta["info"]).split(',')[1]
        pdfUrl = response.url
        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_gansu_JinCang",
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
        filePath = "/user/hadoop/bidding/GanSu/JinChang/"+str(hashName)+".pdf"
        client = ToHdfs(filePath, fileContent)
        client.toHdfs()
        print filePath

