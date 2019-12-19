pragma solidity ^0.4.25;

contract Electronic {

    enum OwnType {NOTHAVE, HAVEBOUGHT, HAVEBUTNOTBOUGHT, TRANSFERED}

    struct Property {
        uint resource;
        OwnType own_type; // 0: no, 1: have, 2: transfered
        address transfer_to;
    }

    address[] userAddrs;

    mapping (address => Property[]) public users;

    function checkUser(address _addr) internal returns (bool) {
        for (uint i = 0; i < userAddrs.length; i++){
            if (userAddrs[i] == _addr) return true;
        }
        return false;
    }

    modifier userExist(address _addr) {
        require(checkUser(_addr));
        _;
    }

    function newUser(address _addr) public {
        userAddrs.length++;
        userAddrs[userAddrs.length-1] = _addr;
    }

    function obtainProperty(address _addr, uint _res, OwnType _type) userExist(_addr) public {
        Property[] storage props = users[_addr];
        props.length++;
        props[props.length-1] = Property(_res, _type, 0x00);

    }

    function transProperty(address _addr_from, address _addr_to, uint _res) userExist(_addr_from) userExist(_addr_to) public returns(bool) {
        Property[] storage props = users[_addr_from];
        for (uint i = 0; i < props.length; i++){
            Property storage p = props[i];
            if (p.resource == _res && (p.own_type == OwnType.HAVEBOUGHT || p.own_type == OwnType.HAVEBUTNOTBOUGHT)) {
                p.transfer_to = _addr_to;
                p.own_type = OwnType.TRANSFERED;
                obtainProperty(_addr_to, _res, OwnType.HAVEBUTNOTBOUGHT);
                return true;
            }
        }
        return false;
    }

    function obtainProperty(address _addr, uint _res) userExist(_addr) view public returns (OwnType) {
        Property[] memory props = users[_addr];
        for (uint i = 0; i < props.length; i++){
            if (props[i].resource == _res){
                return props[i].own_type;
            }
        }
        return OwnType.NOTHAVE;
    }

}