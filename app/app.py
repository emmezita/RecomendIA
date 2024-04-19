from flask import Flask
from flask import render_template

app = Flask(__name__)

# https://image.tmdb.org/t/p/original/[poster_path]

# npx tailwindcss -i ./app/static/src/input.css -o ./app/static/src/main.css --watch

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/login')
def login():
    return render_template('login/login.html')

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello/hello.html', name=name)