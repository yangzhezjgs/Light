class View:
	methods = None
	methods_meta = None
	def dispatch_request(self,request,*args,**option):
		raise NotImplementedError
	@classmethod
	def get_func(cls,name):
		def func(*args,**kwargs):
			obj = func.view_class()
			return obj.dispatch_request(*args,**kwargs)
		func.view_class = cls
		func.__name__=name
		func.__doc__ = cls.__doc__
		func.methods = cls.methods
		return func


class BaseView(View):
    methods = ['GET, POST']

    def post(self, request, *args, **options):
        pass

    def get(self, request, *args, **options):
        pass

    def dispatch_request(self, request, *args, **options):
        methods_meta = {
            'GET': self.get,
            'POST': self.post,
        }

        if request.method in methods_meta:
            return methods_meta[request.method](request, *args, **options)
        else:
            return '<h1>Unknown or unsupported require method</h1>'


class Controller:
	def __init__(self,name,url_map):
		self.url_map = url_map
		self.name = name
	def __name__(self):
		return self.name
