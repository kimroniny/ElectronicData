import sys, os
sys.path.append(os.path.abspath('.'))
print(sys.path)
import json
from web3 import Web3, HTTPProvider
from utils.chain.config import CHAINCONFIG
charityConfig = CHAINCONFIG['charity']
url = charityConfig['url']
contract = charityConfig['contract']['charity']

w3 =  Web3(HTTPProvider(url))

defaultAccount = w3.eth.accounts[0]

for i in range(3):
    w3.geth.personal.unlockAccount(w3.eth.accounts[i], '', 0)
    print("unlock {}".format(w3.eth.accounts[i]))

contract_addr = contract['address']
contract_abi = json.load(open(contract['abifile'], 'r'))
contract = w3.eth.contract(address=contract_addr, abi=contract_abi)
print("obtain contract success!")
for i in range(3):
    addr = w3.eth.accounts[i]
    txhash = contract.functions['newUser'](addr).transact({'from': defaultAccount})
    tx_receipt = w3.eth.waitForTransactionReceipt(txhash)
    print("newUser success, {}".format(tx_receipt['blockNumber']))

# 1599872157