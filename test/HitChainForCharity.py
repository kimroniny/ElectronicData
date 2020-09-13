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
    addr='0x61bafb097147005d0057b1e578105dbfe341d49a'
    result = sdk.charge(money=10000, addr=addr)
    print(result)
    print(sdk.getAccountBalance(addr))

def test_withdraw(sdk: CharitySdk):
    addr = '0x61bafb097147005d0057b1e578105dbfe341d49a'
    test_charge(sdk)
    print(sdk.getAccountBalance(addr))
    result = sdk.withdraw(money=500, addr=addr, password='123456')
    print(result)
    print(sdk.getAccountBalance(addr))


if __name__ == "__main__":
    myeth = CharitySdk()
    # test_registerChainAccount(myeth)
    # test_charge(myeth)
    test_withdraw(myeth)