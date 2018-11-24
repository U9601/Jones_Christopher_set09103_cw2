from app import app
from app.models import User, Post, Notification, Message, News, NewsBody, PostLike, Comment

@app.shell_context_processor
def make_sell_context():
    reutrn {'db': db, 'User': User, 'Post': Post, 'Notification': Notfication, 'Message': Message,
            'News': News, 'NewsBody': NewsBody, 'PostLike': PostLike, 'Comment': Comment}
