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

# 陕西商洛招投标网站
# 中标信息和中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "shangluo_zhaobiaoANDzhongbiao.py"
    # allowed_domains = ["ak.gov.cn"]

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
        page =1

        while page <= 5:
            url = "http://www.slcgzx.com/list.jsp?a9530t=5&a9530p="+str(page)+"&a9530c=30&urltype=tree.TreeTempUrl&wbtreeid=1005"
            yield Request(url=url, callback=self.parse)
            page += 1

    # start_urls = [
    #     "http://www.ak.gov.cn/gov/publicinfo/category-5_1.html"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//a[@class='c9530']/@href").extract()
        for i in urls:
            print ''.join(i)
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())



        for i in range(len(names)):
            url = "http://www.slcgzx.com"+"".join(urls[i])
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


        if "".join(items["name"]).find(u"结果公告") >=0 :
            print "交易结果"
            db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
            db.get_insert(
                "bid_SX_ShangLuo",
                {
                    "url": items["url"],
                    "name": items["name"],
                    "info": items["info"],
                    "create_time": items["create_time"],
                    "update_time": items["update_time"]
                }
            )
        else:
            print "交易项目"
            db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
            db.get_insert(
                "bid_SX_ShangLuo",
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

  # start_urls = [
  #       "http://www.ylctc.com/viewlist.asp?var=zhongbren&pageNO=1"
  #   ]
  #
  #   def parse(self, response):
  #       selector = Selector(response)
  #       urls = selector.xpath("//table[@class='color3d']//a/@href").extract()
  #       for i in urls:
  #           print i
  #       names=[]
  #       for i in urls:
  #           names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())
  #
  #       for i in range(len(names)):
  #           url = "http://www.ylctc.com" + "".join(urls[i])
  #           str = "".join(names[i]) + "," + url
  #           print str
  #           yield Request(url=url, callback=self.parse2, meta={"info": str})
  #
  #   def parse2(self, response):
  #       infos = response.meta["info"]
  #       items = biding_gov()
  #       items["url"] = response.url
  #       items["name"] = "".join(infos).split(",")[0]
  #       items["info"] = ""
  #       items["create_time"] = datetime.datetime.now()
  #       items["update_time"] = datetime.datetime.now()
  #
  #       page_info = "".join(response.body)
  #       items["info"] = "".join(page_info)
  #
  #       Tomogo(
  #           items["url"],
  #           items["name"],
  #           items["info"],
  #           items["create_time"],
  #           items["update_time"]
  #       )
  #       print items["url"]
  #       print items["name"]