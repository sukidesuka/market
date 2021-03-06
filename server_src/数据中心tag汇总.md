### 数据中心TAG汇总速查

```
[]符号里面表示通配符
通配符内符号意义
asset 资产名，例如BNB
symbol 交易对符号，例如BNBUSDT
nickname 服务器识别昵称，例如us1

json开头的一般是专供客户端显示用的，而且存储格式就是json

特别注意：TAG不分前后，没有顺序

下单精度
precision quote main [symbol]
precision quote future [symbol]

全仓逐仓支持
allow margin [asset]
allow isolated [symbol]

资产余额
asset main [asset]
asset future [asset]
asset margin [asset]
asset isolated base [symbol]
asset isolated quote [symbol]

负债余额
borrowed margin [asset]
borrowed isolated base [symbol]
borrowed isolated quote [symbol]

仓位
position future [symbol]

价格
price main [symbol]
price future [symbol]

风险率
risk future usage       // 资金使用率
risk margin usage       // 借贷占比


溢价
premium rate [symbol]
premium dif [symbol]
premium fundingRate [symbol]
premium fundingRateHistory [symbol]
premium fundingRateHistory timestamp [symbol]  // 上面那个的时间戳

资金费率流水
json fundingFee

聚合仓位信息
json position
// 聚合仓位信息内容数据格式[item1, item2...]
{
    'main': 0,  # 现货余额
    'margin': 0,  # 全仓余额
    'marginBorrowed': 0,  # 全仓借入
    'isolated': 0,  # 逐仓余额
    'isolatedBorrowed': 0,  # 逐仓借入
    'isolatedQuote': 0,  # 逐仓合约币（一般是USDT）余额
    'isolatedQuoteBorrowed': 0,  # 逐仓合约币借入
    'isolatedRisk': 0,  # 逐仓贷款占比
    'future': 0,  # 期货余额
    'net': 0,  # 净持仓
    'hedging': 0,  # 双向持仓
    
    'value': 0,  # 双向持仓的单边市值
    'fundingRate': 0,  # 期货费率
    'premiumRate': 0,  # 期货溢价
}


服务器运行状况
server status cpu usage percent [nickname]
server status cpu usage percentHistory [nickname]
server status ram usage percent [nickname]
server status ram usage percentHistory [nickname]
server status ram usage total [nickname]
server status ram usage available [nickname]
server status ram usage used [nickname]
server status ram usage free [nickname]
server status disk usage percent [nickname]
server status disk usage percentHistory [nickname]
server status disk usage used [nickname]
server status disk usage free [nickname]
server status disk usage total [nickname]
server info ip [nickname]
server info port api [nickname]
server info port datacenter [nickname]
server info port subscribe [nickname]

脚本管理器
json scriptManager status
// 样例
[{'thread_id': 0, 'name': 'sc_compute', 'status': '运行中'}, ...]

警报
alarm common


```

