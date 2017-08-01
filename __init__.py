#coding:utf-8
from werkzeug.wrappers import Response,Request
from Light.Route import Route

class Light:

	def __init__(self):
		self.url_map = {}
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

	def add_url_rule(self,url,func,**options):
		self.url_map[url] = func


