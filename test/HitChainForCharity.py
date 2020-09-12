import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChainForCharity import CharitySdk
from utils.chain.HitChain import ContractExecType
from utils.chain.config import CHAINCONFIG
import json

def test_registerChainAccount(sdk: CharitySdk):
    result = sdk.registerChainAccount("hello")
    print(result)

if __name__ == "__main__":
    myeth = CharitySdk()
    test_registerChainAccount(myeth)
