from webapp import WebApp,View,render_template
from orm import Model,StringField

class User(Model):
    __table__ = 'users'
    __database__='my_user'
    id = StringField(primary_key=True, ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')


class Index(View):
	def GET(self,request):
		user1 = User.filter()[0]
		name = user1.get('name')
		return render_template("index.html",name=name)

class Test(View):
	def GET(self,request,my_id):
		return "test",my_id

urls = [
{
	'url':'/',
	'view':Index
},
{
   'url':'/test/<my_id>',
   'view':Test
}
] 
if __name__ == '__main__':

    app = WebApp()

    app.add_url_rule(urls)

    app.run()


