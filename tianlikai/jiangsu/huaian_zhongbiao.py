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
# 江苏淮安招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "huaian_zhongbiao.py"
    allowed_domains = ["haztb.gov.cn"]

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
            "http://www.haztb.gov.cn/hawz/jyxx/004001/004001002/MoreInfo.aspx?CategoryNum=004001002",
            "http://www.haztb.gov.cn/hawz/jyxx/004002/004002002/MoreInfo.aspx?CategoryNum=004002002",
            "http://www.haztb.gov.cn/hawz/jyxx/004004/004004002/MoreInfo.aspx?CategoryNum=004004002",
            "http://www.haztb.gov.cn/hawz/jyxx/004006/004006002/MoreInfo.aspx?CategoryNum=004006002"
        ]
        pages = [459, 114, 29, 43]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse, meta={'url': urls[i], 'page': pages[i]})

    def parse(self, response):
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __VIEWSTATEGENERATOR = selector.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").extract()
        headers = {
            "Cookie": "ASP.NET_SessionId=3kbb2z2brusoze45bi4mrhz2",
            "Referer": url,
            "Host": "www.haztb.gov.cn"
        }
        while start <= 2:
            yield FormRequest(url=url,
                              formdata={
                                  '__CSRFTOKEN': '',
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR[0],
                                  '__EVENTTARGET': 'MoreInfoList1$Pager',
                                  '__EVENTARGUMENT': str(start)}, headers=headers,
                              callback=self.middle,meta={'page':str(start)})
            start += 1


    def middle(self, response):
        print "当前是第：" + response.meta['page'] + "页"
        selector = Selector(response)
        u = selector.xpath("//td[@align='left']//a/@href").extract()
        urls = []
        for i in range(4,len(u)):
            urls.append(u[i])



        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.haztb.gov.cn" + "".join(urls[i])
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

                db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
                db.get_insert(
                    "bid_jiangsu_huaian",
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
