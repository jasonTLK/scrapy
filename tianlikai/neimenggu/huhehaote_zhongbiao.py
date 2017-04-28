# -*- coding: utf-8 -*-
# 内蒙古呼和浩特招投标网站
# 中标信息
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
    name = "huhehaote_zhongbiao.py"
    allowed_domains = ["ggzyjy.com.cn"]

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
            "http://www.ggzyjy.com.cn/hsweb/004/004001/004001003/MoreInfo.aspx?CategoryNum=004001003",
            "http://www.ggzyjy.com.cn/hsweb/004/004002/004002003/MoreInfo.aspx?CategoryNum=004002003",
            "http://www.ggzyjy.com.cn/hsweb/004/004010/004010003/MoreInfo.aspx?CategoryNum=004010003",
            'http://www.ggzyjy.com.cn/hsweb/004/004011/004011003/MoreInfo.aspx?CategoryNum=004011003'
        ]
        pages=[223, 125, 6, 41]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse,meta={'url':urls[i],'page':pages[i]})


    def parse(self, response):
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        headers = {
            "Cookie": "ASP.NET_SessionId=m4vqja55tjlu0qzdxyiu1hm2; __CSRFCOOKIE=53e07222-5f96-49b4-8167-7e50102cdcdf; _gscu_987447560=88869101a6bg6m20; _gscs_987447560=89973636c4gf9g13|pv:33; _gscbrs_987447560=1",
            "Referer": url,
            "Host": "www.ggzyjy.com.cn"
        }
        while start<=page:
            start+=1
            yield FormRequest(url=url,
                              formdata={
                                  '__CSRFTOKEN': '/wEFJDUzZTA3MjIyLTVmOTYtNDliNC04MTY3LTdlNTAxMDJjZGNkZg==',
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__VIEWSTATEGENERATOR': 'C92A95CA',
                                  '__EVENTTARGET': 'MoreInfoList1$Pager',
                                '__EVENTARGUMENT': str(start)}, headers=headers,
                          callback=self.middle,meta={'page':str(start)})

    def middle(self,response):
        print "当前是第：" + response.meta['page'] + "页"

        selector = Selector(response)
        urls = selector.xpath("//td[@align='left']//a/@href").extract()
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.ggzyjy.com.cn" + "".join(urls[i])
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
                    "bid_neimenggu_HuHeHaoTe",
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
