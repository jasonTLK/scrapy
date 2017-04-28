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
# 广东佛山招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "foshan_zhaobiao.py"
    allowed_domains = ["stggzy.gov.cn"]

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
            "http://www.fsggzy.cn/gcjy/gc_zbxx/gc_zbsz/index_",
            "http://www.fsggzy.cn/zfcg/zf_cggsgg/zf_ggsz/index_",
            "http://www.fsggzy.cn/yxcg/yx_yxcg/yx_ggsz/index_",
            "http://www.fsggzy.cn/qycg/cggg/jgggsz/index_"
        ]
        urls2 = [
            "http://www.fsggzy.cn/gcjy/gc_zbxx/gc_zbsz/index.html",
            "http://www.fsggzy.cn/zfcg/zf_cggsgg/zf_ggsz/index.html",
            "http://www.fsggzy.cn/yxcg/yx_yxcg/yx_ggsz/index.html",
            "http://www.fsggzy.cn/qycg/cggg/jgggsz/index.html"
        ]
        u = [
            "http://www.fsggzy.cn/gcjy/gc_zbxx/gc_zbsz/",
            "http://www.fsggzy.cn/zfcg/zf_cggsgg/zf_ggsz/",
            "http://www.fsggzy.cn/yxcg/yx_yxcg/yx_ggsz/",
            "http://www.fsggzy.cn/qycg/cggg/jgggsz/"
        ]
        pages=[50, 50, 26, 2]
        for i in range(len(urls)):
            page = 0
            while page <= pages[i]:
                if page == 1:
                    url = urls2[i]
                else:
                    url = urls[i] + str(page) + ".html"
                page += 1
                yield Request(url=url, callback=self.parse, meta={"info":u[i]})

    #
    # start_urls = [
    #     "http://www.stggzy.gov.cn/stggzy/jyxx/002001/002001003/?pageing=1"
    # ]

    def parse(self, response):
        u = response.meta['info']
        selector = Selector(response)
        names = selector.xpath("//div[@class='secondrightlistbox']/ul/li//a/@title").extract()
        urls = selector.xpath("//div[@class='secondrightlistbox']/ul/li//a/@href").extract()
        print len(names),len(urls)

        for i in range(len(names)):
            url = "".join(urls[i]).replace('./',"".join(u))
            str = "".join(names[i]).strip() + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str})
    #
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
            "bid_guangdong_FoShan",
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