from flask import Flask
from flask import render_template
import requests

url = "https://api.themoviedb.org/3/"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkMGI3OTVhMjQ2MzBkYTRhZjVkMTgwOTJkZGNlODE4MSIsInN1YiI6IjY2MjJhMTAwZTRjOWViMDBjN2Y0ZTFjYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.y6uNWZ--j5-V1-HTOdWk59EiCjvrNRMNHPzAwtu8ncg"
}


app = Flask(__name__)

# https://image.tmdb.org/t/p/original/[poster_path]

# npx tailwindcss -i ./app/static/src/input.css -o ./app/static/src/main.css --watch

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)