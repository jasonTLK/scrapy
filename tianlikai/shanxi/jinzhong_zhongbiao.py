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
# 山西晋中招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "jinzhong_zhongbiao.py"
    allowed_domains = ["jzjjzx.com.cn"]

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
        page = 1
        url = "http://www.jzjjzx.com.cn/zbgs_list.aspx"
        while page <= 140:
            n = str(page)
            if page == 1:
                l = '140'
            else:
                l = str(page - 1)
            page += 1
            yield FormRequest(url=url,
                              formdata={
                                  '__EVENTTARGET': 'anp',
                                  '__EVENTARGUMENT': n,
                                  '__LASTFOCUS': '',
                                  '__VIEWSTATE': '/wEPDwUKMTk0NjU1NjQ0NQ9kFgICAQ9kFggCAQ8QZGQWAGQCAw8QZGQWAGQCBQ88KwAJAQAPFgQeCERhdGFLZXlzFgAeC18hSXRlbUNvdW50AhVkFioCAQ9kFgJmDxUFBDQ5NjI856WB5Y6/5bem5a625rup5rC05bqT5bel56iL5YuY5a+f6K6+6K6h5Lit5qCH5L6v6YCJ5Lq65YWs56S6D+elgeWOv+awtOWKoeWxgBEyMDE3LTItMjggMDowMDowMBAyMDE3LTMtMiAwOjAwOjAwZAICD2QWAmYPFQUENDk2MHPlr7/pmLPljr/olKHluoTjgIHnn7Ppl6jjgIHpg5HlrrbluoTmsLTlupMyMDE25bm05bqm5Zu95pyJ5YWs55uK5oCn5rC05Yip5bel56iL57u05L+u5YW75oqk6aG555uu6K+E5qCH57uT5p6c5YWs56S6MOWvv+mYs+WOv+awtOW6k+e7tOS/ruWFu+aKpOW3peeoi+W7uuiuvumhueebrumDqBEyMDE3LTItMjcgMDowMDowMBAyMDE3LTMtMSAwOjAwOjAwZAIDD2QWAmYPFQUENDk1OFHmmYvkuK3luILnrKzkuIDkurrmsJHljLvpmaLov4Hlu7rpobnnm67msaHmsLTlpITnkIbnq5norr7lpIfph4fotK3lj4rlronoo4Xlt6XnqIsY6LWb6byO5bel56iL5pyJ6ZmQ5YWs5Y+4ETIwMTctMi0yNCAwOjAwOjAwETIwMTctMi0yOCAwOjAwOjAwZAIED2QWAmYPFQUENDk1NlHmmYvkuK3luILnrKzkuIDkurrmsJHljLvpmaLov4Hlu7rpobnnm67msaHmsLTlpITnkIbnq5norr7lpIfph4fotK3lj4rlronoo4Xlt6XnqIsb5Y+X6LWb6byO5bel56iL5pyJ6ZmQ5YWs5Y+4ETIwMTctMi0yNCAwOjAwOjAwETIwMTctMi0yOCAwOjAwOjAwZAIFD2QWAmYPFQUENDk1NGPlt6bmnYPljr/lr5LnjovkuaHmkqTlubblu7rliLbmnZHpgJrnoazljJblt6XnqIvnp4vmoJHmuK/oh7PkuIvlh7nlt6XnqIvmlr3lt6XkuK3moIflgJnpgInkurrlhaznpLoe5bem5p2D5Y6/5a+S546L5Lmh5Lq65rCR5pS/5bqcETIwMTctMi0yMyAwOjAwOjAwETIwMTctMi0yNyAwOjAwOjAwZAIGD2QWAmYPFQUENDk1MlTlt6bmnYPljr/lr5LnjovkuaHlubPnjovoh7Plr5Lnjovljr/kuaHlhazot6/mlLnpgKDlt6XnqIvmlr3lt6XkuK3moIflgJnpgInkurrlhaznpLoe5bem5p2D5Y6/5a+S546L5Lmh5Lq65rCR5pS/5bqcETIwMTctMi0yMyAwOjAwOjAwETIwMTctMi0yNyAwOjAwOjAwZAIHD2QWAmYPFQUENDk1MFrmpobmrKHljLrnlLDlrrbmub7msLTlupPpmaTpmanliqDlm7rmuqLmtKrpgZPnu63lu7rlt6XnqIvmlr3lt6Xnm5HnkIbkuK3moIfkvq/pgInkurrlhaznpLoz5qaG5qyh5Yy65Zu65bel55Sw5a625rm+5rC05bqT6Zmk6Zmp5Yqg56iL6aG555uu6YOoETIwMTctMi0yMiAwOjAwOjAwETIwMTctMi0yNCAwOjAwOjAwZAIID2QWAmYPFQUENDk0OFPmpobmrKHljLrnlLDlrrbmub7msLTlupPpmaTpmanliqDlm7rmuqLmtKrpgZPnu63lu7rlt6XnqIswMeagh+S4reagh+S+r+mAieS6uuWFrOekujPmpobmrKHljLrnlLDlrrbmub7msLTlupPpmaTpmanliqDlm7rlt6XnqIvpobnnm67pg6gRMjAxNy0yLTIyIDA6MDA6MDARMjAxNy0yLTI0IDA6MDA6MDBkAgkPZBYCZg8VBQQ0OTQ2SOaYlOmYs+WOv+S5kOS4nOi3r+S6uuihjOWkqeahpeW3peeoi+mhueebruaWveW3peaLm+agh+ivhOagh+e7k+aenOWFrOekui3mmJTpmLPljr/kvY/miL/kv53pmpzlkozln47kuaHlu7rorr7nrqHnkIblsYARMjAxNy0yLTE1IDA6MDA6MDARMjAxNy0yLTE3IDA6MDA6MDBkAgoPZBYCZg8VBQQ0OTQ0deamhuekvuWOv+WNl+WMl+WQkemYs+adkeajmuaIt+WMuuaUuemAoOmhueebru+8iOWNl+WMl+WQkemYs+enu+awkei/geW7uuS4ieacn+W3peeoi++8ieaWveW3peW3peeoi+ivhOagh+e7k+aenOWFrOekuh7mpobnpL7ljr/n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',
                                  '__VIEWSTATEGENERATOR': '7F671CFF',
                                  '__EVENTVALIDATION': '/wEWFQLilsf8CAK42KTxBQLA1JLMBgK3gKXNBwKZ9Z2ICwKfodW0BQLUp43WAwKN562qCQKDmp2GBQL+0Z2GBQL2vMHrAgLort2DCALIxrH+CALS+sLbBgKk0ZaYBwKwg8W0BQLAzYGmCQLl0sXEBwK716HBDwL4tsXEBwLM+sbbBnbbV5+yamQcic7iwR4xbOkWMNz7',
                                  'anp_input': l},
                              callback=self.parse)

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//td[@class='pd2']//a/@href").extract()
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.jzjjzx.com.cn/" + "".join(urls[i])
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
                    "bid_shanxi_JinZhong",
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
