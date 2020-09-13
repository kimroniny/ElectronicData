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
    Cert, # donate record
)
from multiprocessing import process

def sync_user():
    charitySDK.get

def sync_resource():
    pass

def sync_cert():
    pass

def work():
    pass

if __name__ == "__main__":
    work()
