from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import time
from functools import wraps
import argparse
import json

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--txn", type=int, default=100)
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--url", type=str, default="http://127.0.0.1:3001")
    return parser.parse_args()

def decoratorTime(func):
    @wraps(func)
    def func_wraps(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print("{} run for about: {}".format(func.__name__, end-start))
    return func_wraps

class MyEth:
    def __init__(self, url, name="unknown{}".format(int(time.time()*1000)), poa=False):
        self.w3 =  Web3(HTTPProvider(url))
        if poa: self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    def newAccount(self, password=''):
        account = self.w3.geth.personal.new_account(password)
        print("new account: {}".format(account))
        flag = self.w3.geth.personal.unlock_account(account, '', 0)
        print("new account unlock: {}".format(flag))
        if not flag:
            raise Exception("unlock new account failed, new account: {}".format(account))
        return account

    @decoratorTime
    def sendTransactions(self, txs):
        txHashList = []
        for tx in txs:
            tx_hash = self.w3.eth.sendTransaction(tx)
            txHashList.append(tx_hash)
        print("send tx finished!")
        tx_receipts = []
        for txHash in txHashList:
            tx_receipt = self.w3.eth.waitForTransactionReceipt(txHash, timeout=100000)
            tx_receipts.append(str(dict(tx_receipt)))
        with open('{}.txt'.format(len(txs)), 'w') as f:
            f.write("\n".join(tx_receipts))
    
    @decoratorTime
    def callContract(self, contract_address, abi, values):
        contract = self.w3.eth.contract(address=contract_address, abi=abi)
        txHashList = []
        for value in values:
            tx_hash =contract.functions.store(value).transact({'from': self.defaultAccount})
            txHashList.append(tx_hash)
        print("transact value finished!")
        tx_receipts = []
        for txHash in txHashList:
            tx_receipt = self.w3.eth.waitForTransactionReceipt(txHash, timeout=100000)
            tx_receipts.append(str(dict(tx_receipt)))
        with open('contract-{}.txt'.format(len(values)), 'w') as f:
            f.write("\n".join(tx_receipts))

    @property
    def defaultAccount(self):
        if not self.w3.eth.defaultAccount:
            return self.w3.eth.accounts[0] 
        return self.w3.eth.defaultAccount

def workTransfer(handler, value:int):
    txs = [
            {'to': account, 'from': myeth.defaultAccount, 'value': x+1}
            for x in range(value)
        ]
    handler.sendTransactions(txs)

def workContract(handler: MyEth, value:int):
    contract_address = '0x35EF0C0c8385BbB4EE559FA99D7bb1704ac6810c'
    abi = json.load(open('abi/storage.abi', 'r'))
    handler.callContract(contract_address=contract_address, abi=abi, values=[x for x in range(value)])


def work(myeth:MyEth, tx_num:int, limit:int):
    tx_number = tx_num
    while tx_number <= limit:
        print("testing tx_number: {}".format(tx_number))
        # workTransfer(myeth, tx_number)
        workContract(myeth, tx_number)
        tx_number += tx_num


if __name__ == "__main__":
    args = getArgs()
    myeth = MyEth(args.url, name="node1", poa=True)
    account = myeth.newAccount()
    work(myeth, args.txn, args.limit)
    
        
