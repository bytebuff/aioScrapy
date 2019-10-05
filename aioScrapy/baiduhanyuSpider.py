'''
    采集百度汉语 aioScrapy
'''
from aioScrapy.https.request import Request
from aioScrapy.core.spider import Spider
import re
from urllib.parse import unquote


class BaiduSpider(Spider):

    settings = {
        'TASK_LIMIT': 5,  # 并发个数限制
    }

    # 从‘王’开始
    start_urls = ['https://hanyu.baidu.com/zici/s?wd=王&query=王']

    def parse(self, response):
        # 提取图片网址
        img_url = response.xpath('//img[@class="bishun"]/@data-gif').get()
        chinese_character = re.search('wd=(.*?)&', response.url).group(1)
        item = {
            'img_url': img_url,
            'response_url': response.url,
            'chinese_character': unquote(chinese_character)
        }
        yield item
        # 提取相关字 提取热搜字 进行迭代
        new_character = response.xpath('//a[@class="img-link"]/@href').getall()
        for character in new_character:
            # 拼接
            new_url = 'https://hanyu.baidu.com/zici' + character
            # 发送请求
            yield Request(new_url, callback=self.parse)

    def process_item(self, item):
        ''' 数据存储 '''
        print('管道文件-->', item)


if __name__ == '__main__':
    baiduspider = BaiduSpider()
    baiduspider.start()