import math
from datetime import datetime
from hashlib import md5

import pretty
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

followers = db.Table(
    'followers', db.Column('follower_id', db.Integer,
                           db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    replies = db.relationship('Reply', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    number_of_posts = db.Column(db.Integer)
    image_path = db.Column(db.String(5000))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    full_name = db.Column(db.String(240))
    likes = db.relationship('Like', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic')

    def edit_profile_image(self, image_path):
        self.image_path = image_path

    def increment_posts(self):
        posts = self.number_of_posts
        if posts != None:
            posts = posts + 1
        else:
            posts = 0
        self.number_of_posts = posts

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def user_posts(self):
        posts = Post.query.filter_by(user_id=self.id)
        return posts


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    body = db.Column(db.String(50000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    replies = db.relationship('Reply', backref='post', lazy='dynamic')
    number_of_comments = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    tags = db.Column(db.String(500))
    image_path = db.Column(db.String(5000))
    liked_by = db.relationship('Like', backref='post', lazy='dynamic')
    views = db.Column(db.Integer)

    def increment_views(self):
        views = self.views
        if views != None:
            views = views + 1
        else:
            views = 1
        self.views = views

    def decrement_views(self):
        views = self.views
        if views != None:
            views = views - 1
        else:
            views = 0
        self.views = views

    def elapsedTime(self):
        elapsedTime = pretty.date(self.timestamp, short=True).split(' ')
        formattedTime = ''
        for element in elapsedTime:
            if element[0].isdigit():
                formattedTime = element
                break
        return str(math.ceil(float(
            formattedTime[:-1]))) + formattedTime[len(formattedTime) - 1]

    def getSynopsis(self):
        return self.body[:200] + '...'

    def increment_comments_counter(self):
        comments = self.number_of_comments
        if likes != None:
            comments = comments + 1
        else:
            comments = 1
        self.number_of_comments = comments

    def increment_likes(self):
        likes = self.likes
        if likes != None:
            likes = likes + 1
        else:
            likes = 1
        self.likes = likes

    def decrement_likes(self):
        likes = self.likes
        if likes != None:
            likes = likes - 1
        else:
            likes = 0
        self.likes = likes

    def __repr__(self):

        return '<Post {}>'.format(self.body)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    replies = db.relationship('Reply', backref='comment', lazy='dynamic')

    def __repr__(self):

        return '<Comment {}>'.format(self.body)


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    def __repr__(self):

        return '<Reply {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
