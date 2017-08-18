from Light import Light,render_template


app = Light()

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html',args = {'names': ['1','2']})

@app.route("/test/js")
def test_js():
        return '<script src="/static/test.js"></script>'
app.run()
