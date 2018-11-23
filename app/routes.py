from __future__ import print_function
from flask import *
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from app.forms import RegistrationForm, LoginForm, NewsForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, PostForm, CommentForm
from app.models import User, Post, News, Comment
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
top5players = json.load(open("app/data/top5players.json"))
events = json.load(open("app/data/events.json"))
results = json.load(open("app/data/results.json"))

teamslist5 = top5teams["top5teams"]
teamslist20 = top20teams["top20teams"]
playerslist = top5players["top5players"]
eventslist = events["events"]
matchlist20th = matches["20-11-2018"]
matchlist21st = matches["21-11-2018"]
matchlist22nd = matches["22-11-2018"]
matchlist23rd = matches["23-11-2018"]
matchlist24th = matches["24-11-2018"]
matchlist25th = matches["25-11-2018"]
resultslist19th = results["19-11-2018"]
resultslist18th = results["18-11-2018"]
resultslist17th = results["17-11-2018"]
resultslist16th = results["16-11-2018"]
resultslist15th = results["15-11-2018"]

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
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    players = []
    listofevents = []
    for x in teamslist5:
        output.append(x)
    for x in playerslist:
        players.append(x)
    for x in eventslist:
        listofevents.append(x)
    return render_template('news.html', form = form, name = name, teams = teams, news = news, newsform = newsform, output=output, players=players, listofevents=listofevents)

@app.route('/matches', methods=['GET', 'POST'])
def matches():
    name = ''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
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
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    return render_template('login.html', title = 'Sign In', form = form, name = name)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('news'))

