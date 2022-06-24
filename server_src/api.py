"""
此文件用于提供用于客户端的API
"""
# 导入http框架
from flask import Flask, request
from flask_cors import CORS
import logging

# 导入基本库
import json
import time
import traceback
import asyncio
import nest_asyncio
import functools
import base64

# 导入币安api、脚本管理器
import binance
import datacenter
import script_manager

nest_asyncio.apply()  # 开启async嵌套

# 初始化flask框架对象
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域

# 设置flask框架log等级
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 创建公用协程loop
loop = asyncio.get_event_loop()

# 创建公用币安api对象
operator: binance.Operator = loop.run_until_complete(binance.create_operator())

# 创建公用脚本管理器对象
sm: script_manager.Core = script_manager.Core(loop)

# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as _f:
    config = json.loads(_f.read())


# 用于客户端进行HTTP交互的端口
@app.route('/', methods=['POST'])
def root():
    print(str(request.form)[:200])
    # 接收指定函数名以及参数并运行
    # 需接收验证口令正确才可运行，口令可以为自定义字符串
    # 接收格式为表单内 { function: '函数名', args: [...参数字符串列表]， password: '口令' }
    if request.form['password'] != config['password']:
        return json.dumps({
            'msg': 'error',
            'exception': 'password error'
        })
    func_name = request.form['function']
    args = json.loads(request.form['args'])
    try:
        # 使用协程执行指令
        res = loop.run_until_complete(_exec_function(func_name, args))
        res = json.dumps(res)
        return res
    except Exception as e:
        return json.dumps({
            'msg': 'error',
            'traceback': traceback.format_exc(),
            'func': func_name,
            'args': args
        })


async def _exec_function(func_name, args):
    if func_name == 'script_list':
        return await script_list(*args)
    elif func_name == 'script_log':
        return await script_log(*args)
    elif func_name == 'run_script':
        return await run_script(*args)
    elif func_name == 'stop_script':
        return await stop_script(*args)
    elif func_name == 'transfer':
        return await transfer(*args)
    elif func_name == 'trade_premium':
        return await trade_premium(*args)
    elif func_name == 'isolated_transfer':
        return await isolated_transfer(*args)
    elif func_name == 'query_interest':
        return await query_interest(*args)
    elif func_name == 'loan':
        return await loan(*args)
    elif func_name == 'repay':
        return await repay(*args)
    elif func_name == 'dev_sync':
        return await dev_sync(*args)
    elif func_name == 'force_refresh_position':
        return await force_refresh_balance(*args)
    else:
        return json.dumps({
            'msg': 'function name invalid.'
        })


async def script_list():
    """
    获取本地的脚本列表
    """
    return {
        'msg': 'success',
        'data': sm.ls()
    }


async def script_log(pid):
    """
    获取运行中脚本的log信息
    """
    pid = int(pid)
    return {
        'msg': 'success',
        'data': sm.get_log(pid)
    }


async def run_script(path, input_dict):
    """
    运行服务器上某个脚本
    """
    sm.exec(path, input_dict)
    return {
        'msg': 'success'
    }


async def stop_script(pid):
    """
    终止运行服务器上某个脚本
    """
    pid = int(pid)
    sm.kill(pid)
    return {
        'msg': 'success'
    }


async def transfer(trans_type, symbol, quantity):
    """
    万向划转接口
    :param trans_type:  划转类型，看币安API
    :param symbol:  划转的资产符号
    :param quantity:  划转的资产数量

    目前支持的type划转类型:
    MAIN_C2C 现货钱包转向C2C钱包
    MAIN_UMFUTURE 现货钱包转向U本位合约钱包
    MAIN_CMFUTURE 现货钱包转向币本位合约钱包
    MAIN_MARGIN 现货钱包转向杠杆全仓钱包
    MAIN_MINING 现货钱包转向矿池钱包
    C2C_MAIN C2C钱包转向现货钱包
    C2C_UMFUTURE C2C钱包转向U本位合约钱包
    C2C_MINING C2C钱包转向矿池钱包
    UMFUTURE_MAIN U本位合约钱包转向现货钱包
    UMFUTURE_C2C U本位合约钱包转向C2C钱包
    UMFUTURE_MARGIN U本位合约钱包转向杠杆全仓钱包
    CMFUTURE_MAIN 币本位合约钱包转向现货钱包
    MARGIN_MAIN 杠杆全仓钱包转向现货钱包
    MARGIN_UMFUTURE 杠杆全仓钱包转向U本位合约钱包
    MINING_MAIN 矿池钱包转向现货钱包
    MINING_UMFUTURE 矿池钱包转向U本位合约钱包
    MINING_C2C 矿池钱包转向C2C钱包
    MARGIN_CMFUTURE 杠杆全仓钱包转向币本位合约钱包
    CMFUTURE_MARGIN 币本位合约钱包转向杠杆全仓钱包
    MARGIN_C2C 杠杆全仓钱包转向C2C钱包
    C2C_MARGIN C2C钱包转向杠杆全仓钱包
    MARGIN_MINING 杠杆全仓钱包转向矿池钱包
    MINING_MARGIN 矿池钱包转向杠杆全仓钱包
    """
    await operator.request('api', '/sapi/v1/asset/transfer', 'POST', {
        'type': trans_type,
        'asset': symbol,
        'amount': quantity,
    }, auto_timestamp=True)

    return {
        'msg': 'success'
    }


