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
# 宁夏中卫招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "zhongwei_zhongbiao.py"
    allowed_domains = ["zwsggzy.cn"]

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
            "http://www.zwsggzy.cn/morelink.aspx?type=17&index=0",
            "http://www.zwsggzy.cn/morelink.aspx?type=17&index=1"
        ]
        pages = [34, 34]
        item = [2,1]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse, meta={'url': urls[i], 'page': pages[i],'item':item[i]})

    def parse(self, response):
        cookies = response.headers['Set-Cookie']
        url = response.meta['url']
        item = response.meta['item']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __EVENTVALIDATION = selector.xpath("//input[@id='__EVENTVALIDATION']/@value").extract()
        __VIEWSTATEGENERATOR = selector.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").extract()
        headers = {
            "Cookie": cookies,
            "Referer": url,
            "Host": "www.zwsggzy.cn"
        }
        while start <= page:
            yield FormRequest(url=url,
                              formdata={
                                  '__EVENTTARGET': 'goto_page',
                                  '__EVENTARGUMENT': '',
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__EVENTVALIDATION': __EVENTVALIDATION[0],
                                  'goto_text': str(start),
                                  '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR[0],
                                  'HF_SFGG': '',
                                  'HF_T': '2',
                                  'HF_D': str(item)}, headers=headers,
                              callback=self.middle, meta={'page': str(start), 'headers': headers})
            start += 1


    def middle(self, response):
        print "当前是第：" + response.meta['page'] + "页"
        selector = Selector(response)
        urls = selector.xpath("//div[@class='lmright_c']/ul/li//a/@href").extract()

        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.zwsggzy.cn/" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            # print url
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

                db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
                db.get_insert(
                    "bid_ningxia_ZhongWei",
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
