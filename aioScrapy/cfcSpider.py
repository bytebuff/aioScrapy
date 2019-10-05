# _*_ coding: utf-8 _*_

from base.https.form import FormRequest
from base.core.spider import Spider


class CFCSpider(Spider):
    """ 中国基金中心数据抓取 """

    settings = {
        "headers":{'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Accept': '*/*',
                    'Content-Length': '123',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'http://data.foundationcenter.org.cn/foundation.html',
                    'Origin': 'http://data.foundationcenter.org.cn',
                    'Host': 'data.foundationcenter.org.cn',
                    'Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Content-Type': 'application/x-www-form-urlencoded'
                    }
    }

    # 初始网址
    start_urls = [
        "http://blog.jobbole.com/all-posts/",
    ]

    # 最好是在配置文件中可以这么配置
    heardes = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': '*/*',
        'Content-Length': '123',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://data.foundationcenter.org.cn/foundation.html',
        'Origin': 'http://data.foundationcenter.org.cn',
        'Host': 'data.foundationcenter.org.cn',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }


    def parse(self, response):
        post_url = "http://data.foundationcenter.org.cn/NewFTI/GetFDOPagedFoundation.ashx"
        data = {
            "keyWord": "",
            "pageIndex": "1",
            "pageSize": "25",
            "type": "2",
            "sqlWhere": "",
            "sqlTop": "",
            "flag": "0",
            "financeField": "%u51C0%u8D44%u4EA7",
            "searchMode": "0",
            "biaoji": ""
        }
        yield FormRequest(url=post_url,
                          data=data,
                          # headers=self.heardes,
                          callback=self.parse_detail,
                          method='POST')

    def parse_detail(self, response):
        
        print(response.text[0:100])

    def process_item(self, item):
        pass

if __name__ == '__main__':
    cfc_spider = CFCSpider()
    cfc_spider.start()