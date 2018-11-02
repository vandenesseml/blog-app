import hashlib
import os
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import (CommentForm, EditProfileForm, LikeForm, LoginForm,
                       PostForm, RegistrationForm, ReplyForm)
from app.models import Comment, Like, Post, Reply, User
from config import Config


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)

    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template(
        "index.html",
        title='Topics',
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url)


@app.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    form = PostForm()
    if form.validate_on_submit():
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        extension = filename.split('.')[1]
        filename = str(
            hashlib.md5(filename.split('.')[0].encode()).hexdigest())
        filename = filename + '.' + extension
        photo.save(os.path.join(Config.POST_IMAGE_UPLOAD_FOLDER, filename))
        post = Post(
            body=form.body.data,
            title=form.title.data,
            author=current_user,
            number_of_comments='0',
            likes='0',
            summary=form.summary.data,
            views='0',
            image_path=os.path.join(Config.POST_IMAGE_ACCESS_PATH, filename))
        current_user.increment_posts()
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    return render_template("publish.html", title='Publish', form=form)


@app.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def post(id):

    post = Post.query.filter_by(id=id).first()
    post.increment_views()
    db.session.commit()
    likeForm = LikeForm()
    commentForm = CommentForm()
    replyForm = ReplyForm()
    if commentForm.validate_on_submit():
        comment = Comment(
            body=commentForm.comment.data, post=post, author=current_user)
        post.decrement_views()
        db.session.add(comment)
        post.increment_comments_counter()
        db.session.commit()
        flash('Your comment is now live!')
        commentForm.comment.data = ''
        return render_template(
            "post.html",
            title='Post',
            post=post,
            likeForm=likeForm,
            commentForm=commentForm,
            replyForm=replyForm,
            scrollToAnchor=comment.id)
    elif replyForm.validate_on_submit():
        comment = Comment.query.filter_by(id=replyForm.commentId.data).first()
        reply = Reply(
            body=replyForm.reply.data,
            comment=comment,
            author=current_user,
            post=post)
        post.decrement_views()
        db.session.add(reply)
        post.increment_comments_counter()
        db.session.commit()
        flash('Your reply is now live!')
        replyForm.reply.data = ''
        return render_template(
            "post.html",
            title='Post',
            post=post,
            likeForm=likeForm,
            commentForm=commentForm,
            replyForm=replyForm,
            scrollToAnchor=reply.id)
    elif likeForm.validate_on_submit():
        liked = post.liked_by.filter_by(user_id=current_user.id).first()
        print(post.liked_by.filter_by(user_id=current_user.id).first())
        if not liked:
            print('no')
            like = Like(author=current_user, post=post)
            post.increment_likes()
            post.decrement_views()
            db.session.commit()
            likeForm.like.data = ''
            flash('Your like is now live!')
        else:
            post.liked_by.remove(liked)
            post.decrement_likes()
            post.decrement_views()
            db.session.commit()
            likeForm.like.data = ''
            flash('Your unlike is now live!')
            print(post.liked_by.filter_by(user_id=current_user.id).first())
        return render_template(
            "post.html",
            title='Post',
            post=post,
            likeForm=likeForm,
            commentForm=commentForm,
            replyForm=replyForm,
            scrollToAnchor='likePost')
    return render_template(
        "post.html",
        title='Post',
        post=post,
        likeForm=likeForm,
        commentForm=commentForm,
        replyForm=replyForm)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('latest'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('latest')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('latest'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            full_name=form.first_name.data + ' ' + form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.user_posts().order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('latest', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('latest', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template(
        'user.html',
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url)


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
        current_user.first_name = 'Jennifer'
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        extension = filename.split('.')[1]
        filename = str(
            hashlib.md5(filename.split('.')[0].encode()).hexdigest())
        filename = filename + '.' + extension
        photo.save(os.path.join(Config.PROFILE_IMAGE_UPLOAD_FOLDER, filename))
        current_user.image_path = os.path.join(
            Config.PROFILE_IMAGE_ACCESS_PATH, filename)
        db.session.commit()
        flash('Your profile changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template(
        'edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('latest')
        return redirect(next_page)
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('latest')
        return redirect(next_page)
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/', methods=['GET', 'POST'])
@app.route('/latest')
def latest():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('latest', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('latest', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template(
        "index.html",
        title='Latest',
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url)
