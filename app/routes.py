from app import app, db, charitySDK
from app.forms import *
from app.capture import *
from app.email import send_password_reset_email
from app.models import User, Resource, Certs

from flask import render_template, flash, redirect, url_for, request, send_from_directory, abort, make_response, session
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.utils import secure_filename

from utils.chain.HitChainForCharity import CharitySdk
from utils.hash.filehash import FilesHash

from datetime import datetime
from functools import wraps
from io import BytesIO
import json
import os
import pathlib
import traceback


def checkPayPwd(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.account_password_hash == None:
            flash("0,充值、提现、捐款操作请首先创建链上账户")
            # return redirect(url_for('user', userid=current_user.id))
        # else:
        return f(*args, **kwargs)
    return wrapped


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    # resources = Resource.query.filter(
    #     ~Resource.payer.any(User.id == current_user.id)
    # ).paginate(
    #     page, app.config['POSTS_PER_PAGE'], False
    # )
    resources = Resource.query.order_by(Resource.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for(
        'index', page=resources.next_num) if resources.has_next else None
    prev_url = url_for(
        'index', page=resources.prev_num) if resources.has_prev else None
    return render_template('index.html', title='首页', resources=resources.items, next_url=next_url, prev_url=prev_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('0,验证码输入错误')
            return render_template('sign/register.html', title='Register', form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('1,注册成功')
        return redirect(url_for('login'))
    return render_template('sign/register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('0,Wrong verify code.')
            return render_template('sign/login.html', title='Sign In', form=form)
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('0,Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('sign/login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# 发布新的数据资源
@app.route('/issue', methods=['GET', 'POST'])
@login_required
def issue():
    '''
    首先计算文件的哈希值
    首先要向链上注册
    TODO 这里要发送链上账户密码进行解锁
    '''
    form = ResIssueForm()
    if form.validate_on_submit():
        sdk = charitySDK
        resfile = form.resfile.data
        infoHash = form.calcHash()
        endTime = form.formatDatetimeToTimestamp()
        money = form.formatPriceToInt()
        filename = resfile.filename
        password = form.password.data
        if not current_user.check_account_password(password):
            raise Exception("链上账户解锁密码错误")
        unlockFlag = charitySDK.unlockAccount(
            current_user.address, password=password)  # 默认解锁时间为300s
        if not unlockFlag:
            raise Exception("链上账户解锁失败")
        charityInfo, err = sdk.createCharity(
            endTime=endTime, money=money, infoHash=infoHash, owner=current_user.address)
        if not charityInfo:
            flash(message="0,"+err)
            return render_template('issue/res.html', title="issue resource", form=form)
        res = Resource(
            title=form.title.data,
            idOnChain=charityInfo['id'],
            idInUserOnChain=charityInfo['idInUser'],
            price=charityInfo['targetMoney'],
            body=form.body.data,
            endTime=datetime.fromtimestamp(charityInfo['endTime']),
            issuer=current_user,
            filename=filename,
            infoHash=charityInfo['infoHash'],
            status=charityInfo['status']
        )
        db.session.add(res)
        db.session.commit()
        filedir = os.path.join(app.config['RES_FILE_PATH'], str(res.id))
        if not pathlib.Path(filedir).exists():
            os.makedirs(filedir)
        resfile.save(
            os.path.join(
                filedir, res.filename
            )
        )
        # res.filename = url_for('resfiles', filename=os.path.join(str(res.id), filename))
        # db.session.commit()
        
        """
        TODO: 这里要写一个给区块链的ack，表示可以运行了
        然后区块链返回一个值表明项目运行成功与否
        如果区块链运行项目失败，则回滚数据库，删除保存的文件。
        """
        flash('1,成功写入区块链, 项目发布成功(*^▽^*)')
        return redirect(url_for('index'))
    return render_template('issue/res.html', title="issue resource", form=form)


# 捐款
@app.route('/res_donate', methods=['POST'])
@login_required
def res_donate():
    try:
        front_end_response = {
            'code': 0,
            'msg': 'success',
            'err': ''
        }
        if request.method == "POST":
            money, password, resid = int(
                request.form['money']), request.form['password'], int(request.form['resid'])
            if not current_user.check_account_password(password):
                raise Exception("链上账户解锁密码错误")
            unlockFlag = charitySDK.unlockAccount(
                current_user.address, password=password)  # 默认解锁时间为300s
            if not unlockFlag:
                raise Exception("链上账户解锁失败")
            resource = Resource.query.filter_by(id=resid).first()
            donateresult = charitySDK.donate(
                charityId=resource.idOnChain, value=money, sender=current_user.address)
            if donateresult['code'] != 0:
                raise Exception(donateresult['err'])
            print("donate {}ED success".format(money))
            fundInfo = donateresult['msg']
            fund_idOnChain = fundInfo['id']
            fund_charityIdOnChain = fundInfo['charityId']
            # fund_idInUserOnChain = fundInfo['idInUser'],
            # fund_idInCharityOnChain = fundInfo['idInCharity'],
            fund_value = fundInfo['money']
            fund_timestamp_pay = fundInfo['timestamp']
            fund_payer = fundInfo['donator']
            resource = Resource.query.filter_by(
                    idOnChain=fund_charityIdOnChain).first()
            cert = Certs(
                resource=resource,
                user=User.query.filter_by(address=fund_payer).first(),
                timestamp_pay=datetime.fromtimestamp(fund_timestamp_pay),
                value=fund_value,
                idOnchain=fund_idOnChain
            )
            db.session.add(cert)
            db.session.commit()
            print("donate record has been written to db")
            result, err = charitySDK.getCharityByIdOnChain(fund_charityIdOnChain)
            if err:
                raise Exception("getCharityById({}) failed, err: {}".format(
                    fund_charityIdOnChain, err))
            hasMoney = result.get('hasMoney', None)
            status = result.get('status', None)
            if hasMoney and status:
                resource.has_price = int(hasMoney)
                resource.status = int(status)
                db.session.commit()
                print("update charity status")
                # db.session.query(Resource).filter_by(idOnChain=fund_charityIdOnChain).update(
                #     {'has_price': int(hasMoney), 'status': status})
            else:
                raise Exception(
                    "charity update hasMoney and status failed, keys missing")
        else:
            raise Exception("DONATE REQUEST METHOD ERROR, only support POST")
    except Exception as e:
        front_end_response.update({'code': 101, 'msg': "error", 'err': str(e)})
        print(traceback.format_exc())
    finally:
        return json.dumps(front_end_response)


# 数据资源详情
@app.route('/res_detail/<resid>', methods=['GET'])
@login_required
def res_detail(resid):
    resource = Resource.query.filter_by(id=resid).first_or_404()
    # donated = 1 <= Certs.query.filter_by(
    #     resource_id=resid, payer_id=current_user.id).count() # 有可能捐赠多笔
    issued = resource.user_id == current_user.id
    return render_template(
        'detail/res.html',
        title='项目详情',
        res=resource,
        # bought=donated,
        issued=issued
    )


@app.route('/user/<userid>', methods=['GET', 'POST'])
@login_required
def user(userid):
    user = User.query.filter_by(id=userid).first_or_404()
    return render_template('detail/user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('1,您的修改内容已保存')
        return redirect(url_for('user', userid=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('modify/user.html', title='Edit Profile',
                           form=form)


# abandoned
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    resources = Resource.query.order_by(Resource.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        'explore', page=resources.next_num) if resources.has_next else None
    prev_url = url_for(
        'explore', page=resources.prev_num) if resources.has_prev else None
    return render_template('index.html', title='Explore', resources=resources.items, next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('0,检查您的邮箱并按照指导说明重新设置密码')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('1,密码已充值')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# abandoned
@app.route('/show_res_issue', methods=['POST'])
@login_required
def show_res_issue():
    resources = current_user.resources.order_by(
        Resource.timestamp.desc()).all()
    res = [resource.as_dict() for resource in resources]
    return json.dumps(res)


@app.route('/my_res_issue', methods=['GET', 'POST'])
@login_required
def my_res_issue():
    resources = current_user.resources.order_by(
        Resource.timestamp.desc()).all()
    return render_template(
        'myres/res_issue.html',
        resources=resources
    )


#abandoned
@app.route('/show_res_bought', methods=['POST'])
@login_required
def show_res_bought():
    result = []
    certs = Certs.query.filter(
        Certs.user_id == current_user.id, Certs.transfer_id == None
    ).order_by(Certs.timestamp_pay.desc()).all()
    for cert in certs:
        res = Resource.query.filter_by(
            id=cert.resource_id).first_or_404().as_dict()
        res.update(
            {
                'timestamp_pay': cert.format_timestamp_pay(),
                'price': cert.value
            }
        )
        result.append(res)
    return json.dumps(result)


@app.route('/my_res_donate', methods=['GET', 'POST'])
@login_required
def my_res_donate():
    result = []
    certs = Certs.query.filter(
        Certs.user_id == current_user.id
    ).order_by(Certs.timestamp_pay.desc()).all()
    
    resource_dist = set()
    for cert in certs:
        res = Resource.query.filter_by(id=cert.resource_id).first()
        result.append({
            'res':res,
            'donate_timestamp': cert.timestamp_pay,
            'donate_price': cert.value
        })
        resource_dist.add(res.id)

    allnum = len(certs)
    allnum_dist = len(resource_dist)
    return render_template(
        'myres/res_donate.html',
        resources=result,
        allnum=allnum,
        allnum_dist=allnum_dist
    )


# abandoned
@app.route('/show_res_transfer', methods=['POST'])
@login_required
def show_res_transfer():
    result = list()
    certs = Certs.query.filter(
        Certs.user_id == current_user.id, Certs.transfer_id != None
    ).order_by(Certs.timestamp_trans.desc()).all()
    for cert in certs:
        resource = Resource.query.filter_by(
            id=cert.resource_id).first_or_404().as_dict()
        resource.update(
            {
                'timestamp_pay': cert.format_timestamp_pay(),
                'timestamp_trans': cert.format_timestamp_trans(),
                'transfer_to': User.query.filter_by(id=cert.transfer_id).first().username
            }
        )
        print(resource)
        result.append(resource)
    return json.dumps(result)

@app.route('/charge', methods=['GET', 'POST'])
@login_required
@checkPayPwd
def charge():
    form = ChargeForm()
    if form.validate_on_submit():
        if not current_user.account_password_hash:
            flash('0,请先创建链上账户')
        elif current_user.check_account_password(form.paypwd.data):
            result = charitySDK.charge(
                money=form.amount.data, addr=current_user.address)
            if result:
                flash('1,充值成功，充值金额: {}ED'.format(form.amount.data))
                current_user.balance = charitySDK.getAccountBalance(current_user.address)
                db.session.commit()
            else:
                flash('0,充值失败')
        else:
            flash("0,密码错误")
    return render_template(
        'finance/charge.html',
        form=form,
        title='充值'
    )


@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
@checkPayPwd
def withdraw():
    form = WithdDraw()
    if form.validate_on_submit():
        if not current_user.account_password_hash:
            flash('0,请先创建链上账户')
        elif current_user.check_account_password(form.paypwd.data):
            result = charitySDK.withdraw(
                money=form.amount.data, addr=current_user.address, password=form.paypwd.data)
            if result == 0:
                flash('1,提现成功，提现金额: {}ED'.format(form.amount.data))
                current_user.balance = charitySDK.getAccountBalance(current_user.address)
                db.session.commit()
            elif -1 == result:
                flash("0,链上账户余额不足")
            elif -2 == result:
                flash("0,链上账户解锁失败")
            else:
                flash('0,提现失败')
        else:
            flash('0,密码错误')
    return render_template(
        'finance/withdraw.html',
        form=form,
        title='withdraw'
    )


# abandoned
@app.route('/download/<resid>', methods=['GET'])
@app.route('/download/<resid>/<filename>', methods=['GET'])
@login_required
def download_res(resid, filename=None):
    if not filename:
        flash('0,没有可以下载的文件')
        return redirect(
            url_for('res_detail', resid=resid)
        )
    if resid:
        if Resource.query.filter_by(id=resid, filename=filename).count() == 1:
            return send_from_directory(
                os.path.join(app.config['RES_FILE_PATH'], str(resid)),
                filename,
                as_attachment=True
            )
    abort(404)


@app.route('/trace_donate/<resid>', methods=['GET', 'POST'])
@login_required
def trace_donate(resid):
    resource = Resource.query.filter(Resource.id==resid).first_or_404()
    certs = Certs.query.filter(Certs.resource_id == resid).order_by(Certs.timestamp_pay.desc()).all()
    result = []
    for cert in certs:
        result.append({
            'userid': cert.user.id,
            'address': cert.user.address,
            'timestamp': cert.timestamp_pay,
            'value': cert.value
        })
    donatee_address = resource.issuer.address
    return render_template(
        'trace/trace.html',
        title=resource.title,
        res_title=resource.title,
        donatee=donatee_address,
        result=result,
        enumerate=enumerate,
    )


@app.route('/code')
def get_capture_code():
    image, code = get_verify_code()
    # 图片以二进制形式写入
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把buf_str作为response返回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = code
    return response


@app.route('/registechain', methods=['GET', 'POST'])
def register_chain_account():
    form = RegisteChainAccountForm()
    if form.validate_on_submit():
        account_password = form.account_password.data
        print("====================={}".format(account_password))
        result = charitySDK.registerChainAccount(account_password)
        if not result:
            flash("0,创建链上账户失败")
        else:
            idOnChain, address = result['id'], result['addr']
            current_user.idOnChain = idOnChain
            current_user.address = address
            current_user.set_account_password(account_password)
            db.session.commit()
            flash("1,创建链上账户成功(*^▽^*)，链上账户地址可在个人信息中查看")
            return redirect(url_for('index'))
    return render_template(
        'sign/registe_chain.html',
        form=form,
        title="注册链上账户"
    )
