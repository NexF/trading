from updateobj import UpdateObj
import trading_interface
import json

class Stock(UpdateObj):
    def __init__(self, stock_id, interval = 1):
        self.__stock_id = stock_id
        super().__init__(interval)

    # 接口尚未实现
    def get_history_trends(self, days):
        url = trading_interface.GetUrl_StockHistoryTrend(self.__stock_id, days)
        ret_json = trading_interface.GetHtml(url)
        self.history_trends = json.loads(ret_json)
        return 0

    # 得到股票的基本信息
    def get_info(self):
        url = trading_interface.GetUrl_StockInfo(self.__stock_id)
        ret_json = trading_interface.GetHtml(url)
        self.stock_info = json.loads(ret_json[1:-2])
        return 0


    def update(self) -> int:
        self.get_info()
        
        return 0