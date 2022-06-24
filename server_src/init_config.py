"""
运行此脚本，在本地创建默认的配置文件，方便手写修改
已有配置文件也可运行，只会添加没有的条目，不会覆盖
对于多余的条目，会发出警告
"""
import json

default_config = {
    "binance_public_key": "xxxxxxxx",  # 币安的apikey
    "binance_private_key": "xxxxxxxx",  # 币安的私钥

    "api": {
        "server_ip": "0.0.0.0",
        "server_port": 10000,
    },
    "datacenter": {
        "server_ip": "0.0.0.0",
        "server_port": 10001,
        "client_ip": "xxxxx",
        "client_port": 10001,
        "subscribe_server_ip": "0.0.0.0",
        "subscribe_server_port": 10002,
        "subscribe_client_ip": "xxxxxx",
        "subscribe_client_port": 10002
    },

    "ssl_crt": "ssl.crt",
    "ssl_key": "ssl.key",

    "nickname": "defaultName",  # 此服务器的默认昵称
    "self_ip": "us.pwp.today",  # 此服务器的连接地址
    "self_api_port": 10000,  # 此服务器的api端口
    "self_datacenter_port": 10001,  # 此服务器的数据中心端口
    "self_subscribe_port": 10002,  # 此服务器的订阅端口

    "password": "defaultPassword",  # 中央服务器认证口令

    "exec": []  # 需要运行时自动启动的脚本
}

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
except FileNotFoundError:
    config = {}

# 遍历对比没有的条目进行补充
for key in default_config.keys():
    if key not in config.keys():
        config[key] = default_config[key]

# 遍历多余的条目进行警告
for key in config.keys():
    if key not in default_config:
        print('警告：发现多余的key', key)

# 把配置写入文件
with open('config.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(config))
