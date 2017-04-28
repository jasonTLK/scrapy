# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.selector import Selector
import requests
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from utils.toDB import *
import json

class hz_gov_Spider(scrapy.Spider):
    name = "beijing.py"

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
        Cookie = "UM_distinctid=15b7eb379f2c52-06bd4237f0b52-5e4f2b18-13c680-15b7eb379f39e8; test=20111114; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1492479343,1492480443;" \
                 " Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1492480443; JSESSIONID=0000YelYd194TGY_T1PglaPDE_P:-1; AD_VALUE=cbc4b9b1"
        c = "UM_distinctid=15b7eb379f2c52-06bd4237f0b52-5e4f2b18-13c680-15b7eb379f39e8; test=20111114; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1492479343,1492480443;" \
            " Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1492480443; JSESSIONID=0000YelYd194TGY_T1PglaPDE_P:-1; "
        headers = {
            "Cookie": Cookie,
            "Host": "ha.gsxt.gov.cn",
        }
        # data = get_uuid()

        url = 'http://bj.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?entId=a1a1a1a025beeda80125d80eb1340bff&clear=true&urltag=1&credit_ticket=23611633A9DF1AEF1F7176B20D9AA4FE'
        # for i in range(len(data)):
        #     url = "http://ha.gsxt.gov.cn/business/JCXX.jspx?id="+''.join(data[i])+"&date=Wed%20Apr%2019%202017%2010:09:35%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&ad_check=1"
        #
        #     r = requests.get(url, headers=headers, **{"allow_redirects": False})
        #     try:
        #         print "".join(r.headers['Set-Cookie']).split(';')[0]
        #         header = c + "".join(r.headers['Set-Cookie']).split(';')[0]
        #         print header
        #         h = {
        #             "Cookie": header,
        #             "Host": "ha.gsxt.gov.cn",
        #         }
        #         yield Request(url=url, callback=self.parse, headers=h, meta={'url': url})
        #     except:
        yield Request(url=url, callback=self.parse, headers=headers, meta={'url': url})

    def parse(self, response):
        url = response.meta['url']
        entId = "".join(url).split("entId=")[1].split("&")[0]
        credit_ticket = "".join(url).split("credit_ticket=")[1]
        selector = Selector(response)
        iframe = selector.xpath("//iframe/@src").extract()

        h1 = selector.xpath("//h1[@class='public-title2 qy-title']//text()").extract()
        for i in h1:
            print ''.join(i)

        td = selector.xpath("//div[@class='qyqx-detail']/table/tbody//td").extract()
        key = []
        value = []
        for i in td:
            k = ''.join(i).split("<strong>")[1].split('<')[0].replace(u"：", "")
            v = ''.join(i).split("</strong>")[1].split('<')[0]
            key.append(k)
            value.append(v)

        obj = {}
        for i in range(len(key)):
            toObj(obj, key[i], value[i])
        sql = {}
        sql[''.join(h1)] = obj
        sql["entId"] = entId
        sql["credit_ticket"] = credit_ticket
        sql['url'] = response.url
        db = insertMongo()
        db.inserBeiJing(sql)
        for i in iframe:
            yield Request(url="http://bj.gsxt.gov.cn" + ''.join(i), callback=self.parse2, meta={"entId": entId})

    def parse2(self, response):
        entId = response.meta['entId']
        selector = Selector(response)
        h1 = selector.xpath("//h1[@class='public-title2 qy-title']/text()").extract()
        h1 = "".join(h1).strip()
        str = ""
        td = selector.xpath("//table//td").extract()
        if len(td) > 1:
            th = selector.xpath("//table//th/text()").extract()
            length = len(th)

            for i in range(len(td)):
                if (i+1) % length ==0:
                    str += "".join(td[i]).strip().split(">")[1].split("<")[0].strip() + "---"
                else:
                    str += "".join(td[i]).strip().split(">")[1].split("<")[0].strip() + "+++"
        else:
            str = "".join(td).split(">")[1].split("<")[0].strip()

        sql = {}
        sql[h1] = str
        db = insertMongo()
        db.Update_beijing({"entId": entId}, {"$set": sql})


