# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.selector import Selector
import requests
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
from utils.toDB import *

class hz_gov_Spider(scrapy.Spider):
    name = "test.py"

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
        # Cookie = "UM_distinctid=15b7eb379f2c52-06bd4237f0b52-5e4f2b18-13c680-15b7eb379f39e8; test=20111112; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1492479343,1492480443; " \
        #          "Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1492480443; JSESSIONID=0000YelYd194TGY_T1PglaPDE_P:-1; AD_VALUE=cbc4b94f"
        # headers = {
        #     "Cookie": Cookie,
        #     "Referer":'http://ha.gsxt.gov.cn/company/detail.jspx?id=49D6B19AEC11DF1AE053070A080A76B2&jyzk=jyzc&ad_check=1',
        #     "Host": "ha.gsxt.gov.cn"
        # }


        session = requests.session()
        s = session.get("http://ha.gsxt.gov.cn/business/JCXX.jspx?id=49D6B1689198DF1AE053070A080A76B2&date=Wed%20Apr%2019%202017%2014:41:31%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4&ad_check=1))")
        print ''.join(s.content)


        # urls = [
        #     "http://ha.gsxt.gov.cn/business/JCXX.jspx?id=49D6B12F810CDF1AE053070A080A76B2&date=Wed%20Apr%2019%202017%2010:09:35%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&ad_check=1"
        #
        # ]
        # pages = [1]
        # for i in range(len(urls)):
        #     num=1
        #     while num<=pages[i]:
        #         url =urls[i]
        #         num+=1
        #         # print url
        #         yield Request(url=url, callback=self.parse)

    # def parse(self, response):
    #    print response.body

















