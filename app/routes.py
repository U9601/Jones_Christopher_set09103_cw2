from flask import render_template, url_for, redirect
from app import app

@app.route('/')
def home():
    name = ''
    return render_template('news.html', name = name)

@app.route('/matches')
def matches():
    name = ''
    return render_template('matches.html', name = name)

@app.route('/login')
def login():
    name = ''
    return render_template('login.html', name = name)

@app.route('/fourm')
def fourm():
    name = ''
    return render_template('fourm.html', name = name)

@app.route('/results')
def results():
    name = ''
    return render_template('results.html', name = name)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
