import sys, os
sys.path.append(os.path.abspath('.'))
from utils.chain.HitChain import HitSdk
from utils.chain.HitChain import ContractExecType
from utils.chain.config import CHAINCONFIG
import json, traceback

# TODO 在该层调整一下参数的格式问题
class CharitySdk(HitSdk):
    def __init__(self, *args, **kwargs):
        self.config = CHAINCONFIG['charity']
        self.url = self.config['url']
        super(CharitySdk, self).__init__(self.url, 'charity',*args, **kwargs)
    
    def charge(self, money, addr):
        tx = {
            'from': self.defaultAccount,
            'to': addr,
            'value': int(money)
        }
        tx_receipt, err = self.sendSingleTransaction(tx)
        if err: return False
        return True

    def registerChainAccount(self, password=''):
        """
        1. 使用 password 作为账户解锁密钥创建链上账户
        2. 将新创建的账户地址加入到 charity 合约记录中。
        3. 从事件 UserInfo 获取新创建的链上账户编号和地址 
        event UserInfo(
            uint indexed id,
            uint balance,
            address addr
        );

        Args:
            password (str, optional): [description]. Defaults to ''.

        Returns:
            dict: {'id': int, 'addr': address, 'balance': int}
        """
        try:
            addr = self.w3.geth.personal.new_account(password)
            _, eventArgsInfo, err = self.operate(
                func_name='newUser',
                func_args=[addr],
                exec_type=ContractExecType.CONTRACT_TRAN,
                args={'from': self.defaultAccount},    
                event_names=['UserInfo']        
            )
            if err: raise Exception("new account join CharityUser Failed! ERROR: {}".format(err))
            # TODO: 把对eventArgsInfo的判断进行封装
            if not eventArgsInfo.get('UserInfo', None): raise Exception("in newUser, event[UserInfo] cannot be found")
            args = eventArgsInfo['UserInfo']
            if len(args) < 1: 
                raise Exception("in registerChainAccount, obtain event args UserInfo Failed! len(args) is empty!")
            # 所有的返回值都在程序的最后emit出去，所以使用-1来索引        
            return args[-1]
        except Exception as e:
            print(traceback.format_exc())
            return {}
    
    def createCharity(self, endTime, money, infoHash, owner):
        """
        创建募捐项目，并返回项目信息
        result的结果对应字段是：
            uint id,
            uint idInUser,
            uint startTime,
            uint endTime,
            uint targetMoney,
            uint hasMoney,
            string infoHash,
            CharityType status,
            address payable owner
        """
        try:
            owner = self.w3.toChecksumAddress(owner)
            _, eventArgsInfo, err = self.operate(
                func_name='createCharity',
                func_args=[endTime, money, infoHash], # TODO: 增加文件的哈希值
                exec_type=ContractExecType.CONTRACT_TRAN,
                args={'from': owner},
                event_names=['CharityInfo']
            )
            if err: raise Exception("create charity on chain Failed! ERROR: {}".format(err))
            if not eventArgsInfo.get('CharityInfo', None): raise Exception("in newUser, event[CharityInfo] cannot be found")
            args = eventArgsInfo['CharityInfo']
            if len(args) < 1: 
                raise Exception("in createCharity, obtain event args CharityInfo Failed! len(args) is too short")
                '''
                这里还应该做一些操作。
                链上有可能已经创建项目成功，但是获取event的过程中出现了问题，那么链上项目已经启动并参与到同步机制中去了，这显然是illegal的。
                TODO：一个解决办法是给链上的Charity加个字段ack，默认为FALSE，只有链上创建项目成功并成功从event中获取charityId，才向链上发送交易，更改ack的值为True，正式开启募捐。
                '''
            # 所有的返回值都在程序的最后emit出去，所以使用-1来索引        
            return args[-1], ""
        except Exception as e:
            print(traceback.format_exc())
            return {}, str(e)

    def donate(self, charityId, value, sender):
        result = {
            'code': 0,
            'msg': {},
            'err': ""
        }
        try:
            _, eventArgsInfo, err = self.operate(
                func_name='donate',
                func_args=[charityId],
                exec_type=ContractExecType.CONTRACT_TRAN,
                args={'from': sender, 'value': value},
                event_names=['FundInfo']
            )
            if err: raise Exception("donate Failed! ERROR: {}".format(err))
            if not eventArgsInfo.get('FundInfo', None): raise Exception("in newUser, event[UseFundInforInfo] cannot be found")
            args = eventArgsInfo['FundInfo']
            if len(args) < 1: 
                raise Exception("in donate, obtain event args FundInfo Failed! len(args) is too short")
            result.update({'msg': args[-1]})
        except Exception as e:
            print(traceback.format_exc())
            result.update({'code': 101, 'err': str(e)})
        finally:
            return result
            
    def getCharityById(self, charityId):
        """根据charityId获取charity的信息
        result的结果对应字段是：
            uint indexed id,
            uint idInUser,
            uint startTime,
            uint endTime,
            uint targetMoney,
            uint hasMoney,
            string infoHash,
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
            'infoHash'
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

if __name__ == "__main__":
    charitySDK = CharitySdk()
    result = charitySDK.donate(8,100,'0x5915b5b28727C6876d157f5de344A2fc498eE6f4')
    print(result)