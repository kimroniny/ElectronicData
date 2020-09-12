import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChainForCharity import CharitySdk
from utils.chain.HitChain import ContractExecType
from utils.chain.config import CHAINCONFIG
import json

def test_registerChainAccount(sdk: CharitySdk):
    result = sdk.registerChainAccount("hello")
    print(result)

def test_charge(sdk: CharitySdk):
    result = sdk.charge(money=10000, addr='0x5915b5b28727C6876d157f5de344A2fc498eE6f4')
    print(result)

if __name__ == "__main__":
    myeth = CharitySdk()
    # test_registerChainAccount(myeth)
    test_charge(myeth)
