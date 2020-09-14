"""
环境部署：
1. 清除、创建数据库，创建数据表
2. 编译、发布合约，获取合约abi和合约地址
"""
from app import db
from app.models import User, Resource, Certs
from app import charitySDK

import os
import shutil

def prepare_db():
    migrations_file = os.path.abspath('./migrations')
    if os.path.exists(migrations_file):
        shutil.rmtree(migrations_file)
        print("删除migrations文件夹, {}".format(migrations_file))
    resfiles_file = os.path.abspath('./app/static/resfiles')
    if os.path.exists(resfiles_file):
        shutil.rmtree(resfiles_file)
        print("删除募捐项目文件夹, {}".format(resfiles_file))
    os.makedirs(resfiles_file)
    db.drop_all()
    print("删除原数据库")
    db.create_all()
    print("创建新数据库")

def prepare_contract():
    contract_file = './contract/Charity.sol'
    if not os.path.exists(contract_file): raise Exception("sol file '{}' not exits".format(contract_file))
    addr, abistr, err = charitySDK.compileAndDeploy(contractfile=contract_file)
    if err: raise Exception("charitySDK.compileAndDeploy error: {}".format(err))
    with open('./contract/address', 'w') as f:
        f.write(addr)
    with open('./contract/abi/Charity.abi', 'w') as f:
        f.write(abistr)


def worker():
    prepare_db()
    prepare_contract()

if __name__ == "__main__":
    worker()