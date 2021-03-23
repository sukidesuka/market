"""
获取配对的现货与期货价格，并计算溢价
"""
import data_center


class Script(object):
    def __init__(self, dc: data_center.Server):
        self.dc = dc
        callback = data_center.CallbackWrapper(self.calc_premium, {'price', 'main'})
        self.dc.add_update_callback(callback)
        callback = data_center.CallbackWrapper(self.calc_premium, {'price', 'future'})
        self.dc.add_update_callback(callback)

    def calc_premium(self, data: data_center.DataWrapper):
        # 判断是哪边的币价更新了
        if 'main' in data.get_tags():
            mode = 'main'
            special_tags = data.get_tags() - {'price', 'main'}
        else:
            mode = 'future'
            special_tags = data.get_tags() - {'price', 'future'}
        # 返回的数据tag数异常直接返回
        if len(special_tags) != 1:
            return
        # 获取交易符号
        symbol = special_tags.pop()
        # 获取另一方的价格
        if mode == 'main':
            main_price = data.get()
            future_price = self.dc.get({'price', 'future', symbol}).get()
        else:
            main_price = self.dc.get({'price', 'main', symbol}).get()
            future_price = data.get()
        # 如果有数据为None则表示对方数据缺失，直接返回
        if main_price is None or future_price is None:
            return
        # 计算溢价并且放回去
        premium_price = 1 - future_price / main_price
        premium_price *= 100
        self.dc.update({'premium', 'percent', symbol}, premium_price)
        self.dc.update({'premium', 'dif', symbol}, future_price - main_price)
