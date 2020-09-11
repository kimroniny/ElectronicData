import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChain import HitSdk
from utils.chain.HitChain import ContractExecType
from utils.chain.config import CHAINCONFIG
import json, traceback

class CharitySdk(HitSdk):
    def __init__(self, *args, **kwargs):
        self.config = CHAINCONFIG['charity']
        self.url = self.config['BLOCKCHAINURI']
        super(CharitySdk, self).__init__(*args, **kwargs)
    
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
    
    def createCharity(self, endTime, money, fileHash, owner):
        """
        先创建募捐项目
        然后从链上获取该项目的信息
        """
        try:
            owner = self.w3.toChecksumAddress(owner)
            _, eventArgsInfo, err = self.operate(
                func_name='createCharity',
                func_args=[endTime, money, fileHash], # TODO: 增加文件的哈希值
                exec_type=ContractExecType.CONTRACT_TRAN,
                args={'from': owner},
                event_names=['CharityInfo']
            )
            if err: raise Exception("create charity on chain Failed! ERROR: {}".format(err))
            args = eventArgsInfo['CharityInfo']
            if len(args) < 1: 
                raise Exception("in createCharity, obtain event args CharityInfo Failed! len(args) is too short")
                '''
                这里还应该做一些操作。
                链上有可能已经创建项目成功，但是获取event的过程中出现了问题，那么链上项目已经启动并参与到同步机制中去了，这显然是illegal的。
                TODO：一个解决办法是给链上的Charity加个字段ack，默认为FALSE，只有链上创建项目成功并成功从event中获取charityId，才向链上发送交易，更改ack的值为True，正式开启募捐。
                '''
            # 所有的返回值都在程序的最后emit出去，所以使用-1来索引        
            return args[-1]
        except Exception as e:
            print(traceback.format_exc())
            return {}

    def donate(self, charityId, value, sender):
        try:
            _, eventArgsInfo, err = self.operate(
                func_name='donate',
                func_args=charityId,
                exec_type=ContractExecType.CONTRACT_TRAN,
                args={'from': sender, 'value': value},
                event_names=['FundInfo']
            )
            if err: raise Exception("donate Failed! ERROR: {}".format(err))
            args = eventArgsInfo['FundInfo']
            if len(args) < 1: 
                raise Exception("in donate, obtain event args FundInfo Failed! len(args) is too short")
            return args[-1]
        except Exception as e:
            print(traceback.format_exc())
            return {}
            
    def getCharityById(self, charityId):
        """根据charityId获取charity的信息
        result的结果对应字段是：
            uint indexed id,
            uint idInUser,
            uint startTime,
            uint endTime,
            uint targetMoney,
            uint hasMoney,
            string fileHash,
            CharityType status,
            address payable indexed owner

        Args:
            charityId ([type]): [description]

        Raises:
            Exception: [description]
        """
        keys = [
            'id',
            'idInUser',
            'startTime',
            'endTime',
            'targetMoney',
            'hasMoney',
            'fileHash'
            'status',
            'owner',
        ]
        try:
            result, _, err = self.operate(
                func_name='getCharityById',
                func_args=[charityId],
                exec_type=ContractExecType.CONTRACT_CALL,
            )
            if err: raise Exception("getCharityById Failed! ERROR: {}".format(err))
            if len(result) != len(keys): raise Exception("getCharityById len(result) != len(keys), pls check the keys")
            return {key: val for key, val in zip(keys, result)}
        except Exception as e:
            print(traceback.format_exc())
            return {}        
    
    def getFundById(self, fundId):
        """根据 fundId 获取 fund 的信息
        result的结果对应字段是：
            uint id,
            uint charityId,
            uint idInUser,
            uint idInCharity,
            uint money,
            uint timestamp,
            address donator
        Args:
            fundId ([type]): [description]

        Raises:
            Exception: [description]
        """
        keys = [
            'id',
            'charityId',
            'idInUser',
            'idInCharity',
            'money',
            'timestamp',
            'donator',
        ]
        try:
            result, _, err = self.operate(
                func_name='getFundById',
                func_args=[fundId],
                exec_type=ContractExecType.CONTRACT_CALL,
            )
            if err: raise Exception("getFundById Failed! ERROR: {}".format(err))
            if len(result) != len(keys): raise Exception("getFundById len(result) != len(keys), pls check the keys")
            return {key: val for key, val in zip(keys, result)}
        except Exception as e:
            print(traceback.format_exc())
            return {}        

    def operate(self, func_name, func_args=[], exec_type=ContractExecType.CONTRACT_CALL, args={}, event_names=[]):
        contract_address = self.config['contract']['charity']['address']
        contract_abifile = self.config['contract']['charity']['abifile']
        result, eventArgsInfo, err = self.contractSingleTransaction(
            contract_address=contract_address,
            contract_abi=json.load(open(contract_abifile,'r')),
            exec_func=func_name,
            exec_type=exec_type,
            source_args=args,
            func_args=func_args,
            event_names=event_names
        )
        return result, eventArgsInfo, err
