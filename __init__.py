#coding:utf-8
from werkzeug.wrappers import Response,Request
from Light.Route import Route
import Light.exceptions as exceptions
from Light.helper import parse_static_key
from werkzeug.serving import run_simple
from Light.templates import Template
import os,json
ERROR_MAP = {
    '401': Response('<h1>401 Unknown or unsupported method</h1>', content_type='text/html; charset=UTF-8', status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8', status=404),
    '503': Response('<h1>503 Unknown function type</h1>', content_type='text/html; charset=UTF-8',  status=503)
}
def render_json(data):
    content_type = "text/plain"
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
        content_type = "application/json"
    return Response(data, content_type="%s; charset=UTF-8" % content_type, status=200)

def render_template(path,args):
        return template(Light, path, args)
def template(app,path,args={}):
    txt=''
    path = os.path.join(app.template_folder, path)
    if os.path.exists(path):
        txt = open(path,'rb').read().decode()
    t = Template(txt)
    return t.render(args)


def redirect(url,status_code=302):
    response = Response('', status=status_code)
    response.headers['Location'] = url
    return response

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

	def __init__(self,template_folder='templates',static_folder='static'):
		self.host = '127.0.0.1'
		self.port = 8080
		self.url_map = {}
		self.static_map = {}
		self.function_map = {}
		self.static_folder = static_folder
		self.route = Route(self)
		self.template_folder = template_folder
		Light.template_folder = template_folder

	def __call__(self,environ,start_response):
		return self.wsgi_app(environ,start_response)
	def dispatch_static(self, static_path):
		if os.path.exists(static_path):
			key = parse_static_key(static_path)
			doc_type = TYPE_MAP.get(key, 'text/plain')
			with open(static_path, 'rb') as f:
				rep = f.read()
			return Response(rep, content_type=doc_type)
		else:
			return ERROR_MAP['404']

	def dispatch_request(self,request):
		url = "/" + "/".join(request.url.split("/")[3:]).split("?")[0]
		if url.find(self.static_folder) == 1 and url.index(self.static_folder) == 1:
			endpoint = 'static'
			url = url[1:]
		else:
			endpoint = self.url_map.get(url,None)
		headers = {'Server':'Light Web 0.1'}
		if endpoint is None:
			return ERROR_MAP['404']
		exec_function = self.function_map[endpoint]
		if exec_function.func_type == 'route':
			if request.method in exec_function.options.get('methods'):
				argcount = exec_function.func.__code__.co_argcount
				if argcount > 0:
					rep = exec_function.func(request)
				else:
					rep = exec_function.func()
			else:
				return ERROR_MAP['401']
		elif exec_function.func_type == 'view':
			rep = exec_function.func(request)
		elif exec_function.func_type == 'static':
			return exec_function.func(url)
		else:
			return ERROR_MAP['503']
		status = 200
		content_type = 'text/html'
		return Response(rep,content_type='%s;charset=UTF-8'%content_type,headers = headers,status = status)



		return Response(rep, content_type='text/html', headers=headers, status=status)
		
	def wsgi_app(self,environ,start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)
	
	def bind_view(self,url,view_class,endpoint):
		self.add_url_rule(url,func=view_class.get_func(endpoint),func_type='view')
	def add_url_rule(self,url,func,func_type,endpoint=None,**options):
		if endpoint is None:
			endpoint = func.__name__
		if url in self.url_map:
			raise exceptions.URLExistsError
		if endpoint in self.function_map and func_type != 'static':
			raise exceptions.EndpointExistsError
		self.url_map[url] = endpoint
		self.function_map[endpoint] = ExecFunc(func,func_type,**options)
	def load_controller(self,controller):
		name = controller.__name__()
		for rule in controller.url_map:
			self.bind_view(rule['url'],rule['view'],name + '.'+rule['endpoint'])
	def run(self,host=None,port=None,**options):
		for key,value in options.items():
			if value is not None:
				self.__setattr__(key,value)
			if host:
				self.host = host
			if port:
				self.port = port
		self.function_map['static'] = ExecFunc(func=self.dispatch_static,func_type='static')
		run_simple(hostname=self.host,port=self.port,application=self,**options)
