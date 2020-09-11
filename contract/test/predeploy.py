import json
from web3 import Web3, HTTPProvider
url = 'http://192.168.64.130:3001'
w3 =  Web3(HTTPProvider(url))

defaultAccount = w3.eth.accounts[0]

for i in range(3):
    w3.geth.personal.unlockAccount(w3.eth.accounts[i], '', 0)
    print("unlock {}".format(w3.eth.accounts[i]))

contract_addr = '0x2F0A47CE26AB5aDc63b7213AC60C8e67bFd4174f'
contract_abi = json.load(open('./contract/abi/charity.abi', 'r'))
contract = w3.eth.contract(address=contract_addr, abi=contract_abi)
print("obtain contract success!")
for i in range(3):
    addr = w3.eth.accounts[i]
    txhash = contract.functions['newUser'](addr).transact({'from': defaultAccount})
    tx_receipt = w3.eth.waitForTransactionReceipt(txhash)
    print("newUser success, {}".format(tx_receipt['blockNumber']))

# 1599872157