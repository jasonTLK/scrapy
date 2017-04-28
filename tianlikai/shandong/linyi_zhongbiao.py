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
# 山东临沂招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "linyi_zhongbiao.py"
    allowed_domains = ["ggzyjy.linyi.gov.cn"]

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
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019001/019001015/019001015015/019001015015001/MoreInfo.aspx?CategoryNum=019001015015001",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019001/019001015/019001015016/MoreInfo.aspx?CategoryNum=019001015016",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019001/019001015/019001015017/MoreInfo.aspx?CategoryNum=019001015017",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019001/019001015/019001015018/MoreInfo.aspx?CategoryNum=019001015018",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019001/019001015/019001015019/MoreInfo.aspx?CategoryNum=019001015019",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019002/019002005/019002005005/019002005005001/MoreInfo.aspx?CategoryNum=019002005005001",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019002/019002005/019002005004/019002005004001/MoreInfo.aspx?CategoryNum=019002005004001",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019002/019002005/019002005007/019002005007001/MoreInfo.aspx?CategoryNum=019002005007001",
            "http://ggzyjy.linyi.gov.cn/lyztb/jyxx/019002/019002005/019002005008/019002005008001/MoreInfo.aspx?CategoryNum=019002005008001"
        ]

        pages = [59, 10, 6, 13, 5, 111, 40, 65, 22]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse, meta={'url': urls[i], 'page': pages[i]})

    def parse(self, response):
        cookies = response.headers['Set-Cookie']
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __VIEWSTATEGENERATOR = selector.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").extract()
        headers = {
            "Cookie": cookies,
            "Referer": url,
            "Host": "ggzyjy.linyi.gov.cn"
        }
        while start <= page:
            yield FormRequest(url=url,
                              formdata={
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR[0],
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
            url = "http://ggzyjy.linyi.gov.cn" + "".join(urls[i])
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
                    "bid_shandong_LinYi",
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
