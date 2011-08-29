class UsageRecord(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "<UsageRecord(%s, *%s, **%s)>" % (self.name, self.args, self.kwargs)

    def __eq__(self, other):
        if other.name != self.name:
            return False

        if other.args != self.args:
            return False

        if other.kwargs != self.kwargs:
            return False

        return True


class FunctionSpy(object):
    def __init__(self, spy, name, return_spec=None):
        self.spy = spy
        self.name = name
        self.__return_spec = return_spec
        self.__args = []
        self.__kwargs = []

    def __get_called(self):
        return len(self.__args) > 0 
    called = property(fget=__get_called, 
            doc="""Returns True if method was called, False if not""")

    def __get_args(self):
        return tuple(self.__args)
    args = property(fget=__get_args, 
            doc="""Returns tuple of all args method called with""")

    def __get_kwargs(self):
        return tuple(self.__kwargs)
    kwargs = property(fget=__get_kwargs, 
            doc="""Returns tuple of all kwargs method called with""")

    def __call__(self, *args, **kwargs):
        self.__args.append(args)
        self.__kwargs.append(kwargs)

        self.spy.record_usage(self.name, *args, **kwargs)
        if (callable(self.__return_spec)):
            return self.__return_spec(*args, **kwargs)

        return self.__return_spec

class SpyObject(object):

    def __init__(self, method_call_spec=tuple()):
        self.__inited = False
        self.__usage = list()
        self.method_call_spec = method_call_spec

    def __call__(self, *args, **kwargs):
        if not self.__inited:
            self.__inited = True
            self.record_usage('__init__', *args, **kwargs)
            return self

        self.record_usage('__call__', *args, **kwargs)
        if (callable(self.method_call_spec)):
            return self.method_call_spec(*args, **kwargs)

    def __getattr__(self, name):
        if name == 'usage':
            return self.__usage

        function_spy = FunctionSpy(self, name)
        setattr(self, name, function_spy)
        return function_spy 

    def record_usage(self, name, *args, **kwargs):
        self.__usage.append(UsageRecord(name, *args, **kwargs))

    def verify_usage(self, usage_record):
        try:
            self.__usage.index(usage_record)
        except ValueError:
            return False

        return True

    def was_called(self, method):
        for usage in self.__usage:
            if usage.name == method:
                return True

        return False


