from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from hltv import hltv
from app import app, db
from werkzeug.urls import url_parse

@app.route('/', methods=['GET', 'POST'])
@app.route('/news', methods=['GET', 'POST'])
def news():
    name = ''
    teams = hltv.top5teams()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('news.html', form = form, name = name, teams = teams)

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
    return render_template('matches.html', form = form, name = name)

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
def fourm():
    name = ''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('fourm.html', form = form, name = name)

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
        return redirect(url_for('dashboard'))
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
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user = user, posts = posts)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
