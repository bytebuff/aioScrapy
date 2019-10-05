# _*_ coding: utf-8 _*_

""" 请求类 """
from w3lib.url import safe_url_string
from aioScrapy.utils.tools import to_bytes # 工具函数


class Request(object):
    """ 实现请求方法 """

    def __init__(self, url, method='GET', callback=None, 
                headers=None, encoding='utf-8', data=None, meta=None):
        '''
        初始化请求方法
        :param url: 请求的网址
        :param method: 请求的方法
        :param callback: 回调函数
        :param headers: 请求头
        :param encoding: 请求的编码方式
        :param data: 请求的数据POST请求
        :param meta: 请求的额外参数
        '''
        self.encoding = encoding  # 先设置请求编码信息
        self.url = self._set_url(url) # 判断网址/修正网址
        self.method = method.upper() # 请求方法大写
        self.callback = callback # 回调函数
        self.headers = headers or {} # 请求头 不指定就是空字典
        self.data = self._set_data(data) # 请求的数据POST请求
        self.meta = meta if meta else {} # 请求的额外参数 默认是空字典
        
    # 网址的设置
    def _set_url(self, url):
        '''
        网址的修正以及判断
        :param url: 请求网址
        :return: 修正后的网址
        '''
        # 如果不是字符类型肯定报错
        if not isinstance(url, str): # 如果不是字符串 就报错 提醒用户
            # raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)
            raise TypeError(f'请求的网址必须是字符串类型, 您指定的是: {type(url).__name__}')
        # 如果没有冒号 肯定不是完整的网址
        if ':' not in url:
            raise ValueError('网址协议不正确')
        # safe_url_string 返回一个安全的网址
        self.url = safe_url_string(url, self.encoding)
        # 返回安全的网址
        return self.url

    # 表单的设置 主要用于POST表单 
    def _set_data(self, data):
        '''
        表单数据的设置 主要用于POST表单 将数据转换成字节的形式
        :param data: POST的数据
        :return: 返回POST的表单数据(字节形式)
        '''
        # 如果POST的表单数据没有指定就是空值
        if data is None: # 设置为空
           self.data = b'' # 设置为空字节
        else:
            # 如果有数据 就将其转化成字节的形式 并赋予编码 默认utf-8
            self.data = to_bytes(data, self.encoding)
        # 返回字节数据
        return self.data

    def __str__(self):
        '''
        用于打印请求对象
        :return: 返回请求方法 请求的网址
        '''
        return "<%s %s>" % (self.method, self.url)
        # return f'<<{self.method} {self.url}>>'