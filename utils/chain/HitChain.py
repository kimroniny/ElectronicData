from web3 import Web3, HTTPProvider
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.middleware import geth_poa_middleware
import time
from functools import wraps
import argparse
import json, traceback
from enum import Enum, unique


def recordTime(func):
    @wraps(func)
    def func_wraps(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("{} run for about: {}".format(func.__name__, end-start))
        return result
    return func_wraps

@unique
class ContractExecType(Enum):
    CONTRACT_CALL = 0
    CONTRACT_TRAN = 1

class ContractFunction:
    NEWUSER = 'newUser'

class ContractConfig:

    @property
    def mainContractInfo(self):
        return {
            'address': "",
            'abi': {}
        }

    @property
    def mainContractFunctions(self):
        return ContractFunction()

class HitSdk:
    def __init__(self, url, name="unknown{}".format(int(time.time()*1000)), poa=False):
        self.w3 =  Web3(HTTPProvider(url))
        self.contractConfig = ContractConfig()
        self.name = name
        if poa: self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    

    def unlockAccount(self, account, password=""):
        try:
            flag = self.w3.geth.personal.unlock_account(account, '', 0)
            if not flag:
                raise Exception("unlock new account failed, new account: {}".format(account))
        except Exception as e:
            print(traceback.format_exc())
            return False
        return True
    
    def sendSingleTransaction(self, tx):
        try:
            tx_hash = self.w3.eth.sendTransaction(tx)
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=100000)
            return tx_receipt, ""
        except Exception as e:
            print(traceback.format_exc())
            return "", str(e)
      
    def parseEvent(self, contract, tx_receipt, event_names):
        eventArgsInfo = {}
        try:
            if event_names:
                for eventName in event_names:
                    myevents = contract.events[eventName]().processReceipt(txn_receipt=tx_receipt, errors=IGNORE)
                    eventArgsInfo[eventName] = [dict(myevent['args']) for myevent in myevents]
        except Exception as e:
            print(traceback.format_exc())
        return eventArgsInfo

    @recordTime
    def contractSingleTransaction(self, contract_address, contract_abi, exec_func, func_args=[], exec_type=ContractExecType.CONTRACT_CALL, source_args={}, event_names=[]):
        """执行合约交易

        Args:
            contract_address (str): 合约地址
            contract_abi (dict): 合约abi字典
            exec_func (str): 需要执行的函数
            func_args (list, optional): 需要执行的函数的参数列表. Defaults to [].
            exec_type (int, optional): 合约执行的类型 transact() 或者 call(). Defaults to ContractExecType.CONTRACT_CALL.
            source_args (dict, optional): 合约执行的参数字典，就是 transact() 和 call() 的参数. Defaults to {}.
            event_name (list, optional): 事件名称列表. Defaults to [].

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
            result: 
            eventArgsInfo: dict
            err: str
        """
        try:
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
            if ContractExecType.CONTRACT_CALL == exec_type:
                result = contract.functions[exec_func](*func_args).call(source_args)
                return result, {}, ""
            elif ContractExecType.CONTRACT_TRAN == exec_type:
                tx_hash = contract.functions[exec_func](*func_args).transact(source_args)
                tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=100000)
                eventArgsInfo = self.parseEvent(contract=contract, tx_receipt=tx_receipt, event_names=event_names)
                return tx_receipt, eventArgsInfo, ""
            else:
                raise Exception("unknown execution type")
        except Exception as e:
            print(traceback.format_exc())
            return "", {}, str(e)

    @property
    def defaultAccount(self):
        if not self.w3.eth.defaultAccount:
            return self.w3.eth.accounts[0] 
        return self.w3.eth.defaultAccount

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath('.'))
    from utils.chain.config import CHAINCONFIG
    charityConfig = CHAINCONFIG['charity']
    contract = charityConfig['contract']['charity']
    myeth = HitSdk(url=charityConfig['url'], name="node1", poa=True)

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
    
        
'''
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3001 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node1/data --port 30301 
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3002 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node2/data --port 30302 
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3003 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node3/data --port 30303 
'''