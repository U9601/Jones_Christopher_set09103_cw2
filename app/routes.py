from __future__ import print_function
from flask import *
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import RegistrationForm, LoginForm, NewsForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, PostForm
from app.models import User, Post, News
from app.email import send_password_reset_email
from app import app, db
from werkzeug.urls import url_parse
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from python_utils import converters
import sys

top5teams = json.load(open("app/data/top5teams.json"))
top20teams = json.load(open("app/data/top20teams.json"))
matches = json.load(open("app/data/matches.json"))

teamslist5 = top5teams["top5teams"]
teamslist20 = top20teams["top20teams"]
matchlist20th = matches["20-11-2018"]
matchlist21st = matches["21-11-2018"]
matchlist22nd = matches["22-11-2018"]
matchlist23rd = matches["23-11-2018"]
matchlist24th = matches["24-11-2018"]
matchlist25th = matches["25-11-2018"]

def get_parsed_page(url):
    return BeautifulSoup(requests.get(url).text, "lxml")

@app.route('/', methods=['GET', 'POST'])
@app.route('/news', methods=['GET', 'POST'])
def news():
    name = ''
    home = get_parsed_page("http://hltv.org/")
    count = 0
    teams = []
    news = News.query.order_by(News.timestamp.desc())
    for team in home.find_all("div", {"class": ["col-box rank"], }):
        count += 1
        teamname = team.text[3:]
        teams.append(teamname)
    newsform = NewsForm()
    if newsform.validate_on_submit():
        newspost = News(username=newsform.username.data, title=newsform.title.data, body=newsform.body.data)
        db.session.add(newspost)
        db.session.commit()
        flash('You have created a post')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in teamslist5:
        output.append(x)
    return render_template('news.html', form = form, name = name, teams = teams, news = news, newsform = newsform, output=output)

@app.route('/matches', methods=['GET', 'POST'])
def matches():
    name = ''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    output20th = []
    for x in matchlist20th:
        output20th.append(x);
    output21st = []
    for x in matchlist21st:
        output21st.append(x)
    output22nd = []
    for x in matchlist22nd:
        output22nd.append(x)
    output23rd = []
    for x in matchlist23rd:
        output23rd.append(x)
    output24th = []
    for x in matchlist24th:
        output24th.append(x)
    output25th = []
    for x in matchlist25th:
        output25th.append(x)
    return render_template('matches.html', form = form, name = name, output20th=output20th, output21st=output21st, output22nd=output22nd, output23rd=output23rd, output24th=output24th, output25th=output25th)

@app.route('/login', methods=['GET', 'POST'])
def login():
    name = ''
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('login.html', title = 'Sign In', form = form, name = name)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('news'))

@app.route('/forum' , methods=['GET', 'POST'])
def forum():
    name = ''
    postform = PostForm()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    if postform.validate_on_submit():
        post = Post(body=postform.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('forum'))
    posts = [
        {
            'author': {'username': 'U9601'},
            'body': 'Beautiful day in Scotland!'
        },
        {
            'author': {'username': 'banter'},
            'body': 'heheh'
        }
    ]
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('forum', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('forum', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('forum.html', form = form, name = name, postform = postform, next_url=next_url, prev_url=prev_url, posts = posts.items)

@app.route('/results' , methods=['GET', 'POST'])
def results():
    name = ''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('results.html', form = form, name = name)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    name = ''
    return render_template('dashboard.html', name = name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    name = ''
    if current_user.is_authenticated:
        return redirect(url_for('news'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a user Pog')
        return redirect(url_for('dashboard'))
    return render_template('register.html', name = name, form = form)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user = user, posts = posts.items, next_url = next_url, prev_url = prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved Pog')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form = form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('news'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your emails')
        return redirect(url_for('news'))
    return render_template('reset_password_request.html', title ='Reset Password', form = form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('news'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('news'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('news'))
    return render_template('reset_password.html', form=form)

@app.route('/top20teams', methods=['GET', 'POST'])
def top20teams():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in teamslist20:
        output.append(x)
    return render_template('top20teams.html', form=form, output=output)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
