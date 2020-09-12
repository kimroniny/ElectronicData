// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.7.0;

contract Electronic {

    enum CharityType {WAIT, PENDING, FINISH}

    address[] userAddrs;

    struct Charity {
        uint id;
        uint idInUser;
        uint startTime;
        uint endTime;
        uint targetMoney;
        uint hasMoney;
        string infoHash;
        CharityType status;
        address payable owner;
    }
    Charity[] public charities;
    mapping (address => Charity[]) public charitiesOfUser;


    struct Fund {
        uint id;
        uint charityId;
        uint idInUser;
        uint idInCharity;
        uint money;
        uint timestamp;
        address donator;        
    }
    Fund[] public funds;
    mapping (address => Fund[]) public fundsOfUser;
    mapping (uint => Fund[]) public fundsOfCharity;


    function checkUser(address _addr) view internal returns (bool) {
        for (uint i = 0; i < userAddrs.length; i++){
            if (userAddrs[i] == _addr) return true;
        }
        return false;
    }

    modifier userExist(address _addr) {
        require(checkUser(_addr), "this user addr not exists");
        _;
    }

    modifier userNotExist(address _addr) {
        require(!checkUser(_addr), "this user addr has existed");
        _;
    }

    function newUser(address _addr) userNotExist(_addr) public {
        userAddrs.push(_addr);
    }

    function getUserNumber() view public returns (uint) {
        return userAddrs.length;
    }

    event CharityInfo(
        uint indexed id,
        uint idInUser,
        uint startTime,
        uint endTime,
        uint targetMoney,
        uint hasMoney,
        string infoHash,
        CharityType status,
        address payable indexed owner
    );
    function createCharity(uint endTime, uint targetMoney, string memory infoHash) userExist(msg.sender) public {
        require(block.timestamp < endTime, "endTime should be later than now");
        require(targetMoney > 0, "the targetMoney must be positive integer");
        Charity memory charity = Charity(charities.length, charitiesOfUser[msg.sender].length, block.timestamp, endTime, targetMoney, 0, infoHash, CharityType.PENDING, msg.sender);
        charities.push(charity);
        charitiesOfUser[msg.sender].push(charity);
        emit CharityInfo(
            charity.id,
            charity.idInUser,
            charity.startTime,
            charity.endTime,
            charity.targetMoney,
            charity.hasMoney,
            charity.infoHash,
            charity.status,
            charity.owner
        );
    }

    event FundInfo(
        uint id,
        uint charityId,
        uint idInUser,
        uint idInCharity,
        uint money,
        uint timestamp,
        address donator
    );
    function donate(uint charityId) userExist(msg.sender) payable public{
        require(charityId < charities.length, "charityId cannot be larger than length");
        require(charities[charityId].status == CharityType.PENDING, "charity status is not PENDING"); // 还在募捐状态
        require(charities[charityId].hasMoney < charities[charityId].targetMoney, "charity has more money than target"); // fund is less than ta
        require(charities[charityId].endTime > block.timestamp, "charity is dued"); // expired
        require(charities[charityId].owner != msg.sender, "the owner of charity cannot donate to his/her charity"); // sender can not be equal to owner
        require(msg.value > 0);
        
        // 计算有效捐款
        // 捐款金额如果过多，则返还多余的钱
        uint validMoney = msg.value;
        uint diff = charities[charityId].targetMoney - charities[charityId].hasMoney;
        if (msg.value > diff) {
            validMoney = diff;
        }
        if (validMoney != msg.value) {
            msg.sender.transfer(msg.value-validMoney);
        }
        // 捐款转账
        address payable owner = charities[charityId].owner;
        owner.transfer(validMoney);
        // 更新募捐项目的信息
        // 包括已募捐金额
        // 包括募捐状态
        updateCharityMoney(charityId, charities[charityId].hasMoney+validMoney);
        if (charities[charityId].hasMoney >= charities[charityId].targetMoney){
            updateCharityStatus(charityId, CharityType.FINISH);
        }

        // 更新捐款信息
        Fund memory fund = Fund(funds.length, charityId, fundsOfUser[msg.sender].length, fundsOfCharity[charityId].length, validMoney, block.timestamp, msg.sender);
        funds.push(fund);
        fundsOfUser[msg.sender].push(fund);
        fundsOfCharity[charityId].push(fund);
        emit FundInfo(
            fund.id, 
            fund.charityId,
            fund.idInUser,
            fund.idInCharity,
            fund.money,
            fund.timestamp,
            fund.donator
        );
    }

    function updateCharityMoney(uint charityId, uint money) private {
            address owner = charities[charityId].owner;
            charities[charityId].hasMoney = money;
            uint charityIdInUser = charities[charityId].idInUser;
            charitiesOfUser[owner][charityIdInUser].hasMoney = money;
    }

    function updateCharityStatus(uint charityId, CharityType status) private {
            address owner = charities[charityId].owner;
            charities[charityId].status = status;
            uint charityIdInUser = charities[charityId].idInUser;
            charitiesOfUser[owner][charityIdInUser].status = status;
    }

    function getCharityAllNumber() view public returns (uint) {
        return charities.length;
    }

    function getCharitySomeoneNumber(address addr) view public returns (uint) {
        return charitiesOfUser[addr].length;
    }

    function getCharityById(uint id) view public returns (uint, uint, uint, uint, uint, uint, string memory, CharityType, address){
        require(id < charities.length, "id cannot be larger than length");
        Charity memory charity = charities[id];
        return (
            charity.id,
            charity.idInUser,
            charity.startTime,
            charity.endTime,
            charity.targetMoney,
            charity.hasMoney,
            charity.infoHash,
            charity.status,
            charity.owner
        );
    }

    function getCharityBySomeoneId(address addr, uint id) userExist(addr) view public returns (uint, uint, uint, uint, uint, uint, string memory, CharityType, address) {
        require(id < charitiesOfUser[addr].length, "id cannot be larger than length");
        Charity memory charity = charitiesOfUser[addr][id];
        return (
            charity.id,
            charity.idInUser,
            charity.startTime,
            charity.endTime,
            charity.targetMoney,
            charity.hasMoney,
            charity.infoHash,
            charity.status,
            charity.owner
        );
    }

    function getFundNumberBySomeoneAddr(address addr) userExist(addr) view public returns (uint) {
        return fundsOfUser[addr].length;
    }

    function getFundNumberByCharityId(uint charityId) view public returns (uint count) {
        for (uint i = 0; i < funds.length; i++){
            if (funds[i].charityId == charityId) count += 1;
        }
    }

    function getFundByIndexWithCharityId(uint charityId, uint index) view public returns (uint, uint, uint, uint, uint, uint, address){
        require(charityId < charities.length, "charityId cannot be larger than length");
        require(index < fundsOfCharity[charityId].length, "indexInUser cannot be larger than userlength");
        Fund memory fund = fundsOfCharity[charityId][index];
        return (
            fund.id, 
            fund.charityId,
            fund.idInUser,
            fund.idInCharity,
            fund.money,
            fund.timestamp,
            fund.donator
        );
    }

    function getFundById(uint fundId) view public returns (uint, uint, uint, uint, uint, uint, address){
        require(fundId < funds.length, "fundId cannot be larger than length");
        Fund memory fund = funds[fundId];
        return (
            fund.id, 
            fund.charityId,
            fund.idInUser,
            fund.idInCharity,
            fund.money,
            fund.timestamp,
            fund.donator
        );
    }

    fallback () external payable {
        
    }
    
}