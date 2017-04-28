# -*- coding: utf-8 -*-
#  内蒙古锡林郭勒盟招投标网站
#  中标信息

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


class hz_gov_Spider(scrapy.Spider):
    name = "xilinguolemeng_zhongbiao.py"
    allowed_domains = ["xmzwggzy.com"]

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
        urls=[
            "http://www.xmzwggzy.com/xmweb/ggzyjy/009001/009001005/009001005004/MoreInfo.aspx?CategoryNum=009001005004",
        ]
        pages=[15]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse,meta={'url':urls[i],'page':pages[i]})


    def parse(self, response):
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        headers = {
            "Cookie": "ASP.NET_SessionId=xecaxf55xdk3yvajr3vnf4jg; ASP.NET_SessionId_NS_Sig=oenCV6md0WtzuQ_t; _gscu_723362525=89458437kxw4w071; _gscs_723362525=89988312lrxtf071|pv:14; _gscbrs_723362525=1",
            "Referer": url,
            "Host": "www.xmzwggzy.com"
        }
        while start<=page:
            start+=1
            yield FormRequest(url=url,
                              formdata={
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__EVENTTARGET': 'MoreInfoList1$Pager',
                                  '__EVENTARGUMENT': str(start),
                                  '__VIEWSTATEENCRYPTED':''}, headers=headers,
                          callback=self.middle,meta={'page':str(start)})



    def middle(self,response):
        print "当前是第：" + response.meta['page'] + "页"

        selector = Selector(response)
        urls = selector.xpath("//tr[@valign='top']//a/@href").extract()

        names=[]
        for i in range(len(urls)):
            names.append(selector.xpath("//a[@href='" + urls[i] + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.xmzwggzy.com" + "".join(urls[i])
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
                items["info"] = "".join(page_info).decode('gbk')

                db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
                db.get_insert(
                    "bid_neimenggu_XiLinGuoLeMeng",
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
