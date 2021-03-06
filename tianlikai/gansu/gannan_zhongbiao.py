# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.selector import Selector

try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from utils.toDB import *
from items.biding import biding_gov

# 甘肃甘南招投标网站
# 中标信息


class hz_gov_Spider(scrapy.Spider):
    name = "gannan_zhongbiao.py"

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
            "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=23&page=",
            "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=26&page=",
            "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=28&page="
        ]
        pages = [47, 32, 2]

        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                url = urls[i] + str(num) + "&query="
                num += 1
                # print url
                yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     'http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=23&page=1&query='
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//div[@id='showInfos']//a/@href").extract()
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "".join(urls[i]).replace("../", "http://www.gnggzyjy.com/")
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str})

    def parse2(self, response):
        selector = Selector(response)
        url = selector.xpath("//iframe[@id='Iframe']/@src").extract()
        if len(url)>=1:
            yield Request(url="".join(url[0]), callback=self.parse3, meta={"info": response.meta['info']})
        else:
            infos = response.meta["info"]
            items = biding_gov()
            items["url"] = response.url
            items["name"] = "".join(infos).split(",")[0]
            items["info"] = ""
            items["create_time"] = datetime.datetime.now()
            items["update_time"] = datetime.datetime.now()

            page_info = "".join(response.body)
            items["info"] = "".join(page_info)

            db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
            db.get_insert(
                "bid_gansu_GanNan",
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

    def parse3(self, response):
        page_info = "".join(response.body)

        fileName = "".join(response.meta["info"]).split(',')[0]
        hashName = hash("".join(response.meta['info']).split(',')[0])
        url = "".join(response.meta["info"]).split(',')[1]
        pdfUrl = response.url
        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_gansu_GanNan",
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
        filePath = "/user/hadoop/bidding/GanSu/GanNan/" + str(hashName) + ".pdf"
        client = ToHdfs(filePath, fileContent)
        client.toHdfs()
        print filePath
        print fileName, hashName, url, pdfUrl

