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
# 广东汕尾招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "shanwei_zhaobiao.py"
    allowed_domains = ["www.swggzy.cn"]

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
            "http://www.swggzy.cn/newslist.aspx?Id=d3174a1009b141bcb4a99666527f53ed",
            "http://www.swggzy.cn/newslist.aspx?Id=4793892710e942bdb8edb883822dbab4"
        ]

        pages = [22, 16]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse, meta={'url': urls[i], 'page': pages[i]})

    def parse(self, response):
        cookies = response.headers['Set-Cookie']
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __EVENTVALIDATION = selector.xpath("//input[@id='__EVENTVALIDATION']/@value").extract()
        headers = {
            "Cookie": cookies,
            "Referer": url,
            "Host": "www.swggzy.cn"
        }
        while start <= page:
            yield FormRequest(url=url,
                              formdata={
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__EVENTVALIDATION': __EVENTVALIDATION[0],
                                  'ctl00$ContentPlaceHolder1$CP': str(start),
                                  '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$Goto_xxpage',
                                  '__EVENTARGUMENT': ''}, headers=headers,
                              callback=self.middle, meta={'page':str(start)})
            start += 1


    def middle(self, response):
        print "当前是第：" + response.meta['page'] + "页"
        selector = Selector(response)
        urls = selector.xpath("//div[@class='secondrightlistbox']/ul/li//a/@href").extract()

        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.swggzy.cn/" + "".join(urls[i])
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
                    "bid_guangdong_ShanWei",
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
