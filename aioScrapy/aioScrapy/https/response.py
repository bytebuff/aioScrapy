# _*_ coding: utf-8 _*_

""" 响应类 """

class Response(object):
    """响应对象"""

    def __init__(self, url, status=200, headers=None, text='', request=None):
        self.url = url
        self.status = status
        self.headers = headers or {}
        self.text = text
        self.request = request
        self._cached_selector = None

    @property
    def selector(self):
        from parsel import Selector
        if self._cached_selector is None:
            self._cached_selector = Selector(self.text)
        return self._cached_selector

    def xpath(self, query, **kwargs):
        return self.selector.xpath(query, **kwargs)

    def css(self, query):
        return self.selector.css(query)
