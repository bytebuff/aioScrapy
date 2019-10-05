# _*_ coding: utf-8 _*_

''' 发送POST请求 '''
from .request import Request
from aioScrapy.utils.tools import url_encode, is_listlike # 工具函数


class FormRequest(Request):
    """ 实现POST请求 """

    def __init__(self, *args, **kwargs):
        formdata = kwargs.pop('data', None)
        if formdata and kwargs.get('method') is None:
            kwargs['method'] = 'POST'

        super(FormRequest, self).__init__(*args, **kwargs)

        if formdata:
            # 字典表单形式的-->查询字符串形式的 x-www-form-urlencoded
            query_str = url_encode(formdata.items(), self.encoding) if isinstance(formdata, dict) else formdata
            if self.method == 'POST':
                # 表单形式发送
                kwargs.setdefault(b'Content-Type', b'application/x-www-form-urlencoded')
                self._set_data(query_str) # 传递字符形式的 x-www-form-urlencoded
            else: # 如果不是POST请求 就默认是GET请求 那么久拼接查询字符串
                # 拼接网址
                self._set_url(self.url + ('&' if '?' in self.url else '?') + query_str)

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)