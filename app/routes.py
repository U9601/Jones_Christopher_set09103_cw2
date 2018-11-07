from flask import render_template, url_for, redirect
from app import app

@app.route('/')
def home():
    name = ''
    return render_template('news.html', name = name)

@app.route('/matches')
def mathes():
    name = ''
    return render_template('')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
