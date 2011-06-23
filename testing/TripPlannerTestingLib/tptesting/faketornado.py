from tornado.web import ChunkedTransferEncoding
from tornado import httputil
import urlparse
import cgi

class WebApplicationFake(object):

    def __init__(self):
        self.__usage = list()

    def __call__(self, handlers=None, default_host='', transforms=None, 
            wsgi=False, **settings):
        self.handlers = handlers
        self.default_host = default_host
        self.transforms = [ChunkedTransferEncoding]
        self.settings = settings
        self.ui_methods = {}
        self.ui_modules = {}

        return self

    def add_handlers(self, host_pattern, host_handlers):
        raise NotImplementedError

    def add_transform(self, transform_class):
        raise NotImplementedError

    def listen(self, port, address='', **kwargs):
        self.__usage.append((self.listen, (port, address, kwargs)))

    def log_request(self, handler):
        raise NotImplementedError

    def reverse_url(self, name, *args):
        raise NotImplementedError

class IOLoopFake(object):
    def start(self):
        pass

    def add_timeout(self, timeout, connect):
        connect()


class ioloop(object):

    class IOLoop(object):
        @staticmethod
        def instance():
            return IOLoopFake()


class HTTPRequestFake(object):

    def __init__(self, method, uri, version='HTTP/1.0', headers=None, body=None,
            remote_ip=None, protocol=None, host=None, files=None, connection=None):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers or httputil.HTTPHeaders()
        self.body = body or ""
        self.host = host
        #self.connection = connection
        scheme, netloc, path, query, fragment = urlparse.urlsplit(uri)
        self.path = path
        self.query = query
        self.arguments = cgi.parse_qs(query)

    def finish(self):
        raise NotImplementedError

    def full_url(self):
        raise NotImplementedError

    def get_ssl_certificate(self):
        raise NotImplementedError

    def request_time(self):
        raise NotImplementedError

    def supports_http_1_1(self):
        return self.version == 'HTTP/1.1'

    def write(self, chunk):
        raise NotImplementedError


