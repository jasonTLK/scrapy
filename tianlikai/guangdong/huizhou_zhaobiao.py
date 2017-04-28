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
# 广东惠州招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "huizhou_zhaobiao.py"

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
            "http://zyjy.huizhou.gov.cn/pages/cms/hzggzyjyzx/html/artList.html?sn=hzggzyjyzx&cataId=49b0a00aec704a028cf4ad8678aceb7e&pageNo=",
            "http://zyjy.huizhou.gov.cn/pages/cms/hzggzyjyzx/html/artList.html?sn=hzggzyjyzx&cataId=d1906435886c4ee188887bc8297606ed&pageNo="
        ]
        pages = [54, 130]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://zyjy.huizhou.gov.cn/pages/cms/hzggzyjyzx/html/artList.html?sn=hzggzyjyzx&cataId=bb3cfceb67fd4457bd7527b9899058de&pageNo=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        u = selector.xpath("//li[@class='li_art_title']//a/@href").extract()
        urls =[]
        for i in range(20):
            urls.append(u[i])
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://zyjy.huizhou.gov.cn" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.middle, meta={"info": str})

    def middle(self,response):
        str = response.meta['info']
        selector = Selector(response)
        url = selector.xpath("//iframe/@src").extract()
        print url[0]
        yield Request(url=url[0], callback=self.parse2, meta={"info": str})

    def parse2(self, response):
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = response.url
        items["name"] = "".join(infos).split(",")[0]
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info).decode('gbk')

        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_guangdong_HuiZhou",
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