async def trade_premium(symbol: str, amount: float, side: str, main_mode: str):
    """
    创建套利交易\n
    :param symbol: 创建套利交易的符号
    :param amount: 创建套利交易的货币数
    :param side: 创建套利交易的方向，只能为OPEN或者CLOSE
    :param main_mode: 现货下单的位置，只能为MAIN、MARGIN、ISOLATED
    """
    if side != 'OPEN' and side != 'CLOSE':
        raise Exception('side只能为OPEN或者CLOSE')
    if main_mode != 'MAIN' and main_mode != 'MARGIN' and main_mode != 'ISOLATED':
        raise Exception('main_mode只能为MAIN、MARGIN、ISOLATED')
    if side == 'OPEN':
        await asyncio.gather(
            operator.trade_market(symbol, main_mode, amount, 'BUY'),
            operator.trade_market(symbol, 'FUTURE', amount, 'SELL')
        )

    elif side == 'CLOSE':
        await asyncio.gather(
            operator.trade_market(symbol, main_mode, amount, 'SELL'),
            operator.trade_market(symbol, 'FUTURE', amount, 'BUY')
        )

    return {
        'msg': 'success'
    }


async def isolated_transfer(asset: str, symbol: str, to: str, amount):
    """
    用于逐仓账户的划转，逐仓账户没法用万向划转，只能用这个
    :param asset: 被划转的资产，例如BTC
    :param symbol: 操作的逐仓symbol，例如BTCUSDT
    :param to: 转账的目标，只有SPOT和ISOLATED_MARGIN，代表现货和逐仓
    :param amount: 划转的数量
    """
    asset = asset.upper()
    symbol = symbol.upper()
    to = to.upper()
    if to == 'SPOT':
        _from = 'ISOLATED_MARGIN'
    elif to == 'ISOLATED_MARGIN':
        _from = 'SPOT'
    else:
        return {
            'msg': 'transfer to invalid.',
        }

    await operator.request('api', '/sapi/v1/margin/isolated/transfer', 'POST', {
        'asset': asset,
        'symbol': symbol,
        'transFrom': _from,
        'transTo': to,
        'amount': amount,
        'timestamp': binance.get_timestamp()
    })

    return {
        'msg': 'success'
    }


async def query_interest(asset):
    """
    查询某个资产的借贷利息
    """
    asset = asset.upper()
    info = await operator.request('api', '/sapi/v1/margin/interestRateHistory', 'GET', {
        'asset': asset,
        'timestamp': binance.get_timestamp()
    })

    res_data = []
    for e in info:
        res_data.append({
            'dailyInterestRate': float(e['dailyInterestRate']),
            'timestamp': e['timestamp']
        })

    return {
        'msg': 'success',
        'data': res_data
    }


async def loan(asset, is_isolated, symbol, amount):
    """
    归还某个资产
    """
    asset = asset.upper()
    if isinstance(is_isolated, bool):
        if is_isolated:
            is_isolated = 'TRUE'
        else:
            is_isolated = 'FALSE'
    if is_isolated == 'TRUE':
        symbol = symbol.upper()
        await operator.request('api', '/sapi/v1/margin/loan', 'POST', {
            'asset': asset,
            'isIsolated': is_isolated,
            'symbol': symbol,
            'amount': amount,
            'timestamp': binance.get_timestamp()
        })
    elif is_isolated == 'FALSE':
        await operator.request('api', '/sapi/v1/margin/loan', 'POST', {
            'asset': asset,
            'isIsolated': is_isolated,
            'amount': amount,
            'timestamp': binance.get_timestamp()
        })
    else:
        return {
            'msg': 'isolated param invalid.'
        }

    return {
        'msg': 'success'
    }


