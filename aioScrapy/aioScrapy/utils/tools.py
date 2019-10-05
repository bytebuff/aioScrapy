# _*_ coding: utf-8 _*_

""" 公共工具 """

from urllib.parse import urlencode


# 在引擎中使用
def result2list(result):
    '''
    处理回调函数返回的结果
    :param result: 传递的是回调函数返回的结果 也就是回调函数的返回值
    :return: 空列表, 返回响应的列表, 直接返回结果
    '''
    # 如果回调函数的返回值是None 或者没有返回值 就返回空列表
    if result is None:
        return []
    # 如果回调函数的返回值是字典 或者是字符串对象 就将其放置在列表中去 (这个返回的代表是数据)
    if isinstance(result, (dict, str)):
        return [result] # 返回的数据
    # 如果回调函数返回的是可迭代对象 那么就代表是返回的是新的请求 那么直接返回这个请求
    if hasattr(result, "__iter__"):
        return result # 返回请求

# 工具函数 用在 FormRequest 里面
def url_encode(seq, enc):
    values = [(to_bytes(k, enc), to_bytes(v, enc)) for k, vs in seq for v in (vs if is_listlike(vs) else [vs])]
    return urlencode(values, doseq=1)

# 工具函数 用在 FormRequest 里面
def is_listlike(x):
    """
    >>> is_listlike("foo")
    False
    >>> is_listlike(5)
    False
    >>> is_listlike(b"foo")
    False
    >>> is_listlike([b"foo"])
    True
    >>> is_listlike((b"foo",))
    True
    >>> is_listlike({})
    True
    >>> is_listlike(set())
    True
    >>> is_listlike((x for x in range(3)))
    True
    >>> is_listlike(six.moves.xrange(5))
    True
    """
    return hasattr(x, "__iter__") and not isinstance(x, (str, bytes))

# 工具函数 用在 request 里面 对参数data表单数据进行编码
def to_bytes(data, encoding=None, errors='strict'):
    """
    返回“text”的二进制表示形式。如果“文本”已经是bytes对象，按原样返回。
    :param data: 传递的post数据
    :param encoding: 编码格式
    :param errors: encode函数的一个参数 设置不同错误的处理方案。默认为 'strict',意为编码错误引起一个UnicodeError。
    :return: 返回字节形式的数据(经过了编码)
    """
    if isinstance(data, bytes):
        return data
    # 如果数据不是字符串形式的就报错
    if not isinstance(data, str):
        raise TypeError(f'to_bytes 必须接受参数类型是: unicode, str 或者 bytes, 传递的是{type(data).__name__}')
    if encoding is None:
        encoding = 'utf-8' # 默认是utf-8
    # 转化编码格式默认utf-8
    # errors --> 设置不同错误的处理方案。默认为 'strict',意为编码错误引起一个UnicodeError。
    return data.encode(encoding, errors)