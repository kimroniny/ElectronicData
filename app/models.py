from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from Crypto.Hash import keccak
import jwt
from time import time
from utils.chain.HitChain import ContractExecType

"""
User(1)     ->  Resource(N)     By User.id          -> issue
Resource(1) ->  Certs(N)        By Resource.id      -> have/donated
User(1)     ->  Certs(N)        By User.id          -> have/donate
"""

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
    """
    TODO
    用户或者募捐项目被删除，要不要把对应的捐款记录也删除掉呢？
    目前暂时按照"删除"来处理，但是TMD不起效果！！！
    """
    __tablename__ = 'certs'

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id', ondelete='CASCADE')) # 募捐项目的id
    # resource = db.relationship('Resource', backref=db.backref('certs', passive_deletes='all'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')) # 捐款人用户的id
    # user = db.relationship('User', backref=db.backref('certs', passive_deletes='all'))
    timestamp_pay = db.Column(db.DateTime, index=True, default=datetime.utcnow) # 捐款时间
    value = db.Column(db.Integer, default=0) # 捐款金额
    idOnchain = db.Column(db.Integer)

    # def format_timestamp_pay(self):
    #     return self.timestamp_pay.strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        return '<Certs {}: resource_id, {}; user_id, {}; value, {}; time: {}>'.format(
            self.id, 
            self.resource_id,
            self.user_id,
            self.value,
            self.timestamp_pay
            )
    
    def as_dict(self):
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'timestamp_pay': self.transtamp_pay,
            'value': self.value
        }


from enum import Enum
class ResourceStatus(Enum):
    """要和合约charity.sol里的募捐项目状态对应

    Args:
        Enum ([type]): [description]
    """
    WAIT = 0
    PENDING = 1
    FINISH = 2
class Resource(db.Model):
    __tablename__ = 'resource'
    id = db.Column(db.Integer, primary_key=True, )
    title = db.Column(db.String(60))
    body = db.Column(db.String(200))
    idOnChain = db.Column(db.Integer, index=True, unique=True)
    idInUserOnChain = db.Column(db.Integer, default=-1)
    price = db.Column(db.Integer, default=1)
    has_price = db.Column(db.Integer, default=0)
    endTime = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updatetime = db.Column(db.DateTime)
    filename = db.Column(db.String(100))
    infoHash = db.Column(db.String(100))
    status = db.Column(db.Integer, default=ResourceStatus.WAIT.value)
    certs = db.relationship('Certs', backref='resource', lazy='dynamic', passive_deletes=True, cascade="all, delete-orphan")
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
        ).count()
            
    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'desp': self.body,
            'price': self.price,
            'endTime': self.endTime,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'issuer': self.issuer.username
        }


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Integer, default=0)
    # pub_key = db.Column(db.String(64), default=generate_pub_key) # 貌似乎以太坊没法获取公钥
    idOnChain = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(42), unique=True)
    account_password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    resources = db.relationship('Resource', backref='issuer', lazy='dynamic', passive_deletes=True,cascade="all, delete-orphan",)
    certs = db.relationship('Certs', backref='user', lazy='dynamic', passive_deletes=True,cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_account_password(self, account_password):
        self.account_password_hash = generate_password_hash(account_password)

    def check_account_password(self, account_password):
        return check_password_hash(self.account_password_hash, account_password)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
        
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

    @staticmethod
    def getIdByAddress(address):
        user = User.query.filter_by(address=address).first()
        return user['id']

    

    def __repr__(self):
        return '<User {}>'.format(self.username)


