from flask_wtf import FlaskForm
from app.models import User, Resource
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField,HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_wtf.file import FileField, FileRequired


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    verify_code = StringField('验证码', validators=[DataRequired()])
    remember_me = BooleanField('记住账户')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '重置密码', validators=[DataRequired(), EqualTo('password')])
    verify_code = StringField('验证码', validators=[DataRequired()])
    submit = SubmitField('注册')

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
    username = StringField('用户名', validators=[DataRequired()])
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    submit = SubmitField('提交')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EditResForm(FlaskForm):
    title = StringField('题目', validators=[DataRequired()])
    body = TextAreaField('描述', validators=[DataRequired()])
    price = IntegerField('价格', validators=[DataRequired()])
    resfile = FileField('资源文件', validators=[])
    submit = SubmitField('确认')
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
    title = StringField('题目', validators=[DataRequired()])
    body = TextAreaField('描述', validators=[DataRequired()])
    price = IntegerField('价格', validators=[DataRequired()])
    resfile = FileField('资源文件', validators=[FileRequired()])
    submit = SubmitField('确定提交')

    def validate_price(self, price):
        try:
            p = int(price.data)
        except Exception as e:
            raise ValidationError('Please input an Integer')
        if p <= 0:
            raise ValidationError('Please input a positive Integer')
        

class ResTransferForm(FlaskForm):
    res_id = HiddenField()
    to = StringField('转让给', validators=[DataRequired()], description="pls input his/her username")
    submit = SubmitField('确认')

    def validate_to(self, to):
        user = User.query.filter_by(username=to.data).first()
        if user is None:
            raise ValidationError('用户名无效，请确认是否输入正确')


class ChargeForm(FlaskForm):
    amount = IntegerField('充值金额', validators=[NumberRange(1, 1000), DataRequired()])
    paypwd = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('充值')



class WithdDraw(FlaskForm):
    amount = IntegerField('提现金额', validators=[NumberRange(1, 1000), DataRequired()])
    paypwd = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('提现')