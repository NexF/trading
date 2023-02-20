"""

example: 增强型网格交易

以上证50etf(510050)为例
----------网格设置----------
价值交易                        < 2.600
流动-价值混合交易                2.600-3.200
流动交易                        3.200-3.800
底仓清仓                        > 3.800

网格密度                        0.5%
交易佣金                        0.018%*2
每格收益                        0.464%

流动-价值混合交易中价值交易量      100股
每格交易量                      700股

"""
import pdb_attach
pdb_attach.listen(50000)  # Listen on port 50000.

import sys,os,time
sys.path.append('./src')

from configparser import ConfigParser
import logging
from updateloop import UpdateLoop
from updateobj import UpdateObj
from user import User
from stock import Stock
from trade import Trade, OrderHistoty, Action



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
    def __init__(self, loop:UpdateLoop, user:User, stock:Stock, interval=1) -> None:
        self.__loop = loop
        # 新建一个OriderHistory对象，存储历史交易记录
        self.__OrderHistory = OrderHistoty("ExGridTrading_Order_nexchen")
        # 新建一个HoldingOrders对象，存储尚未卖出的，持仓中的交易记录
        self.__HoldingOrders = OrderHistoty("ExGridTrading_Holding_nexchen")


        # 新建一个用户对象，并将其注册到循环中。loop会定时更新user的基本信息，并维持会话
        #  User(uuid) 这可以写到对象内，也可以写到外边
        self.__user = user
        self.__loop.add_obj(self.__user)
        
        self.__stock = stock
        self.__loop.add_obj(self.__stock)

        self.__set_grids(2.0, 5, 1.005)

        self.__price_A = 2.6        # 价值交易 和 价值-流动性交易的分界线
        self.__price_B = 3.2        # 价值-流动性交易 和 流动性交易的分界线
        self.__price_C = 3.8        # 流动性交易的终止线

        self.__amount = 700        # 单次网格买入股数
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
            buttom_price = round(buttom_price*1000)/1000.0
            logging.info("网格价:%.3f"%buttom_price)
            self.__grids.append(buttom_price)
            buttom_price = buttom_price*grid_density

    # 判断两个float的价格是否相等（取3位有效值，ex: 2.700==2.6998）
    def __is_price_equal(self, price1:float, price2:float) -> bool:
        price1 = round(price1*1000)         # 由于价格为3位小数，需要将其转换为整数方便比较
        price2 = round(price2*1000)         # 由于价格为3位小数，需要将其转换为整数方便比较
        if price1 == price2:
            return True
        return False

    def __get_nearest_grids(self, target_price:float):
        price = []
        for i in range(2, len(self.__grids)):
            # 当target_price在self.__grids[i - 1] 和self.__grids[i] 之间
            if target_price <= self.__grids[i]:
                # 当target_price更靠近 self.__grids[i]
                if self.__grids[i] - target_price < target_price - self.__grids[i - 1]:
                    price.append(self.__grids[i - 1])
                    price.append(self.__grids[i])
                    price.append(self.__grids[i + 1])
                # 当target_price更靠近 self.__grids[i - 1]
                else:
                    price.append(self.__grids[i - 2])
                    price.append(self.__grids[i - 1])
                    price.append(self.__grids[i])
                
                logging.info(f"当前最接近的网格为：{price}")
                
                return price
        price = [1,1,1]
        return price

    # 快速下单
    # stock         要交易的股票对象
    # trade_type    交易类型：“B”买，“S”卖
    # amount        交易量 单位 股
    # price         下单价格，默认-1，即以当前市场价下单
    # timeout       超时时间，默认10s 超过超时时间的报价单将被撤回
    def fast_trade(self, trade_type, amount, price = -1, timeout=10):

        logging.warning("当前价格为%.3f, 触发网格自动交易，委托类型 %s, 委托数量 %d 股"%(price, trade_type, amount))
        self.__trade = Trade(stock=self.__stock, user=self.__user, amount=amount, trade_type=trade_type, price=price, timeout=timeout)
        self.__loop.add_obj(self.__trade)
        time.sleep(timeout + 1)
        if self.__trade.status != self.__trade.IN_PROCESS:
            self.__loop.del_any(self.__trade)
        if self.__trade.status == self.__trade.ERROR:
            logging.error("下单失败，错误原因：%s"%(self.__trade.return_info["Message"]))
            return -1
        return 0

    # 判断当前价格适合买入还是卖出
    def buy_or_sell(self, price) -> str:
        order = {"type":"N", "price":0.0}
        logging.info(f"当前价格：{price}")
        if self.__HoldingOrders.get_len() == 0:             # 当前没有持仓记录，买入
            nearest_grids = self.__get_nearest_grids(price)
            if price > nearest_grids[1]:
                order["price"] = nearest_grids[2]
            else:
                order["price"] = nearest_grids[1]
            order["type"] = "B"
            return order

        prev_price = self.__HoldingOrders.get_prev_delegate_price()
        nearest_grids = self.__get_nearest_grids(prev_price)
        if price > nearest_grids[0] and price < nearest_grids[2]:        # 如果当前价格没有突破网格 则不操作 这里有一个bug，当部分成交的时候可能会亏损 问题应该不大
            order["price"] = 0.0
            order["type"] = "N"
            return order
        elif price >= nearest_grids[2]:                                        # 高于或等于最后买入的网格+1格，就将其平掉
            order["price"] = nearest_grids[2]
            order["type"] = "S"
            return order
        elif price <= nearest_grids[0]:                                        # 低于或等于最后买入的价格-1格，就买入
            order["price"] = nearest_grids[0]
            order["type"] = "B"
            return order      

        # 理论上不存在此情况
        return order

    # 检查当前交易是否成功，如果成功，则保存交易信息
    def check_and_save_order(self):
        if int(self.__trade.order_info["Cjsl"]) > 0:      # 成交数量大于0, 表明有成功成交
        # if int(self.__trade.order_info["Cjsl"]) >= 0:      # 成交数量大于0, 表明有成功成交 debug
            
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
        t = time.localtime(time.time())

        # 判断是否在交易时间，不在交易时间直接return
        if t.tm_hour < 9 or t.tm_hour > 14:
            return 0
        if t.tm_hour == 9 and t.tm_min < 30:
            return 0


        cur_price = self.__stock.get_current_price()
        # cur_price = 2.789
        order = self.buy_or_sell(cur_price)    # 确定交易类别
        B_or_S = order["type"]
        grid_price = order["price"]        # 最接近网格点的价格
        if cur_price < self.__price_A:      # 价格在价值交易区间中 只买不卖
            if B_or_S == "B":      # 买入
                if self.fast_trade("B", self.__amount, grid_price) == 0:
                    self.check_and_save_order()
            elif B_or_S == "S":     # 只出栈，不做实际的卖出操作
                self.__HoldingOrders.pop_prev_order()

        elif cur_price < self.__price_B:    # 价格在价值-流动性交易区间中
            if B_or_S == "B":      # 买入
                if self.fast_trade("B", self.__amount, grid_price) == 0:
                    self.check_and_save_order()
            elif B_or_S == "S":     # 卖出一部分，保留底仓
                if self.fast_trade("S", self.__amount - self.__holding_amount, grid_price) == 0:
                    self.check_and_save_order()

        elif cur_price < self.__price_C:    # 价格在流动性交易区间中
            if B_or_S == "B":      # 买入
                if self.fast_trade("B", self.__amount, grid_price) == 0:
                    self.check_and_save_order()
            elif B_or_S == "S":     # 卖出
                if self.fast_trade("S", self.__amount, grid_price) == 0:
                    self.check_and_save_order()
        else:                               # 价格超出范围，不自动操作了，手动卖出吧
            pass
            
        return 0



