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
    name = "heilongjiang.py"

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
        headers = {
            # "Cookie": Cookie,
            "Host": "ha.gsxt.gov.cn",
        }
        # data = get_uuid()
        url = "http://hl.gsxt.gov.cn/business/JCXX.jspx?id=20538ACF3327511A34BCDFBBB8F55502&date=Fri%20Apr%2021%202017%2010:14:03%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)"
        # for i in range(len(data)):
        #     url = "http://ha.gsxt.gov.cn/business/JCXX.jspx?id="+''.join(data[i])+"&date=Wed%20Apr%2019%202017%2010:09:35%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&ad_check=1"

        # r = requests.get(url, headers=headers, **{"allow_redirects": False})
        # if r.status_code == 302:
        #     print "".join(r.headers['Set-Cookie']).split(';')[0]
        #     header = c + "".join(r.headers['Set-Cookie']).split(';')[0]
        #     # print header
        #     h = {
        #         "Cookie": header,
        #         "Host": "ha.gsxt.gov.cn",
        #     }

        yield Request(url=url, callback=self.parse, headers=headers, meta={'url': url})


    def parse(self, response):
        obj2={}
        selector = Selector(response)
        all = selector.xpath("//div[@class='baseinfo']").extract()
        for i in range(1,len(all)):
            p = selector.xpath("//div[@class='baseinfo']["+str(i+1)+"]//p[@class='text mainPerText']/span/text()").extract()
            p = ''.join(p).strip().replace("&nbsp",'').replace(' ','')

            type1 = selector.xpath("//div[@class='baseinfo']["+str(i+1)+"]//div[@class='noData2']/div/text()").extract()
            type2 = selector.xpath("//div[@class='baseinfo']["+str(i+1)+"]//div[@class='ax_table liebiaoxinxin']//td").extract()
            # print len(type2)
            type3 = []
            for j in range(len(type2)):
                type3.append(''.join(type2[j]).split('>')[1].split('<')[0])

            if(type1):
                if len(type1) == 1:
                    toObj(obj2, u''.join(p).strip(), u''.join(type1).strip())
                else:
                    print '123' + ''.join(p).strip() + str(i+1)
            if(type2):
                s = ''
                if len(type3) == 1:
                    s = ''.join(type3).strip()
                    toObj(obj2, u''.join(p).strip(), s)
                else:
                    th = selector.xpath("//div[@class='baseinfo'][" + str(
                        i + 1) + "]//div[@class='ax_table liebiaoxinxin']//th/text()").extract()
                    l = len(th)
                    if u''.join(p).strip()  == u'企业年报信息':
                            a = selector.xpath("//div[@class='baseinfo'][" + str(
                        i + 1) + "]//div[@class='ax_table liebiaoxinxin']//a/@href").extract()
                            if len(a) > 0:
                                arr = []
                                for k in a:
                                    arr.append("http://ha.gsxt.gov.cn"+''.join(k))
                                toObj(obj2, u'年度报表数组', arr)

                    for i in range(len(type3)):
                        if (i+1) % l == 0:
                            s += ''.join(type3[i]).strip()+"---"
                        else:
                            s += ''.join(type3[i]).strip()+'+++'
                        toObj(obj2, u''.join(p).strip(), s)


        info1 = selector.xpath("//div[@id='zhizhao']//td/text()").extract()
        info1_span = selector.xpath("//div[@id='zhizhao']//td//span").extract()
        info = []
        for i in range(len(info1_span)):
            info.append(''.join(info1_span[i]).split(">")[1].split("<")[0])

        info1_td = []

        for i in info1:
            if len(''.join(i).strip().replace(' ', '')) > 0:
                info1_td.append(''.join(i).strip().replace(' ', ''));

        jingyingfanwei = selector.xpath("//div[@id='zhizhao']//td//div[@class='jingyingfanwei']/text()").extract()
        jingyingfanwei_info = selector.xpath(
                "//div[@id='zhizhao']//td//div[@class='jingyingfanwei']/span/text()").extract()
        for i in range(len(jingyingfanwei)):
            info1_td.append(jingyingfanwei[i])
            info1_span.append(jingyingfanwei_info[i])

        obj1={}
        print len(info1_td), len(info)

        for i in range(len(info1_td)):
            toObj(obj1, u"".join(info1_td[i]).strip().replace(u"· ", "").replace(u' ：', ''), "".join(info[i]).strip())


        toObj(obj2,u'营业执照信息',obj1)
        toObj(obj2,'url',response.meta['url'])
        for i in obj2:
            print ''.join(i)

        sql = {}
        for i in obj2:
            sql[i] = obj2[i]
        db = insertMongo()
        db.insertHeiLongJiang(sql)
        print "插入成功"





































