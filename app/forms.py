from flask_wtf import FlaskForm
from app.models import User, Resource
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField,HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_wtf.file import FileField, FileRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    verify_code = StringField('VerifyCode', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    verify_code = StringField('VerifyCode', validators=[DataRequired()])
    submit = SubmitField('Register')

    # self-define validator
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

class EditResForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    resfile = FileField('res file', validators=[])
    submit = SubmitField('Confirm')
    resid = HiddenField()

    def validate_price(self, price):
        try:
            p = int(price.data)
        except Exception as e:
            raise ValidationError('Please input an Integer')
        if p <= 0:
            raise ValidationError('Please input a positive Integer')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class ResIssueForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    resfile = FileField('res file', validators=[FileRequired()])
    submit = SubmitField('Confirm')

    def validate_price(self, price):
        try:
            p = int(price.data)
        except Exception as e:
            raise ValidationError('Please input an Integer')
        if p <= 0:
            raise ValidationError('Please input a positive Integer')
        

class ResTransferForm(FlaskForm):
    res_id = HiddenField()
    to = StringField('transfer to', validators=[DataRequired()], description="pls input his/her username")
    submit = SubmitField('Confirm')

    def validate_to(self, to):
        user = User.query.filter_by(username=to.data).first()
        if user is None:
            raise ValidationError('invalid user, please confirm the username')


class ChargeForm(FlaskForm):
    amount = IntegerField('charge amount', validators=[NumberRange(1, 1000), DataRequired()])
    paypwd = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('charge')



class WithdDraw(FlaskForm):
    amount = IntegerField('withdraw amount', validators=[NumberRange(1, 1000), DataRequired()])
    paypwd = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('charge')