if __name__ == "__main__":

    # 从父进程fork一个子进程出来
    pid = os.fork()
    # 子进程的pid一定为0，父进程大于0
    if pid:
        # 退出父进程，sys.exit()方法比os._exit()方法会多执行一些刷新缓冲工作
        sys.exit(0)



    os.rename(sys.argv[0] + '.log', sys.argv[0] + '.log.old')
    logging.basicConfig(filename=sys.argv[0] + '.log', level=logging.INFO, format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s():%(lineno)d|%(message)s')
    try:
        conf = ConfigParser()
        conf.read("trading.cfg", encoding='utf-8')
        sections=dict(conf.items('login_info'))
        username = sections['user']
        passwd = sections['passwd']
    except:
        logging.exception("读取config文件失败，请检查")
        exit
        
    # 新建一个主事件循环，每一秒更新一次
    loop = UpdateLoop(interval=1)
    loop.setDaemon(True)                # 主线程结束以后子线程也退出
    loop.start()

    # 新建一个用户对象，并将其注册到循环中。loop会定时更新user的基本信息，并维持会话
    #  User(uuid) 这可以写到对象内，也可以写到外边
    user = User(username, passwd)
    stock = Stock("510050")
    TradingS = ExGridTrading(loop, user=user, stock=stock)

    # loop.add_target(TradingS)         # 将网格策略直接作为指标添加到主循环里，这样交易延迟更短，目前下单存在bug

    # 新建一个循环用于指标同步，这样交易可能存在延迟
    time.sleep(5)   # 等循环全部初始化
    while True:
        
        TradingS.update()
        time.sleep(0.5)

    time.sleep(60*60*24*365*10) # 永久运行下去