async def repay(asset, is_isolated, symbol, amount):
    asset = asset.upper()
    if isinstance(is_isolated, bool):
        if is_isolated:
            is_isolated = 'TRUE'
        else:
            is_isolated = 'FALSE'
    if is_isolated == 'TRUE':
        symbol = symbol.upper()
        await operator.request('api', '/sapi/v1/margin/repay', 'POST', {
            'asset': asset,
            'isIsolated': is_isolated,
            'symbol': symbol,
            'amount': amount,
            'timestamp': binance.get_timestamp()
        })
    elif is_isolated == 'FALSE':
        await operator.request('api', '/sapi/v1/margin/repay', 'POST', {
            'asset': asset,
            'isIsolated': is_isolated,
            'amount': amount,
            'timestamp': binance.get_timestamp()
        })
    else:
        return {
            'msg': 'isolated param invalid.'
        }

    return {
        'msg': 'success'
    }


async def dev_sync(data):
    """
    用来将开发机的代码上传到服务器
    """
    for e in data:
        name = e['name']
        base = e['data']
        with open(name, 'wb') as f:
            buf = base64.b64decode(base.encode('utf-8'))
            f.write(buf)

    return {
        'msg': 'success'
    }


async def force_refresh_balance():
    """
    使用此API可以强制刷新仓位信息
    不会从websocket接口接收信息，而是使用http接口请求信息
    最终数据会更新到数据中心上
    """
    datacenter_client = await datacenter.create_client()

    run_gather = []

    # 获取现货的资产数量
    res = await operator.request('api', '/api/v3/account', 'GET', {}, auto_timestamp=True)
    res = res['balances']
    for e in res:
        asset = e['asset']
        free = float(e['free'])
        run_gather.append(datacenter_client.compare_update({'asset', 'main', asset}, free))

    # 获取期货的资产和头寸信息
    res = await operator.request('fapi', '/fapi/v2/account', 'GET', {}, auto_timestamp=True)
    for e in res['assets']:
        asset = e['asset']
        free = float(e['maxWithdrawAmount'])
        run_gather.append(datacenter_client.compare_update({'asset', 'future', asset}, free))
    for e in res['positions']:
        symbol = e['symbol']
        position = float(e['positionAmt'])
        run_gather.append(datacenter_client.compare_update({'position', 'future', symbol}, position))

    # 获取全仓的资产和借贷数量
    res = await operator.request('api', '/sapi/v1/margin/account', 'GET', {}, auto_timestamp=True)
    res = res['userAssets']
    for e in res:
        asset = e['asset']
        borrowed = float(e['borrowed'])
        free = float(e['free'])
        run_gather.append(datacenter_client.compare_update({'asset', 'margin', asset}, free))
        run_gather.append(datacenter_client.compare_update({'borrowed', 'margin', asset}, borrowed))

    # 获取逐仓的资产和借贷数量
    res = await operator.request('api', '/sapi/v1/margin/isolated/account', 'GET', {}, auto_timestamp=True)
    res = res['assets']
    for e in res:
        symbol = e['symbol']

        free = float(e['baseAsset']['free'])
        borrowed = float(e['baseAsset']['borrowed'])
        run_gather.append(datacenter_client.compare_update({'asset', 'isolated', 'base', symbol}, free))
        run_gather.append(datacenter_client.compare_update({'borrowed', 'isolated', 'base', symbol}, borrowed))

        free = float(e['quoteAsset']['free'])
        borrowed = float(e['quoteAsset']['borrowed'])
        run_gather.append(datacenter_client.compare_update({'asset', 'isolated', 'quote', symbol}, free))
        run_gather.append(datacenter_client.compare_update({'borrowed', 'isolated', 'quote', symbol}, borrowed))

    for e in run_gather:
        await e

    await datacenter_client.close()

    return {
        'msg': 'success'
    }


def memory_summary():
    # 只在需要的时候引入pympler！ 不然引入后就会影响程序运行
    while True:
        from pympler import summary, muppy
        mem_summary = summary.summarize(muppy.get_objects())
        rows = summary.format_(mem_summary)
        print('\n'.join(rows))
        time.sleep(300)


async def main():
    # # 运行内存泄露检测
    # threading.Thread(target=memory_summary).start()

    # 读取要自动启动的脚本
    print('正在执行自启动脚本:')
    for name in config['exec']:
        print(name)
        sm.exec(name, {})

    ip = config['api']['server_ip']
    port = config['api']['server_port']

    print('即将运行http服务器{}:{}'.format(ip, port))
    loop.run_in_executor(None, functools.partial(app.run, config['api']['server_ip'],
                                                 config['api']['server_port'],
                                                 ssl_context=(config['ssl_crt'],
                                                              config['ssl_key'])))


if __name__ == '__main__':
    loop.run_until_complete(main())
    loop.run_forever()
