import sys
sys.path.append('./src')

from updateloop import UpdateLoop
from user import User
from stock import Stock
from trade import Trade
import time


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
    # loop.del_any(trade)
    if trade.status == trade.FINISHED:
        return 0
    return -1


# 新建一个主事件循环，每一秒更新一次
loop = UpdateLoop(interval=1)
loop.setDaemon(True)        # 主线程结束以后子线程也退出
loop.start()

print("main thread\n")

# 新建一个用户对象，并将其注册到循环中。loop会定时更新user的基本信息，并维持会话
#  User(uuid)
# user = User("ec524d177aee40fe8c4afdd968566579")
user = User('540860216117', '689067')
user_id = loop.add_obj(user)

# 新建一个股票对象，并将其注册到循环中，loop会定时更新股票的基本信息，如当前价格，成交量等
stock = Stock("510300")
stock_id = loop.add_obj(stock)

# 按照当前市场价买入100股stock，等待10s后如果交易成功则返回succeed
if (fast_trade(user, stock, "B", "100") == 0):
    print("order succeed\n")
else:
    print("order err\n")

time.sleep(50000)
print("main thread\n")
