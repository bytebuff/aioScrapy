# _*_ coding: utf-8 _*_

""" 调度器 """
import queue


class Scheduler(object):
    """
        调度器的实现 主要是请求的入队和出队 (去重暂时没有加上)
    """

    def __init__(self, spider):
        '''
        初始化队列
        :param spider: 爬虫对象
        '''
        # 存放请求的队列
        self.queue = queue.Queue()

    def __len__(self):
        '''
        队列的长度 (目前没有使用-->用的是下面的has_pending_requests方法)
        :return: 返回队列的长度
        '''
        # 返回队列的长度 
        return self.queue.qsize()

    def enqueue_request(self, request):
        '''
        将请求添加到队列
        :param request: start_requests中的请求 / 回调函数中的请求
        :return: True(可以不要返回值)
        '''
        print(f'请求添加进队列 --> {request}')
        self.queue.put(request)
        return True

    def next_request(self):
        '''
        取出下一个请求 取出请求
        :return: 返回从队列中取出的请求
        '''
        try:
            request = self.queue.get(block=False) # pop剔除一个元祖 并将这个元素赋值给requests
        except Exception as e: # 如果没有取出队列中的元素(队列是空的) 就默认request是None
            request = None
        return request # 返回请求

    def has_pending_requests(self):
        '''
        判断队列中是否有请求
        :return:
        '''
        # 如果有请求那么就返回True
        # 没有请求就返回False
        return self.queue.qsize() > 0