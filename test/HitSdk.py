import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChain import HitSdk
from utils.chain.HitChain import ContractExecType
from utils.chain.config import CHAINCONFIG
import json

def test_newAccount(sdk: HitSdk):
    result = sdk.newAccount("hello")
    print(result)

def test_event(sdk: HitSdk):
    result, eventArgsInfo, err = myeth.contractSingleTransaction(
        contract_address=contract['address'],
        contract_abi=json.load(open(contract['abifile'],'r')),
        exec_func='getCharityById',
        exec_type=ContractExecType.CONTRACT_CALL,
        source_args={'from': myeth.w3.eth.accounts[0]},
        func_args=[100],
        event_names=[]
    )
    print("result: {}".format(result))
    print("eventArgsInfo: {}".format(eventArgsInfo))
    print("err: {}".format(err))

if __name__ == "__main__":
    charityConfig = CHAINCONFIG['charity']
    contract = charityConfig['contract']['charity']
    myeth = HitSdk(url=charityConfig['url'], name="node1", poa=False)
    test_newAccount(myeth)
