import json
CHAINCONFIG = {
    'charity': {
        'url': 'http://192.168.64.136:3001',
        'contract': {
            'charity': {
                'address':open('./contract/address', 'r').read().strip('\n\r '),
                'abifile':'./contract/abi/Charity.abi',
            }
        },
        'gasPrice': 0,
    }
}