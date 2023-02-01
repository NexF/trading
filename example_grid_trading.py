"""
example: 增强型网格交易

以上证50etf(510050)为例
----------网格设置----------
价值交易                        2.300-2.600
流动-价值混合交易                2.600-3.200
流动交易                        3.200-3.800
底仓清仓                        >3.800

网格密度                        0.7%
交易佣金                        0.018%
每格收益                        0.782%

流动-价值混合交易中价值交易量      100股
每格交易量                      1200股
"""

from updateloop import UpdateLoop
from user import User
from stock import Stock
from trade import Trade
from redis import Redis         # 用来存储交易数据
import time


# 新建一个主事件循环，每一秒更新一次
loop = UpdateLoop(interval=1)
loop.setDaemon(True)        # 主线程结束以后子线程也退出
loop.start()

# 快速下单
# stock         要交易的股票对象
# trade_type    交易类型：“B”买，“S”卖
# amount        交易量 单位 股
# price         下单价格，默认-1，即以当前市场价下单
# timeout       超时时间，默认10s 超过超时时间的报价单将被撤回
def fast_trade(user, stock, trade_type, amount, price = -1, timeout=10):
    trade = Trade(stock=stock, user=user, amount=amount, trade_type=trade_type,price=price,timeout=timeout - 1)
    loop.add_obj(trade)
    time.sleep(timeout + 1)
    # loop.del_any(trade)       # 存在多线程bug，还没修复
    if trade.status == trade.FINISHED:
        return 0
    return -1

# 新建一个用户对象，并将其注册到循环中。loop会定时更新user的基本信息，并维持会话
#  User(uuid)
user = User("ec524d177aee40fe8c4afdd968566579")
user_id = loop.add_obj(user)