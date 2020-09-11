## create node dir

```bash
mkdir node1 node2 node3
```

## create account & backup keystore

```bash
geth --datadir node1/data account new
# don't forget to backup keystore
```

## puppeth

使用 puppeth 创建 genesis 配置文件

保存 genesis 到 paper_test.json 文件

## init
```bash
geth --datadir node1/data init paper_test.json
```

## start rpc
```bash
geth  --rpc --rpcaddr 0.0.0.0 --rpcport 3001 --rpcapi "personal,eth,net,web3" --rpccorsdomain "*" --allow-insecure-unlock -datadir node1/data --port 30301 
```

## addPeer
```bash
geth attach ipc:node1/data/geth.ipc
> admin.nodeInfo.enode # 查看当前节点的 enode 信息
> admin.addPeer('') # 把其他节点的 enode 信息加入进来
> admin.peers
```

## basic cmds
```js
personal.unlockAccount(eth.accounts[0], '')
miner.start(1) // 挖矿前必须先解锁账户
eth.sendTransaction({'to': eth.accounts[1], 'from': eth.acccounts[0], 'value': 100000000})
```

## Tips

1. 每次杀掉geth后重新启动，都需要重新设置`admin.addPeer('')`，重新`personal.unlockAccount(eth.accounts[0],'',0)`，重新`miner.stop(); miner.start(1)`