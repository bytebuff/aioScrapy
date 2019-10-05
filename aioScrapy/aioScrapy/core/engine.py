# _*_ coding: utf-8 _*_

""" Engine """

import asyncio # Python 3.6 
from datetime import datetime
import logging

from aioScrapy.core.scheduler import Scheduler # 调度器
from aioScrapy.core.downloader.downloader import Downloader # 下载器
from aioScrapy.utils.tools import result2list # 工具函数
from aioScrapy.https.request import Request # 请求对象


class Engine(object):
    '''
        引擎：用于处理爬虫文件，调度器，下载器，启动等事件
    '''
    def __init__(self, spider):
        '''
        初始化 爬虫 调度器 下载器 配置文件 事件循环
        :爬虫 --> 从爬虫文件传递过来
        :调度器 --> 导入
        :下载器 --> 导入
        :配置文件(在爬虫文件中定义) --> 爬虫文件中定义的类属性
        :事件循环 --> asyncio模块
        :param spider: 爬虫对象
        '''
        '''
            初始化
                :爬虫 --> 从爬虫文件传递过来
                :调度器 --> 导入
                :下载器 --> 导入
                :配置文件(在爬虫文件中定义) --> 爬虫文件中定义的类属性
                :事件循环 --> asyncio模块
        '''
        self.spider = spider # 爬虫 实例
        self.scheduler = Scheduler(spider) # 调度器
        self.downloader = Downloader(spider) # 下载器
        self.settings = spider.settings # 配置文件
        self.loop = asyncio.get_event_loop() # 开始事件循环 一般一个程序只需要一个事件循环对象

    # 启动引擎的方法
    def start(self):
        # 转化为可迭代的 self.spider.start_requests() 方法返回可迭代的Request()
        # iter将其转化为可迭代对象 --> 将其一个个放到队列中
        start_requests = iter(self.spider.start_requests())
        # 把start_requests的所有请求全部传到execute里面用来启动初始化的网址(start_urls)
        self.execute(self.spider, start_requests) # 执行

    def execute(self, spider, start_requests):
        '''
        执行初始化start_urls里面的请求
        :param spider: 爬虫对象
        :param start_requests: start_requests里面返回的多个请求
        :return: None
        '''
        # 打印开始采集 self.spider.name --> 爬虫名字
        print(f'{">"*25} {self.spider.name}: 开始采集 {"<"*25}' )
        # 初始化 start_requests 中的多个请求 将请求放入队列中
        # _init_start_requests 中的crawl方法就是将请求加入到调度器定义的队列中
        self._init_start_requests(start_requests)
        # 爬虫开始的时间
        start_time = datetime.now()
        try:
            # 将协程注册到事件循环中
            self.loop.run_until_complete(self._next_request(spider))
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
            print(f'{">" * 25} {self.spider.name}: 爬虫结束 {"<" * 25}')
            print(f'{">" * 25} 总共用时: {datetime.now() - start_time} {"<" * 25}')

    def _init_start_requests(self, start_requests):
        for req in start_requests:
            self.crawl(req) # 传入每个网址

    async def _next_request(self, spider):
        '''
        协程方法 该方法用于不断的获取下一个请求(从调度器中的队列中)
        :param spider: 爬虫对象
        :return: None
        '''
        # self.settings 是在初始化的时候从爬虫文件中的settings传递过来的
        task_limit = self.settings.get("TASK_LIMIT", 5)   # 同时允许任务数量 配置文件中是5
        # 请求并发量的设置 value默认是1
        semaphore = asyncio.Semaphore(value=task_limit)
        # 死循环 不断的循环 从调度器中的队列不断获取请求
        while True:
            # 从调度器队列中获取一个请求 next_request() 在调度器中定义的
            request = self.scheduler.next_request()
            # if not isinstance(request, Request): # 如果取出来的不是请求 就进入等待
            if not request: # 如果取出来的不是请求 就进入等待
                logging.warning("time.sleep(3)")
                # 暂停三秒 协程的方式 暂停过后判断调度器的队列中是否还有请求
                await self.heart_beat() # 心跳函数 暂停3秒
                # has_pending_requests() 用来判断队列的大小是否大于0 如果大于0代表有请求在队列中
                # 如果队列中还是没有数据 那么久跳出整个循环 --> 爬虫终止 (这种判断爬虫终止的方法可以改进) --> 判断调度器，判断下载器等
                if not self.scheduler.has_pending_requests(): # 判断 再次判断目前队列的长度
                    break # 如果3秒过后队列中还是没有数据 那么就退出 这种做法有点生硬 应该同时判断下载器 爬虫文件等是否完成更好
                continue
            # 上锁 保证前面设置的并发量生效 每次上锁value值会减一 (-1)
            # 但是value值是不能低于0的 value等于0就会造成阻塞 --> 从而可以实现并发的控制
            await semaphore.acquire()
            # 创建任务 用于注册到事件循环中
            # 将每个从调度器中取出的请求都创建任务 --> 每次while循环创建一个任务(不断的创建任务)
            # _process_request 处理每个请求 request(从队列中取出的) --> 将请求交到下载器中去处理
            self.loop.create_task(self._process_request(request, spider, semaphore))

    @staticmethod
    async def heart_beat():
        '''
        实现的心跳函数 不断的检查调度器中是否有数据 
        :return: None
        '''
        await asyncio.sleep(3)

    # 封装下载器
    async def _process_request(self, request, spider, semaphore):
        '''
        协程方法 该方法每个从调度器中取出的请求交给下载器中处理
        :param request: 从调度器中的队列取出的请求 在_next_request方法中取出来的
        :param spider: 爬虫对象
        :param semaphore: 限制并发量 release() 释放
        :return: None
        '''
        try:
            # 调用下载器中的下载请求
            # self.download() 方法在引擎中再度封装 主要封装下载器中的下载请求的方法 fetch() 方法
            response = await self.download(request, spider)
        except Exception as exc: # 有异常执行except 但是不执行下面的else了
            # 如果报错 出现下载错误提示 捕获exc错误
            print(f'下载错误: {exc}')
        else: # 没有异常的时候正常执行else
            # 处理响应 传递response(响应) request(请求) spider(爬虫对象)
            self._handle_downloader_output(response, request, spider)
        # 释放锁资源 释放的时候 value的值会增加一 (+1)
        semaphore.release()

    # 封装下载器中的请求响应的方法
    async def download(self, request, spider):
        '''
        协程方法 该方法用于封装下载器中的请求响应的方法 fetch()
        :param request: 从调度器中的队列中取出的请求
        :param spider: 爬虫对象
        :return: 响应 --> response
        '''
        # self.downloader 在 __init__中封装了 fetch()方法在下载器中定义的 用来下载器请求对应的响应
        response = await self.downloader.fetch(request)
        # 把请求对象赋值到请求对象中 方便在response中读取对应的请求的数据
        response.request = request
        return response

    def _handle_downloader_output(self, response, request, spider):
        '''
        该方法用来处理下载器得到的响应的
        :param response: 下载器的响应
        :param request: 调度器的请求
        :param spider: 爬虫对象
        :return: None
        '''
        # 如果响应是请求类型就加入队列中去
        # if isinstance(response, Request):
        #     self.crawl(response)
        #     return
        # 如果不是请求 就是数据 处理下载后的数据  对于多个返回值
        self.process_response(response, request, spider)

    # 处理从下载器返回来的响应
    def process_response(self, response, request, spider):
        '''
        处理响应
        :param response: 下载器返回的响应
        :param request: 调度器中响应
        :param spider: 爬虫对象
        :return: None
        '''
        # 请求中是否有回调函数 如果没有就默认是parse函数作为回调
        callback = request.callback or spider.parse # 调用回调函数 没有指定就调用默认回调函数
        # 回调函数来处理响应 第一个参数就是response响应 回调函数是有返回值的 返回值就是result的值
        # 回调函数的返回值可能有多个结果 所以需要判断一下 到底是什么结果
        result = callback(response)
        # result2list() --> 用来判断回调函数返回的是数据，请求，还是None值
        ret = result2list(result)
        # 将回调函数返回的结果进行处理 --> handle_spider_output()
        self.handle_spider_output(ret, spider)

    def handle_spider_output(self, result, spider):
        '''
        集中处理回调函数返回的数据
        :param result: 回调函数返回是数据是什么 来自-->result2list()
        :param spider: 爬虫对象
        :return: None
        '''
        # 因为result2list中返回的要么是 列表(两种情况) 要么是可迭代的请求对象
        for item in result: # 回调函数返回的结果
            if item is None: # 代表回调函数返回None 或者没有返回值
                continue # 继续循环
            # 如果返回的是请求对象 那么就把请求加入到队列中去 crawl方法来实现
            elif isinstance(item, Request):
                self.crawl(item)
            # 如果结果是字典类型的 那么就交给管道函数来处理
            elif isinstance(item, dict): # 如果是字典就代表是数据 交给管道函数(文件)处理
                # 管道函数来处理 item数据
                self.process_item(item, spider)
            # 如果不是上面的数据类型 就报错
            else:
                print("爬虫文件中的回调函数必须返回请求, 数据, None值")

    def process_item(self, item, spider):
        '''
        封装爬虫中的管道函数 管道函数 用来保存数据 处理数据
        :param item: 爬虫采集的数据
        :param spider: 爬虫对象
        :return: None
        '''
        # 爬虫中的管道函数 用来处理数据
        spider.process_item(item) # 这个要求spider实例中有这个方法

    def crawl(self, request): # 将网址 请求加入队列
        '''
        将请求加到调度器中的队列中去
        :param request: 请求
        :return: True (enqueue_request会返回True)
        '''
        self.scheduler.enqueue_request(request)