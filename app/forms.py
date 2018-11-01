from flask_wtf import FlaskForm
from wtforms import (BooleanField, FileField, HiddenField, PasswordField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    title = TextAreaField(
        'Title', validators=[DataRequired(),
                             Length(min=1, max=500)])
    body = TextAreaField(
        'Post', validators=[DataRequired(),
                                     Length(min=1, max=50000)])
    photo = FileField()
    submit = SubmitField('Publish')


class CommentForm(FlaskForm):
    comment = TextAreaField(
        '', validators=[DataRequired(),
                        Length(min=1, max=50000)])
    submit = SubmitField('Comment')


class ReplyForm(FlaskForm):
    reply = TextAreaField(
        '', validators=[DataRequired(),
                        Length(min=1, max=50000)])
    submit = SubmitField('Reply')
    commentId = HiddenField()


class LikeForm(FlaskForm):
    like = SubmitField('Like')
