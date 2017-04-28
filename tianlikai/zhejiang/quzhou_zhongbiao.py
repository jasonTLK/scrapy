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
# 浙江衢州招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "quzhou_zhongbiao.py"
    allowed_domains = ["www.qzggzy.com"]

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
            "http://www.qzggzy.com/FrontWeb/ggshow.aspx?Type=jsgc&BigType=6&findtxt=",
            "http://www.qzggzy.com/FrontWeb/ggshow.aspx?Type=zfcg&BigType=6&findtxt=",
            "http://www.qzggzy.com/FrontWeb/ggshow.aspx?Type=qtjy&BigType=21&findtxt=",
            'http://www.qzggzy.com/FrontWeb/ggshow.aspx?Type=ssdq&BigType=6&findtxt='
        ]

        pages = [269, 40, 7, 113]
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
            "Host": "www.qzggzy.com"
        }
        while start <= page:
            yield FormRequest(url=url,
                              formdata={
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__VIEWSTATEENCRYPTED': '',
                                  '__EVENTVALIDATION': __EVENTVALIDATION[0],
                                  '__EVENTTARGET': '',
                                  'ctl17': str(start),
                                  'ctl18': 'Go',
                                  '__EVENTARGUMENT': ''}, headers=headers,
                              callback=self.middle, meta={'page':str(start)})
            start += 1


    def middle(self, response):
        print "当前是第：" + response.meta['page'] + "页"
        selector = Selector(response)
        urls = selector.xpath("//td[@align='left']//a/@href").extract()

        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.qzggzy.com/FrontWeb/" + "".join(urls[i])
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
                print items['info']
                db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
                db.get_insert(
                    "bid_zhejiang_HengZhou",
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
