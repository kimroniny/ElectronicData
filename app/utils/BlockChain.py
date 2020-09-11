from web3 import Web3, HTTPProvider
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
        func(*args, **kwargs)
        end = time.time()
        print("{} run for about: {}".format(func.__name__, end-start))
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

class HitChain:
    def __init__(self, url, name="unknown{}".format(int(time.time()*1000)), poa=False):
        self.w3 =  Web3(HTTPProvider(url))
        self.contractConfig = ContractConfig()
        self.name = name
        if poa: self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    def newAccount(self, password=''):
        addr = self.w3.geth.personal.new_account(password)
        mainContractInfo = self.contractConfig.mainContractInfo
        txReceipt = self.contractSingleTransaction(
            mainContractInfo['address'],
            mainContractInfo['abi'],
            self.contractConfig.mainContractFunctions.NEWUSER,
            ContractExecType.CONTRACT_TRAN,
            {'from': self.defaultAccount},
            addr
        )
        return addr

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
        tx_hash = self.w3.eth.sendTransaction(tx)
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=100000)
        return tx_receipt
      
    @recordTime
    def contractSingleTransaction(self, contract_address, abi, exec_func, exec_type, source_args, *args, **kwargs):
        contract = self.w3.eth.contract(address=contract_address, abi=abi)
        if ContractExecType.CONTRACT_CALL == exec_type:
            result = contract.functions[exec_func](*args, **kwargs).call(source_args)
            return result
        elif ContractExecType.CONTRACT_TRAN == exec_type:
            tx_hash = contract.functions[exec_func](*args, **kwargs).transact(source_args)
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=100000)
            return tx_receipt

    @property
    def defaultAccount(self):
        if not self.w3.eth.defaultAccount:
            return self.w3.eth.accounts[0] 
        return self.w3.eth.defaultAccount


if __name__ == "__main__":
    myeth = HitChain(url='http://127.0.0.1:3001', name="node1", poa=True)
    
        
'''
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3001 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node1/data --port 30301 
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3002 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node2/data --port 30302 
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3003 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node3/data --port 30303 
'''