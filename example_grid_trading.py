"""

example: 增强型网格交易

以上证50etf(510050)为例
----------网格设置----------
价值交易                        2.300-2.600
流动-价值混合交易                2.600-3.200
流动交易                        3.200-3.800
底仓清仓                        > 3.800

网格密度                        0.7%
交易佣金                        0.018%
每格收益                        0.682%

流动-价值混合交易中价值交易量      100股
每格交易量                      1200股

"""

from updateloop import UpdateLoop
from updateobj import UpdateObj
from user import User
from stock import Stock
from trade import Trade, OrderHistoty, Action

import time


# # 快速下单
# # stock         要交易的股票对象
# # trade_type    交易类型：“B”买，“S”卖
# # amount        交易量 单位 股
# # price         下单价格，默认-1，即以当前市场价下单
# # timeout       超时时间，默认10s 超过超时时间的报价单将被撤回
# def fast_trade(user, stock, trade_type, amount, price = -1, timeout=10):
#     trade = Trade(stock=stock, user=user, amount=amount, trade_type=trade_type,price=price,timeout=timeout - 1)
#     loop.add_obj(trade)
#     time.sleep(timeout + 1)
#     return trade.order_info


class ExGridTrading(UpdateObj):
    def __init__(self, loop:UpdateLoop, interval=1) -> None:
        self.__loop = loop
        # 新建一个OriderHistory对象，存储历史交易记录
        self.__OrderHistory = OrderHistoty("ExGridTrading_Order_nexchen")
        # 新建一个HoldingOrders对象，存储尚未卖出的，持仓中的交易记录
        self.__HoldingOrders = OrderHistoty("ExGridTrading_Holding_nexchen")


        # 新建一个用户对象，并将其注册到循环中。loop会定时更新user的基本信息，并维持会话
        #  User(uuid) 这可以写到对象内，也可以写到外边
        self.__user = User("03a0c6cb97664f89a8f0305389e42526")
        self.__loop.add_obj(self.__user)
        
        self.__stock = Stock("510050")
        self.__loop.add_obj(self.__stock)

        self.__set_grids(2.3, 4.2, 1.007)

        self.__price_A = 2.6        # 价值交易 和 价值-流动性交易的分界线
        self.__price_B = 3.2        # 价值-流动性交易 和 流动性交易的分界线
        self.__price_C = 3.8        # 流动性交易的终止线

        self.__amount = 1200        # 单次网格买入股数
        self.__holding_amount = 100 # 底仓股数

        self.__trade = Action()
        super().__init__(interval)

    # 计算出交易的网格价
    # buttom_price          网格底价
    # top_price             网格顶价
    # grid_density          网格密度
    def __set_grids(self, buttom_price, top_price, grid_density):
        self.__grids = []
        
        while(buttom_price < top_price):
            print("%.3f"%buttom_price)
            self.__grids.append(buttom_price)
            buttom_price = buttom_price*grid_density

    # 判断两个float的价格是否相等（取3位有效值，ex: 2.700==2.6998）
    def __is_price_equal(self, price1:float, price2:float) -> bool:
        price1 = round(price1*1000)         # 由于价格为3位小数，需要将其转换为整数方便比较
        price2 = round(price2*1000)         # 由于价格为3位小数，需要将其转换为整数方便比较
        if price1 == price2:
            return True
        return False

    def __is_on_grids(self, target_price:float) -> bool:
        for price in self.__grids:
            if self.__is_price_equal(target_price, price):
                return True

        return False

    # 快速下单
    # stock         要交易的股票对象
    # trade_type    交易类型：“B”买，“S”卖
    # amount        交易量 单位 股
    # price         下单价格，默认-1，即以当前市场价下单
    # timeout       超时时间，默认10s 超过超时时间的报价单将被撤回
    def fast_trade(self, trade_type, amount, price = -1, timeout=10):

        print("当前价格为%.3f, 触发网格自动交易，委托类型 %s, 委托数量 %d 股"%(price, trade_type, amount))
        self.__trade = Trade(stock=self.__stock, user=self.__user, amount=amount, trade_type=trade_type, price=price, timeout=timeout)
        self.__loop.add_obj(self.__trade)
        time.sleep(timeout + 1)
        if self.__trade.status == self.__trade.FINISHED or \
            self.__trade.status == self.__trade.OVERTIME:
            self.__loop.del_any(self.__trade)

        return self.__trade.order_info

    # 判断当前价格适合买入还是卖出
    def buy_or_sell(self, price) -> str:
        if self.__HoldingOrders.get_len() == 0:             # 当前没有持仓记录，买入
            return "B"
            
        prev_price = self.__HoldingOrders.get_prev_delegate_price()
        if self.__is_price_equal(price, prev_price):      # 如果当前价格等于最后持仓的价格 则不操作 这里有一个bug，当部分成交的时候可能会亏损 问题应该不大
            return "N"
        elif price > prev_price:                            # 高于最后买入的价格，就将其平掉
            return "S"
        elif price < prev_price:                            # 低于最后买入的价格，就买入
            return "B"
        
        # 理论上不存在此情况
        return "N"

    # 检查当前交易是否成功，如果成功，则保存交易信息
    def check_and_save_order(self):
        if int(self.__trade.order_info["Cjsl"]) > 0:      # 成交数量大于0, 表明有成功成交
            if self.__trade.order_info["Mmlb"] == "B":      # 如果是买入 则直接入HoldingOrder栈
                self.__HoldingOrders.save_order(self.__trade.order_info)

            elif self.__trade.order_info["Mmlb"] == "S":    # 卖出，不管成交多少 都和之前买入的进行抵消 这里简化了一些部分成交的复杂情况
                prev_order = self.__HoldingOrders.pop_prev_order()

                # prev_order["Cjsl"] = int(prev_order["Cjsl"]) - int(self.__trade.order_info["Cjsl"])
                # if prev_order["Cjsl"] > 0:
                #     prev_order["Cjsl"] = str(prev_order["Cjsl"])
                #     self.__HoldingOrders.save_order(prev_order)
                
            self.__OrderHistory.save_order(self.__trade.order_info)

    def update(self) -> int:
        cur_price = self.__stock.get_current_price()
        if self.__is_on_grids(cur_price):       # 确认当前价格在网格点上
            B_or_S = self.buy_or_sell(cur_price)    # 确定交易类别
            if cur_price < self.__price_A:      # 价格在价值交易区间中 只买不卖
                if B_or_S == "B":      # 买入
                    self.fast_trade("B", self.__amount, cur_price)
                    self.check_and_save_order()
                elif B_or_S == "S":     # 只出栈，不做实际的卖出操作
                    self.__HoldingOrders.pop_prev_order()

            elif cur_price < self.__price_B:    # 价格在价值-流动性交易区间中
                if B_or_S == "B":      # 买入
                    self.fast_trade("B", self.__amount, cur_price)
                    self.check_and_save_order()
                elif B_or_S == "S":     # 卖出一部分，保留底仓
                    self.fast_trade("S", self.__amount - self.__holding_amount, cur_price)
                    self.check_and_save_order()

            elif cur_price < self.__price_C:    # 价格在流动性交易区间中
                if B_or_S == "B":      # 买入
                    self.fast_trade("B", self.__amount, cur_price)
                    self.check_and_save_order()
                elif B_or_S == "S":     # 卖出
                    self.fast_trade("S", self.__amount, cur_price)
                    self.check_and_save_order()
            else:                               # 价格超出范围，不自动操作了，手动卖出吧
                pass
            
        return 0




# 新建一个主事件循环，每一秒更新一次
loop = UpdateLoop(interval=1)
loop.setDaemon(True)        # 主线程结束以后子线程也退出
loop.start()

TradingS = ExGridTrading(loop)
# loop.add_target(TradingS)   # 将网格策略直接作为指标添加到主循环里，这样交易延迟更短，目前下单存在bug

# 新建一个循环用于指标同步，这样交易可能存在延迟
time.sleep(5)   # 等循环全部初始化
while True:
    TradingS.update()
    time.sleep(0.5)

time.sleep(60*60*24*365*10) # 永久运行下去