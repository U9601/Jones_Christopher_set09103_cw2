from flask import render_template
from app import app, db
from app.forms import LoginForm

@app.errorhandler(404)
def not_found_error(error):
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('404.html', form=form), 404

@app.errorhandler(500)
def internal_error(error):
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    db.session.rollback()
    return render_template('500.html', form=form), 500
