# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
from scrapy.selector import Selector

try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from items.biding import biding_gov
from utils.toDB import *
# 江西萍乡招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "pingxiang_zhaobiao.py"
    allowed_domains = ["pxggzy.jiangxi.gov.cn"]

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
            "http://pxggzy.jiangxi.gov.cn/pxzbw/jyxx/002001/002001002/MoreInfo.aspx?CategoryNum=002001002",
            "http://pxggzy.jiangxi.gov.cn/pxzbw/jyxx/002003/002003001/MoreInfo.aspx?CategoryNum=002003001",
            "http://pxggzy.jiangxi.gov.cn/pxzbw/jyxx/002004/002004001/MoreInfo.aspx?CategoryNum=002004001"
        ]

        pages = [17, 3, 87, ]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse, meta={'url': urls[i], 'page': pages[i]})

    def parse(self, response):
        cookies = response.headers['Set-Cookie']
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __CSRFTOKEN = selector.xpath("//input[@id='__CSRFTOKEN']/@value").extract()
        headers = {
            "Cookie": cookies,
            "Referer": url,
            "Host": "pxggzy.jiangxi.gov.cn"
        }
        while start <= page:
            yield FormRequest(url=url,
                              formdata={
                                  '__CSRFTOKEN': __CSRFTOKEN[0],
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__EVENTTARGET': 'MoreInfoList1$Pager',
                                  '__EVENTARGUMENT': str(start)}, headers=headers,
                              callback=self.middle, meta={'page':str(start)})
            start += 1


    def middle(self, response):
        print "当前是第：" + response.meta['page'] + "页"
        selector = Selector(response)
        urls = selector.xpath("//tr[@valign='top']//a/@href").extract()

        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://pxggzy.jiangxi.gov.cn" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str})

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
                    "bid_jiangxi_PingXiang",
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
