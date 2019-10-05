# _*_ coding: utf-8 _*_

""" Base Spider"""
import logging

from aioScrapy.https.request import Request
from aioScrapy.core.engine import Engine


class Spider(object):
    ''' 爬虫文件  '''

    # 爬虫名字 默认aioscrapy
    name = 'aioscrapy'

    # 个性化配置文件 微框架就用这个作为配置项 不再另外创建一个配置文件了
    settings = {
        'headers': {}, # 请求头 dict
        'timeout': 10, # 延迟时间 int
        'proxy': '', # IP代理
        'proxy_file': "proxy_list.txt", # 代理保存的文件 一般代理的时效性都不高 【暂未实现】
        'proxy_interval': 1, # 每个代理的时间间隔 【暂未实现】
        'task_limit': 5, # 并发个数限制
    }

    def __init__(self):
        '''
            初始化start_urls属性 如果用户没有在爬虫文件中定义这个方法就默认等于空列表
        '''
        # 如果没有这个属性就置为空 self.start_urls属性
        if not hasattr(self, "start_urls"):
            self.start_urls = []

    def start_requests(self):
        '''
            * 发送self.start_urls里面的网址 
            * 没有self.start_urls的时候可以自定义该方法
        '''
        for url in self.start_urls:
            yield Request(url)

    def start(self):
        '''
            * 把爬虫传递到引擎中 用于初始化爬虫对象 
            * engine.start()来启动爬虫
        '''
        engine = Engine(self) # 传入爬虫对象
        # 该方法中封装了execute方法
        # execute方法封装了事件循环 用来实现爬虫的初始化的启动
        engine.start() # 启动爬虫

    def parse(self, response):
        '''
            解析下载器回来的响应数据 默认的解析回调方法
            返回有三种类型:
                * 请求Request
                * 数据dict/str
                * None值
        '''
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

    def process_item(self, item):
        '''
            管道函数：处理从爬虫文件过来的数据
            在引擎中被使用
        '''
        pass