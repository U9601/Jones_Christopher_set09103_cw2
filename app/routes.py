from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_user, login_required, logout_user
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from app import app, db
from werkzeug.urls import url_parse

@app.route('/')
def home():
    return render_template('news.html')

@app.route('/matches')
def matches():
    name = ''
    return render_template('matches.html', name = name)

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
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashbaord')
        return redirect(next_page)
    return render_template('login.html', title = 'Sign In', form = form, name = name)

@app.route('/logout')
def logout():
    logout_user()
    return render_template('news.html')

@app.route('/forum')
def fourm():
    name = ''
    return render_template('fourm.html', name = name)

@app.route('/results')
def results():
    name = ''
    return render_template('results.html', name = name)

@app.route('/dashboard')
@login_required
def dashboard():
    name = ''
    return render_template('dashboard.html', posts = posts, name = name)

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
        return redirect(url_for(''))
    return render_template('register.html', name = name, form = form)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
