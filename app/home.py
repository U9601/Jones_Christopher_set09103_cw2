from flask import Flask, render_template, url_for, redirect
from app import app

app = Flask(__name__)

@app.route('/')
def home():
    name = ''
    return render_template('home.html', name = name)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
