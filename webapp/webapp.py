import os
from werkzeug.wrappers import BaseRequest, BaseResponse
from werkzeug.exceptions import HTTPException, MethodNotAllowed, \
     NotImplemented, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from jinja2 import Environment, FileSystemLoader

def render_template(template_name, **context):
    template_path = os.path.join(os.getcwd(), 'templates')
    jinja_env = Environment(loader=FileSystemLoader(template_path),autoescape=True)
    text = jinja_env.get_template(template_name).render(context)
    return text
	

class Request(BaseRequest):
    """Encapsulates a request."""


class Response(BaseResponse):
    """Encapsulates a response."""


class View(object):
    """Baseclass for our views."""
    def __init__(self):
        self.methods_meta = {
            'GET': self.GET,
            'POST': self.POST,
            'PUT': self.PUT,
            'DELETE': self.DELETE,
        }
    def GET(self):
        raise MethodNotAllowed()
    POST = DELETE = PUT = GET

    def HEAD(self):
       	return self.GET()
    def dispatch_request(self, request, *args, **options):
        if request.method in self.methods_meta:
            return self.methods_meta[request.method](request, *args, **options)
        else:
            return '<h1>Unknown or unsupported require method</h1>'

    @classmethod
    def get_func(cls):
        def func(*args, **kwargs):
            obj = func.view_class()
            return obj.dispatch_request(*args, **kwargs)
        func.view_class = cls
        return func

class WebApp(object):
    """
    An interface to a web.py like application.  It works like the web.run
    function in web.py
    """
    def __init__(self):
        self.url_map = Map()
        self.view_function = {}

    def wsgi_app(self,environ,start_response):
        req = Request(environ)
        response = self.dispatch_request(req)
        if response:
            response = Response(response,content_type='text/html; charset=UTF-8')
        else:
            response = Response('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8', status=404)
        return response(environ, start_response)


    def __call__(self,environ,start_response):
        return self.wsgi_app(environ,start_response)
	
    def dispatch_request(self,req):
        adapter = self.url_map.bind_to_environ(req.environ)
        try:
            endpoint, values = adapter.match()
            return self.view_function[endpoint](req, **values)
        except HTTPException as e:
            return e

    def add_url_rule(self,urls):
         for url in urls:
             rule = Rule(url['url'],endpoint=str(url['view']))
             self.url_map.add(rule)
             self.view_function[str(url['view'])]=url['view'].get_func()

    def run(self, port=5000, ip='', debug=False):
        run_simple(ip, port, self, use_debugger=debug, use_reloader=True)
 
