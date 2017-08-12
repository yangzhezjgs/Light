#coding:utf-8
from werkzeug.wrappers import Response,Request
from Light.Route import Route
from Light.exceptions as exceptions
from Light.helper import parse_stat
ERROR_MAP = {
    '401': Response('<h1>401 Unknown or unsupported method</h1>', content_type='text/html; charset=UTF-8', status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8', status=404),
    '503': Response('<h1>503 Unknown function type</h1>', content_type='text/html; charset=UTF-8',  status=503)
}

# 定义文件类型
TYPE_MAP = {
    'css':  'text/css',
    'js': 'text/js',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg'
}

class ExecFunc:
	def __init__(self,func,func_type,**options):
		self.func = func
		self.options = options
		self.func_type = func_type

class Light:

	def __init__(self,static_folder='static'):
		self.host = '127.0.0.1'
		self.port = 8080
		self.url_map = {}
		self.static_map = {}
		self.function_map = {}
		self.static_folder = static_folder
		self.route = Route(self)

	def __call__(self,environ,start_response):
		return self.wsgi_app(environ,start_response)
	
	def dispatch_request(self,request):
		url = "/" + "/".join(request.url.split("/")[3:]).split("?")[0]
		
		rep = self.url_map[url]()
		status = 200  
		headers = {
			 'Server': 'Shiyanlou Framework'
		 }

		return Response(rep, content_type='text/html', headers=headers, status=status)
		
	def wsgi_app(self,environ,start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def add_url_rule(self,url,func,func_type,endpoint=None,**options):
		if endpoint is None:
			endpoint = func.__name__
		if url in self.url_map:
			raise exceptions.URLExistsError
		if endpoint in self.function_map and func_type != 'static':
			raise exceptions.EndpointExistsError
		self.url_map[url] = endpoint
		self.function_map[endpoint] = ExecFunc(func,func_type,**options)

	def run(self,host=None,port=None,**options):
		for key,value in options.item():
			if value is not None:
				self.__setattr__(key,value)
			if host:
				self.host = host
			if port:
				self.port = port
		run_simple(hostname=self.host,port=self.port,application=self,**options)
