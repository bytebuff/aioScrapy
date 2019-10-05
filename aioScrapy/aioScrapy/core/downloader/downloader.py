# _*_ coding: utf-8 _*_

# 下载器和中间件执行模块
import logging
import aiohttp
from urllib.parse import urlparse
import chardet

from aioScrapy.https.response import Response


class DownloadHandler(object):

    """ DownloadHandler """

    def __init__(self, spider):
        self.settings = spider.settings # 读取配置文件

    async def fetch(self, request):
        kwargs = {} # 用来存储aiohttp.get & aiohttp.post的参数
        try:
            # 请求头

            # 先提取用户指定的headers参数里面的请求头 优先级较高
            if request.headers:
                headers = request.headers
            # 再提取用户在配置文件指定的headers 优先级较低
            elif self.settings.get('headers', False):
                headers = self.settings.get('headers')
            else:
                headers = {}
            kwargs['headers'] = headers # 请求头

            # 时间延迟
            timeout = self.settings.get("timeout", 10)
            kwargs['timeout'] = timeout # 时间延迟

            # IP
            proxy = request.meta.get("proxy", False)
            if proxy:
                kwargs["proxy"] = proxy # IP代理  meta指定方式
                print(f"user proxy {proxy}")

            # 并发的控制 在这里会更好
            url = request.url   
            # 替换Cookie应该在ClientSession(cookies=cookies)里面替换 在get post里面也行的
            async with aiohttp.ClientSession() as session:
                if request.method == "POST":
                    print('post的数据', request.data)
                    response = await session.post(url, data=request.data, **kwargs)
                else:
                    response = await session.get(url, **kwargs)
                content = await response.read()
                return Response(str(response.url), 
                                response.status,
                                response.headers, 
                                content)
        except Exception as _e:
            logging.exception(_e)
        return Response(str(request.url), 404)


class Downloader(object):

    """ Downloader """

    ENCODING_MAP = {} # 用于编码的转换 可以放在下载器中间件

    def __init__(self, spider):
        self.hanlder = DownloadHandler(spider)

    async def fetch(self, request):
        """
        request, Request, 请求
        """
        response = await self.hanlder.fetch(request)
        # 返回预处理 下载器中间件
        response = await self.process_response(request, response)
        return response

    # 编码处理 必须要有这一步 这一步也可以在下载器中实现
    async def process_response(self, request, response):
        # urlparse()把url拆分为6个部分，scheme(协议)，netloc(域名)，path(路径)，params(可选参数)，query(连接键值对)，fragment(特殊锚)，并且以元组形式返回。
        netloc = urlparse(request.url).netloc # netloc(域名)
        content = response.text # 响应内容
        if self.ENCODING_MAP.get(netloc) is None:
            # 自动识别编码
            encoding = chardet.detect(content)["encoding"]
            # GB 18030 与 GB 2312-1980 和 GBK 兼容 比后两者收录的字更多
            encoding = "GB18030" if encoding.upper() in ("GBK", "GB2312") else encoding
            self.ENCODING_MAP[netloc] = encoding
        text = content.decode(self.ENCODING_MAP[netloc], "replace")
        return  Response(url=str(response.url),
                         status=response.status,
                         headers=response.headers,
                         text=text)