@app.route('/forum' , methods=['GET', 'POST'])
@login_required
def forum():
    name = ''
    postform = PostForm()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    if postform.validate_on_submit():
        post = Post(body=postform.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('forum'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('forum', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('forum', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('forum.html', form = form, name = name, postform = postform, next_url=next_url, prev_url=prev_url, posts = posts.items)

@app.route('/comments/<post_id>' , methods=['GET', 'POST'])
@login_required
def comments(post_id):
    post = Post.query.get(post_id)
    commentform = CommentForm()
    if commentform.validate_on_submit():
        comment = Comment(body=commentform.comment.data, post_id=post.id, username=current_user.username, timestamp=datetime.utcnow())
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("comments", post_id=post.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    return render_template('comments.html', commentform=commentform, post_id=post_id, post=post, form=form)


@app.route('/results' , methods=['GET', 'POST'])
def results():
    name = ''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output19th = []
    for x in resultslist19th:
        output19th.append(x)
    output18th = []
    for x in resultslist18th:
        output18th.append(x)
    output17th = []
    for x in resultslist17th:
        output17th.append(x)
    output16th = []
    for x in resultslist16th:
        output16th.append(x)
    output15th = []
    for x in resultslist15th:
        output15th.append(x)
    return render_template('results.html', form = form, name = name, output19th = output19th, output18th = output18th, output17th = output17th, output16th = output16th, output15th = output15th)

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
        return redirect(url_for('news'))
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


@app.route('/matchdetails/havuvsrr', methods=['GET', 'POST'])
def HAVUvsRR():
    name = 'HAVUvsRR'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/sproutvsldlc', methods=['GET', 'POST'])
def SproutVSLDLC():
    name = 'SproutVSLDLC'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/quescovsforze', methods=['GET', 'POST'])
def QuescovsforZe():
    name = 'QuescovsforZe'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/windigoavssmoke', methods=['GET', 'POST'])
def WindigoAvsSmoke():
    name = 'WindigoAvsSmoke'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/fcdbvswindigo', methods=['GET', 'POST'])
def FCBDvsWindigo():
    name = 'FCBDvsWindigo'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/3dmaxvsalternate', methods=['GET', 'POST'])
def threeDMAXvsAlternate():
    name = '3DMAXvsAlternate'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/trickedvsvexed', methods=['GET', 'POST'])
def TrickedvsVexed():
    name = 'TrickedvsVexed'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/isurusvsuruguay', methods=['GET', 'POST'])
def IsurusvsUruguay():
    name = 'IsurusvsUruguay'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/sproutvsldlc2', methods=['GET', 'POST'])
def SproutvsLDLC2():
    name = 'SproutvsLDLC2'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/wildvsisurus', methods=['GET', 'POST'])
def WildvsIsurus():
    name = 'WildvsIsurus'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist20th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/w7mvsfuria', methods=['GET', 'POST'])
def W7MvsFuria():
    name = 'W7MvsFuria'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist21st:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/euronicsvstricked', methods=['GET', 'POST'])
def EURONICSvsTricked():
    name = 'EURONICSvsTricked'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist21st:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/havuvsex6tence', methods=['GET', 'POST'])
def HAVUvsx6tence():
    name = 'HAVUvsx6tence'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist21st:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/astvsc9', methods=['GET', 'POST'])
def AstvsC9():
    name = 'AstvsC9'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist22nd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/vexedvsvaliance', methods=['GET', 'POST'])
def VexedvsValiance():
    name = 'VexedvsValiance'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist22nd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/mouzvsmibr', methods=['GET', 'POST'])
def MouzvsMIBR():
    name = 'MouzvsMIBR'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist22nd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/nrgvsnip', methods=['GET', 'POST'])
def NRGvsNIP():
    name = 'NRGvsNIP'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist22nd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/liquidvsnorth', methods=['GET', 'POST'])
def LiquidvsNorth():
    name = 'LiquidvsNorth'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist22nd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecsgroupawinner', methods=['GET', 'POST'])
def ECSGroupAWinner():
    name = 'ECSGroupAWinner'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist22nd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecsgroupbwinner', methods=['GET', 'POST'])
def ECSGroupBWinner():
    name = 'ECSGroupBWinner'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist23rd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecsgroupaelim', methods=['GET', 'POST'])
def ECSGroupAElim():
    name = 'ECSGroupAElim'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist23rd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/expertvsldlc', methods=['GET', 'POST'])
def ExpertvsLDLC():
    name = 'ExpertvsLDLC'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist23rd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecsgroupbelim', methods=['GET', 'POST'])
def ECSGroupBElim():
    name = 'ECSGroupBElim'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist23rd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecsgroupbdecider', methods=['GET', 'POST'])
def ECSGroupBDecider():
    name = 'ECSGroupBDecider'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist23rd:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecssemifinal1', methods=['GET', 'POST'])
def ECSSemiFinal1():
    name = 'ECSSemiFinal#1'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist24th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecssemifinal2', methods=['GET', 'POST'])
def ECSSemiFinal2():
    name = 'ECSSemiFinal#2'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist24th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/matchdetails/ecsgrandfinal', methods=['GET', 'POST'])
def ECSGrandFinal():
    name = 'ECSGrandFinal'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in matchlist25th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/dentonavscoolkids', methods=['GET', 'POST'])
def DentonavscOOLkids():
    name = 'DentonavscOOLkids'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/yeahvsnoorg', methods=['GET', 'POST'])
def YeahvsNOORG():
    name = 'YeahvsNOORG'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/ldlcvs3dmax', methods=['GET', 'POST'])
def LDLCvs3DMAX():
    name = 'LDLCvs3DMAX'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/windigoavsnemiga', methods=['GET', 'POST'])
def WindigoavsNemiga():
    name = 'WindigoavsNemiga'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/windigovsvaliance', methods=['GET', 'POST'])
def WindigovsValiance():
    name = 'WindigovsValiance'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/mvppkvsgosu', methods=['GET', 'POST'])
def MVPPKvsGOSU():
    name = 'MVPPKvsGOSU'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/renegadesvstaintedminds', methods=['GET', 'POST'])
def RenegadesvsTaintedMinds():
    name = 'RenegadesvsTaintedMinds'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/ordervstaintedminds', methods=['GET', 'POST'])
def OrdervsTaintedMinds():
    name = 'OrdervsTaintedMinds'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/renegadesvsgrayhound', methods=['GET', 'POST'])
def RenegadesvsGrayhound():
    name = 'RenegadesvsGrayhound'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/luminosityvsvitality', methods=['GET', 'POST'])
def LuminosityvsVitality():
    name = 'LuminosityvsVitality'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist19th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/complexityvsvitality', methods=['GET', 'POST'])
def compLexityvsVitality():
    name = 'compLexityvsVitality'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist18th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/imperialvswild', methods=['GET', 'POST'])
def ImperialvsWild():
    name = 'ImperialvsWild'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist18th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/gambitvspugstar5', methods=['GET', 'POST'])
def GambitvsPUGSTAR5():
    name = 'GambitvsPUGSTAR5'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist18th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/forzevspro100', methods=['GET', 'POST'])
def forZevsPro100():
    name = 'forZevsPro100'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist18th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/taintedmindsvslegacy', methods=['GET', 'POST'])
def TaintedMindsvsLegacy():
    name = 'TaintedMindsvsLegacy'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist18th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/renegadesvsbreakaway', methods=['GET', 'POST'])
def RenegadesvsBreakaway():
    name = 'RenegadesvsBreakaway'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist18th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/roguevsvitality', methods=['GET', 'POST'])
def RoguevsVitaltiy():
    name = 'RoguevsVitaltiy'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist17th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/euronicsvstricked', methods=['GET', 'POST'])
def resultEURONICSvsTricked():
    name = 'EURONICSvsTricked'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist17th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/eunitedvsluminosity', methods=['GET', 'POST'])
def eUnitedvsLuminosity():
    name = 'eUnitedvsLuminosity'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist17th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/fragstersvsrogue', methods=['GET', 'POST'])
def FragstersvsRogue():
    name = 'FragstersvsRogue'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist16th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/ghostvsvitality', methods=['GET', 'POST'])
def GhostvsVitality():
    name = 'GhostvsVitality'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist16th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/complexityvsenvyus', methods=['GET', 'POST'])
def compLexityvsEnvyUs():
    name = 'compLexityvsEnvyUs'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist16th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/agovskinguin', methods=['GET', 'POST'])
def AGOvsKinguin():
    name = 'AGOvsKinguin'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist16th:
        output.append(x)
    return render_template('matchdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/ordervsavant', methods=['GET', 'POST'])
def OrdervsAvant():
    name = 'OrdervsAvant'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist16th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/epsilionvskinguin', methods=['GET', 'POST'])
def EpsilonvsKinguin():
    name = 'EpsilonvsKinguin'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist15th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)

@app.route('/resultsdetails/trickedvsnexus', methods=['GET', 'POST'])
def TrickedvsNexus():
    name = 'TrickedvsNexus'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('news'))
        login_user(user, remember=form.remember_me.data)
    output = []
    for x in resultslist15th:
        output.append(x)
    return render_template('resultsdetails.html', form=form, name = name, output=output)




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
