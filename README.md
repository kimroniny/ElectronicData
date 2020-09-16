# ElectronicData
electronic datas sharing frontend based flask smartcontract based future

# flask-migrate

## 基本指令

```bash
flask db init
flask db migrate
flask db upgrade
flask run -h 0.0.0.0 -p 5000
```

# 环境预部署

```bash
python prepare-environment.py
```


# Tips

1. mysqlclient 无法安装，提示找不到mysql_config
```bash
sudo apt install default-libmysqlclient-dev
```
> refer: https://stackoverflow.com/questions/5178292/pip-install-mysql-python-fails-with-environmenterror-mysql-config-not-found
