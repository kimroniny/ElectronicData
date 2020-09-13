from flask_wtf import FlaskForm
from app.models import User, Resource
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField,HiddenField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_wtf.file import FileField, FileRequired
import datetime
from utils.hash.filehash import FilesHash

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
    title = StringField('标题', validators=[DataRequired()])
    body = TextAreaField('详细描述', validators=[DataRequired()])
    price = IntegerField('目标金额', validators=[DataRequired()])
    endTime = DateTimeField('截止时间', validators=[DataRequired()])
    resfile = FileField('证明文件', validators=[])
    submit = SubmitField('确认')
    resid = HiddenField()

    def validate_price(self, price):
        try:
            p = int(price.data)
        except Exception as e:
            raise ValidationError('Please input an Integer')
        if p <= 0:
            raise ValidationError('Please input a positive Integer')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class ResIssueForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    body = TextAreaField('详细描述', validators=[DataRequired()])
    price = IntegerField('募捐金额', validators=[DataRequired()])
    endTime = DateTimeField('截止时间', validators=[DataRequired()], format="%Y/%m/%d %H:%M")
    resfile = FileField('证明文件', validators=[FileRequired()])
    submit = SubmitField('确定提交')

    def validate_price(self, price):
        try:
            p = int(price.data)
        except Exception as e:
            raise ValidationError('Please input an Integer')
        if p <= 0:
            raise ValidationError('Please input a positive Integer')

    def formatDatetimeToTimestamp(self):
        return int(datetime.datetime.timestamp(self.endTime.data)) # endTime.data 是一个 datetime 类型
    
    def formatPriceToInt(self):
        return int(self.price.data)

    def calcHash(self):
        """
        TODO: 实现文件的hash值
        """
        filehash = FilesHash()
        infoHash = filehash.calcHashForStr(self.title, self.body, self.price, self.endTime)
        return infoHash

class RegisteChainAccountForm(FlaskForm):
    account_password = PasswordField("链上账户密码", validators=[DataRequired()])
    account_password2 = PasswordField("确认链上账户密码", validators=[DataRequired(), EqualTo('account_password')])
    submit = SubmitField("确认创建")


class ResTransferForm(FlaskForm):
    res_id = HiddenField()
    to = StringField('转让给', validators=[DataRequired()], description="pls input his/her username")
    submit = SubmitField('确认')

    def validate_to(self, to):
        user = User.query.filter_by(username=to.data).first()
        if user is None:
            raise ValidationError('用户名无效，请确认是否输入正确')
    

class ResDonateForm(FlaskForm):
    """
    捐款表单
    """
    res_id = HiddenField()
    money = IntegerField("捐款金额(ED)", validators=[DataRequired()])
    submit = SubmitField("确认转账")

class ChargeForm(FlaskForm):
    amount = IntegerField('充值金额(ED)', validators=[NumberRange(1, 1000000), DataRequired()])
    paypwd = PasswordField('链上账户密码', validators=[DataRequired()])
    submit = SubmitField('充值')

class WithdDraw(FlaskForm):
    amount = IntegerField('提现金额', validators=[NumberRange(1, 1000), DataRequired()])
    paypwd = PasswordField('链上账户密码', validators=[DataRequired()])
    submit = SubmitField('提现')