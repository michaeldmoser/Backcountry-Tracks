from tornado.web import ChunkedTransferEncoding
from tornado import httputil
from tornado.escape import utf8, native_str, parse_qs_bytes
import Cookie
import urlparse
import cgi

class WebApplicationFake(object):

    def __init__(self):
        self.__usage = list()

    def record_usage(self, method, *args, **kwargs):
        self.__usage.append((method, args, kwargs))

    def verify_usage(self, method, args, kwargs):
        '''
        Returns True if method was called and the args and kwargs match the call, 
        otherwise returns False

        method is function object instance on this class
        '''
        for method_call in self.__usage:
            instancemethod = method_call[0]

            if not callable(instancemethod):
                continue

            unbound_method = getattr(instancemethod.im_class, instancemethod.__name__)
            search_unbound_method = getattr(method.im_class, method.__name__)
            if unbound_method == search_unbound_method:
                if args != '*' and method_call[1] != args:
                    return False

                if kwargs != '*' and method_call[2] != kwargs:
                    return False

                return True

        return False

    def was_called(self, method):
        '''
        Returns True if method was called otherwise returns false

        method is function object instance on this class
        '''
        for method_call in self.__usage:
            instancemethod = method_call[0]

            if not callable(instancemethod):
                continue

            unbound_method = getattr(instancemethod.im_class, instancemethod.__name__)
            search_unbound_method = getattr(method.im_class, method.__name__)
            if unbound_method == search_unbound_method:
                return True

        return False

    @property
    def usage(self):
        return self.__usage

###
### These methods are part of the Pika API, these can/should be used
### in production code
###

    def __call__(self, handlers=None, default_host='', transforms=None,
            wsgi=False, **settings):
        self.handlers = handlers
        self.default_host = default_host
        self.transforms = [ChunkedTransferEncoding]
        self.ui_methods = {}
        self.ui_modules = {}
        self._wsgi = wsgi
        self.settings = {
            'cookie_secret': 'test_secret',
            'login_url': '/login'
            }
        self.settings.update(settings)

        return self

    def add_handlers(self, host_pattern, host_handlers):
        raise NotImplementedError

    def add_transform(self, transform_class):
        raise NotImplementedError

    def listen(self, port, address='', **kwargs):
        self.record_usage(self.listen, port, address=address, **kwargs)

    def log_request(self, handler):
        pass

    def reverse_url(self, name, *args):
        raise NotImplementedError

class IOLoopFake(object):
    def __init__(self):
        self.timeout_callbacks = list()

    def start(self):
        for callback in self.timeout_callbacks:
            callback()

    def add_timeout(self, timeout, connect):
        self.timeout_callbacks.append(connect)


class ioloop(object):

    class IOLoop(object):
        @staticmethod
        def instance():
            return IOLoopFake()


class HTTPRequestFake(object):

    def __init__(self, method, uri, version='HTTP/1.0', headers=None, body=None,
            remote_ip='127.0.0.1', protocol=None, host=None, files=None, connection=None):
        self.__usage = list()

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
        self.files = files or {}
        self.remote_ip = remote_ip

        self._output = ""

    def was_called(self, method):
        '''
        Returns True if method was called otherwise returns false

        method is function object instance on this class
        '''
        for method_call in self.__usage:
            instancemethod = method_call[0]

            if not callable(instancemethod):
                continue

            unbound_method = getattr(instancemethod.im_class, instancemethod.__name__)
            search_unbound_method = getattr(method.im_class, method.__name__)
            if unbound_method == search_unbound_method:
                return True

        return False

    def record_usage(self, method, *args, **kwargs):
        self.__usage.append((method, args, kwargs))

    def finish(self):
        self.record_usage(self.finish)

    def full_url(self):
        raise NotImplementedError

    def get_ssl_certificate(self):
        raise NotImplementedError

    def request_time(self):
        raise NotImplementedError

    def supports_http_1_1(self):
        return self.version == 'HTTP/1.1'

    def write(self, chunk, callback=None):
        self.record_usage(self.finish, chunk)
        self._output += str(chunk)

    @property
    def cookies(self):
        """A dictionary of Cookie.Morsel objects."""
        if not hasattr(self, "_cookies"):
            self._cookies = Cookie.SimpleCookie()
            if "Cookie" in self.headers:
                try:
                    self._cookies.load(
                        native_str(self.headers["Cookie"]))
                except Exception:
                    self._cookies = {}
        return self._cookies


