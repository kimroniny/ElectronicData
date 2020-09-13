"""
链上链下数据同步机制，主要是同步三个数据表：
- User
- Resource # charity project
- Cert # donate record
每个数据表一个进程进行同步
下面是每个数据表具体同步的信息:
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

"""
import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChainForCharity import CharitySdk
from app import db
from app.models import (
    User,
    Resource, # charity project
    Cert, # donate record
)
from multiprocessing import process

def sync_user():
    pass

def sync_resource():
    pass

def sync_cert():
    pass

def work():
    pass

if __name__ == "__main__":
    work()
