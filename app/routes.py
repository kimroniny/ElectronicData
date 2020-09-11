from app import app, db
from app.forms import *
from app.capture import *
from app.email import send_password_reset_email
from app.models import User, Resource, Certs

from flask import render_template, flash, redirect, url_for, request, send_from_directory, abort, make_response, session
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.utils import secure_filename

from datetime import datetime
from functools import wraps
from io import BytesIO
import json, os, pathlib


def checkPayPwd(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.password_hash == None:
            flash("0,请完善支付密码")
            return redirect('user', userid=current_user.id)
        else:
            return f(*args, **kwargs)
    return wrapped


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
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


# 发布新的数据资源
@app.route('/issue', methods=['GET', 'POST'])
@login_required
def issue():
    form = ResIssueForm()
    if form.validate_on_submit():
        resfile = form.resfile.data
        filename = resfile.filename
        res = Resource(
            title=form.title.data,
            price=form.price.data,
            body=form.body.data,
            endTime=form.endTime.data,
            issuer=current_user,
            filename=filename
        )
        db.session.add(res)
        db.session.commit()
        filedir = os.path.join(app.config['RES_FILE_PATH'], str(res.id))
        if not pathlib.Path(filedir).exists():
            os.makedirs(filedir)
        resfile.save(
            os.path.join(
                app.config['RES_FILE_PATH'], str(res.id), res.filename
            )
        )
        flash('1,发布成功！！！资源已上架！')
        return redirect(url_for('index'))
    return render_template('issue/res.html', title="issue resource", form=form)

# 转让
@app.route('/res_transfer', methods=['POST'])
@login_required
def res_transfer():
    result = {
        'code': 0,
        'msg': '',
    }
    if request.method == "POST":
        username, password, resid = request.form['username'], request.form['password'], request.form['resid']
        user = User.query.filter_by(username=username).first()
        if not user:
            result['code'] = 1
            result['msg'] = 'transfer user "{}" not exists'.format(username)
        else:
            if not current_user.check_password(password):
                result['code'] = 1
                result['msg'] = 'password is wrong'.format(username)
            else:
                cert = Certs.query.filter_by(
                    resource_id=resid,
                    payer_id=current_user.id,
                    transfer_id=None).first()
                if not cert:
                    result['code'] = 1
                    result['msg'] = 'you don`t have this resource'
                else:
                    to_cert = Certs.query.filter_by(
                        resource_id=resid,
                        payer_id=user.id,
                        transfer_id=None
                    ).first()
                    if to_cert:
                        # if the to_user have the data, you cannot transfer this res to him/her
                        result['code'] = 1
                        result['msg'] = '用户 "{}" 已经拥有该数据，所以不能再转让给TA'.format(
                            username)
                    else:
                        new_cert = user.obtain_cert(cert)
                        db.session.add(new_cert)
                        db.session.commit()
                        result['msg'] = '资源转让成功 !!!'

    return json.dumps(result)

# 捐款
@app.route('/res_donate', methods=['POST'])
@login_required
def res_donate():
    result = {
        'code': 0,
        'msg': 'success',
    }
    if request.method == "POST":
        money, password, resid = request.form['money'], request.form['password'], request.form['resid']
        '''
        这里是不是可以调用合约了
        '''
    else:
        result['code'] = 101
        result['msg'] = "REQUEST METHOD ERROR, only support POST"

    return json.dumps(result)


# 购买资源
@app.route('/res_buy/<resid>', methods=['GET', 'POST'])
@login_required
def res_buy(resid):
    resource = Resource.query.filter_by(id=resid).first_or_404()
    if resource:
        if resource.price > current_user.balance:
            flash('0,您的余额不足 !!!')
        else:
            current_user.buy_res(resource)
            db.session.commit()
            flash('1,购买成功，您已经成功购买该资源')
    return redirect(url_for('res_detail', resid=resid))

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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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


@app.route('/edit_res/<resid>', methods=['GET', 'POST'])
@login_required
def edit_res(resid=None):
    form = EditResForm()
    if form.validate_on_submit():
        res = current_user.resources.filter_by(
            id=form.resid.data).first_or_404()
        res.title = form.title.data
        res.body = form.body.data
        res.price = form.price.data
        res.updatetime = datetime.utcnow()
        if form.resfile.data is not None:
            resfile = form.resfile.data
            res.filename = resfile.filename
        db.session.commit()
        if form.resfile.data is not None:
            filedir = os.path.join(app.config['RES_FILE_PATH'], str(res.id))
            if not pathlib.Path(filedir).exists():
                os.makedirs(filedir)
            resfile.save(
                os.path.join(
                    app.config['RES_FILE_PATH'], str(res.id), res.filename
                )
            )
        flash("1,资源信息已修改!!!")
        return redirect(url_for('res_detail', resid=res.id))
    elif request.method == 'GET':
        res = current_user.resources.filter_by(id=resid).first_or_404()
        form.resid.data = resid
        form.title.data = res.title
        form.body.data = res.body
        form.price.data = res.price
    return render_template(
        'modify/res.html',
        title='edit resource',
        form=form
    )


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


@app.route('/show_res_issue', methods=['POST'])
@login_required
def show_res_issue():
    resources = current_user.resources.order_by(Resource.timestamp.desc()).all()
    res = [resource.as_dict() for resource in resources]
    return json.dumps(res)


@app.route('/my_res_issue', methods=['GET', 'POST'])
@login_required
def my_res_issue():
    resources = current_user.resources.order_by(Resource.timestamp.desc()).all()
    return render_template(
        'myres/res_issue.html',
        resources=resources
    )


@app.route('/show_res_bought', methods=['POST'])
@login_required
def show_res_bought():
    result = []
    certs = Certs.query.filter(
        Certs.payer_id == current_user.id, Certs.transfer_id == None
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
        Certs.payer_id == current_user.id
    ).order_by(Certs.timestamp_pay.desc()).all()
    for cert in certs:
        res = Resource.query.filter_by(id=cert.resource_id).first()
        res.donate_timestamp = cert.timestamp_pay
        res.donate_price = cert.value
        result.append(res)
    return render_template(
        'myres/res_donate.html',
        resources=result
    )


@app.route('/show_res_transfer', methods=['POST'])
@login_required
def show_res_transfer():
    result = list()
    certs = Certs.query.filter(
        Certs.payer_id == current_user.id, Certs.transfer_id != None
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


@app.route('/page_res_transfer', methods=['GET', 'POST'])
@login_required
def page_res_transfer():
    result = list()
    certs = Certs.query.filter(
        Certs.payer_id == current_user.id, Certs.transfer_id != None
    ).order_by(Certs.timestamp_trans.desc()).all()
    for cert in certs:
        resource = Resource.query.filter_by(id=cert.resource_id).first_or_404()
        resource.pay_timestamp = cert.format_timestamp_pay()
        resource.pay_timestamp_trans = cert.format_timestamp_trans()
        resource.pay_transfer_to = User.query.filter_by(
            id=cert.transfer_id).first()
        result.append(resource)
    return render_template(
        'myres/res_transfer.html',
        resources=result
    )


@app.route('/charge', methods=['GET', 'POST'])
@login_required
@checkPayPwd
def charge():
    form = ChargeForm()
    if form.validate_on_submit():
        if current_user.check_password(form.paypwd.data):
            current_user.balance += int(form.amount.data)
            db.session.commit()
            flash('1,充值 {} 成功'.format(form.amount.data))
        else:
            flash("0,密码错误")
    return render_template(
        'finance/charge.html',
        form=form,
        title='charge'
    )


@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
@checkPayPwd
def withdraw():
    form = WithdDraw()
    if form.validate_on_submit():
        if current_user.check_password(form.paypwd.data):
            if current_user.balance >= int(form.amount.data):
                current_user.balance -= int(form.amount.data)
                db.session.commit()
                flash('1,提现 {} 成功'.format(form.amount.data))
            else:
                flash('0,余额不足以提现 {}'.format(
                    form.amount.data))
        else:
            flash("0,密码错误")
    return render_template(
        'finance/withdraw.html',
        form=form,
        title='withdraw'
    )

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
    certs = Certs.query.filter(Certs.resource_id==resid).all()
    result = []
    for cert in certs:
        payer = User.query.filter_by(id==cert.payer_id).first();
        result.append(
            {
                'time': cert.timestamp_pay,
                'payer': payer if payer is not None else "illegal user",
                'receiver': current_user,
                'value': cert.value
            }
        )
    return render_template(
        'trace/trace.html',
        title='trace_record',
        res_title = Resource.query.filter_by(id=resid).first().title,
        result=result,
        enumerate=enumerate,
        userid=current_user.id,
        resid=resid
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