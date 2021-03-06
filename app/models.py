from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from Crypto.Hash import keccak
import jwt
from time import time
# from flask_sqlalchemy.utils.sqlalchemy import 


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# transfers = db.Table(
#     'transfers',
#     db.Column('transfer_id', db.Integer, db.ForeignKey('buys.id', ondelete='CASCADE')),
#     db.Column('transfee_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
# )

def getPrice(context):
    resource_id = context.get_current_parameters()['resource_id']
    return Resource.query.filter_by(id=resource_id).first().price

class Certs(db.Model):
    __tablename__ = 'certs'

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id', ondelete='CASCADE'))
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    transfer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    timestamp_pay = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timestamp_trans = db.Column(db.DateTime)
    value = db.Column(db.Integer, default=getPrice)

    def getUserOf(self, user_id):
        return User.query.filter_by(id=user_id).first_or_404()

    def format_timestamp_pay(self):
        return self.timestamp_pay.strftime('%Y-%m-%d %H:%M:%S')

    def format_timestamp_trans(self):
        return self.timestamp_trans.strftime('%Y-%m-%d %H:%M:%S')

    def transfer_to(self, userid):
        self.transfer_id = userid
        self.timestamp_trans = datetime.utcnow()

    def __repr__(self):
        return '<Certs {}: resource_id, {}; payer_id, {}; transfer_id, {}; value, {}>'.format(
            self.id, 
            self.resource_id,
            self.payer_id,
            self.transfer_id,
            self.value
            )
    
    def as_dict(self):
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'payer_id': self.transfer_id,
            'timestamp_pay': self.transtamp_pay,
            'timestamp_trans': self.transtamp_trans,
            'value': self.value
        }

    # 指明
    # payer = db.relationship('User', foreign_keys=[resource_id])
    # transfer = db.relationship('User', foreign_keys=[transfer_id])


class Resource(db.Model):
    __tablename__ = 'resource'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(200))
    price = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updatetime = db.Column(db.DateTime)
    filename = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<Resource {}>'.format(self.body)

    def avatar(self, size):
        digest = md5(self.title.encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def paid_nums(self):
        return Certs.query.filter_by(
            resource_id=self.id,
            transfer_id=None
        ).count()
        

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'desp': self.body,
            'price': self.price,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'issuer': self.issuer.username
        }


def generate_pub_key(context):
    email = context.get_current_parameters()['email']
    return keccak.new(data=email.encode(), digest_bits=256).hexdigest()

def generate_addr(context):
    email = context.get_current_parameters()['email']
    return keccak.new(data=email.encode(), digest_bits=256).hexdigest()[24:]

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Integer, default=0)
    pub_key = db.Column(db.String(64), default=generate_pub_key)
    address = db.Column(db.String(40), default=generate_addr)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    resources = db.relationship('Resource', backref='issuer', lazy='dynamic', passive_deletes=True)
    res_bought = db.relationship(
        'Resource', 
        secondary="certs",
        primaryjoin=('certs.c.payer_id == User.id'),
        secondaryjoin=('certs.c.resource_id == Resource.id'),
        backref=db.backref('payer', lazy='dynamic'), 
        lazy='dynamic', passive_deletes=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    def buy_res(self, resource):
        self.res_bought.append(resource)
    
    def obtain_cert(self, cert: Certs):
        # 首先需要添加新的购买记录
        # self.res_bought.append(Resource.query.filter_by(id=cert.resource_id).first())
        # 转让源点人的购买记录要加上转让终点人的id
        cert.transfer_to(self.id)
        # 创建新的购买记录，但是价格设为-1，代表当前凭证是转让得来的
        new_cert = Certs(resource_id=cert.resource_id, payer_id=self.id, value=-1, transfer_id=None)
        return new_cert
        
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


