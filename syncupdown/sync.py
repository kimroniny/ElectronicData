"""
链上链下数据同步机制，主要有两个功能：检测，同步

1. 同步的话是同步三个数据表：
- User # 这个同步的意义不大，因为创建链上账户之后直接就进行了账户地址的更新
- Resource # charity project
- Cert # donate record
每个数据表一个进程进行同步

2. 检测的话是也是这三个数据表的信息。

同步前先检测某些内容是否发生变化。

下面是每个数据表具体同步和检测的信息:
User:{
    '',
    '',
    '',
    '',
    '',
}
Resource:{
    '',
    '',
    '',
    '',
    '',
}
Cert:{
    '',
    '',
    '',
    '',
    '',
}

突然感觉同步的意义并不大，因为在创建链上内容之后，可以直接根据返回的信息同步数据库内容。
或者说需要同步六个块以前的交易，那这样的话就太复杂了。。。但是可以想一想

"""
import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChainForCharity import CharitySdk
from app import (
    db,
    charitySDK
)
from app.models import (
    User,
    Resource, # charity project
    Certs, # donate record
    StatusOnChain
)
from multiprocessing import Process
import time, datetime
import argparse
import traceback

def sync_user(time_interval):
    """从数据库中读取 user 的链上账户id，然后获取其链上 address 进行检测
    检测成功则更新 user.balance
    否则则更新当前 user 的状态为非法态
    """
    error_num = 0
    while True:
        users = User.query.all()
        try:
            for user in users:
                idOnChain = user.idOnChain
                address = user.address
                addressOnChain = charitySDK.getUserByIdOnChain(idOnChain)
                if address != addressOnChain:
                    user.statusOnChain = StatusOnChain.INVALID
                    db.session.commit()
                    print("find invalid account, user: {}".format(str(user)))
                else:
                    balance = charitySDK.getAccountBalance(address)
                    if balance != user.balance:
                        user.balance = balance
                        user.updatetime = datetime.datetime.now()
                        db.session.commit()
                        print("sync user: {}".format(str(user)))
        except Exception as e:
            print(traceback.format_exc())
            error_num += 1
            if error_num > 3:
                print("sync_user error num > 3, exit!!!")
                return
            
        time.sleep(time_interval)   
            

def sync_resource(time_interval):
    """从链上依次获取数据，并根据链上募捐项目的idOnChain来获取链下数据库中的对应内容。
    如果在链下数据库中找不到，暂时不做处理~（未来可以考虑将链上募捐项目进行销毁，并将捐款返还给原账户，或者把文件信息也同步过去，然后这样就可以直接插入到数据库中）
    如果可以找到，则比对 infoHash，并更新 has_price, status, updatetime
    
    Args:
        time_interval ([type]): [description]
    """
    idx = 0
    error_num = 0
    while True:
        try:
            allnum, err = charitySDK.getCharityNum()
            if err != "": raise Exception("getCharityNum err: {}".format(err))
            if idx >= allnum:
                idx = 0
                continue
            info = charitySDK.getCharityByIdOnChain(idx)
            resources = Resource.query.filter_by(idOnChain=info['id']).all()
            if len(resources) > 1:
                for res in resources:
                    res.statusOnChain = StatusOnChain.INVALID
                    print("find invalid(too many) resource: {}".format(str(res)))
                db.session.commit()                
            elif len(resources) == 0:
                # 暂时不做处理
                pass
            else:
                res = resources[0]
                if info['infoHash'] != res.infoHash:
                    res.statusOnChain = StatusOnChain.INVALID
                    print("find invalid(infoHash is not equal) resource: {}".format(str(res)))
                    db.session.commit()
                else:
                    has_money, status = info['has_money'], info['status']
                    if res.has_price != has_money or res.status != status:
                        res.has_price = info['has_money']
                        res.status = info['status']
                        res.updatetime = datetime.datetime.now()
                        db.session.commit()
                        print("sycn resource: {}".format(str(res)))
        except Exception as e:
            print(traceback.format_exc())
            error_num += 1
            if error_num > 3:
                print("sync_resource error num > 3, exit!!!")
                return
        finally:
            idx += 1
            time.sleep(time_interval)

def sync_cert(time_interval):
    """
    根据链上funds的idOnChain来链下数据库中获取certs, 然后比对
    1. 创建者
    2. 捐赠者
    3. 捐款金额
    如果不一样就更新
    Args:
        time_interval ([type]): [description]
    """
    error_num = 0
    idx = 0
    while True:
        try:
            allnum, err = charitySDK.getFundNum()
            if err != "": raise Exception()
            if idx >= allnum:
                idx = 0
                continue
            info = charitySDK.getFundByIdOnChain(idx)
            res = Resource.query.filter_by(idOnChain=info['charityId']).first()
            user = User.query.filter_by(address=info['donator']).first()
            certs = Certs.query.filter_by(idOnChain=info['id']).all()
            if len(certs) > 1:
                for cert in certs:
                    cert.statusOnChain = StatusOnChain.INVALID
                    print("find invalid(too many) certs: {}".format(str(cert)))
                db.session.commit()                
            elif len(certs) == 0:

                
                cert = Certs(
                    resource=res,
                    user=user,
                    timestamp_pay=info['timestamp'],
                    value=info['money'],
                    idOnChain=info['id'],
                    updatetime=datetime.datetime.now(),
                )
                db.session.add(cert)
                db.session.commit()
                
            else:
                cert = certs[0]
                if info['infoHash'] != res.infoHash:
                    res.statusOnChain = StatusOnChain.INVALID
                    print("find invalid(infoHash is not equal) resource: {}".format(str(res)))
                    db.session.commit()
                else:
                    """
                    'id': self.id,
                    'resource_id': self.resource_id,
                    'user_id': self.user_id,
                    'timestamp_pay': self.timestamp_pay,
                    'value': self.value,
                    'idOnChain': self.idOnchain,
                    'updatetime': self.updatetime,
                    'statusOnChain': self.statusOnChain

                    fund.id, 
                    fund.charityId,
                    fund.idInUser,
                    fund.idInCharity,
                    fund.money,
                    fund.timestamp,
                    fund.donator
                    """
                    if not (cert.user_id == user.id and cert.resource_id == res.id and cert.timestamp_pay == info['timestamp'] and cert.value == info['money']):
                        cert.user = user
                        cert.resource = res
                        cert.timestamp_pay = info['timestamp']
                        cert.value = info['money']
                        cert.updatetime = datetime.datetime.now()
                        cert.statusOnChain = StatusOnChain.VALID
                        db.session.commit()
                        print("sycn cert: {}".format(str(cert)))
        except Exception as e:
            print(traceback.format_exc())
            error_num += 1
            if error_num > 3:
                print("sync_certs error num > 3, exit!!!")
                return
        finally:
            idx += 1
            time.sleep(time_interval)
    pass

def work(interval):
    process_user = Process(target=sync_user, args=(interval, ))
    process_resource = Process(target=sync_resource, args=(interval, ))
    process_cert = Process(target=sync_cert, args=(interval, ))
    processes = [
        process_user,
        process_resource,
        process_cert
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

def getArgs():
    time.sleep()
    parser = argparse.ArgumentParser()
    parser.add_argument('itv', type=float, default=0.5, help="sync time interval")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs
    work(args.itv)
