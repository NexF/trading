from updateobj import UpdateObj
import interface
import json

class Stock(UpdateObj):
    def __init__(self, stock_code, interval = 1):
        self.stock_code = stock_code
        super().__init__(interval)

    # 接口尚未实现
    def get_history_trends(self, days):
        url = interface.GetUrl_StockHistoryTrend(self.stock_code, days)
        ret_json = interface.GetHtml(url)
        self.history_trends = json.loads(ret_json)
        return 0

    # 得到股票的基本信息
    """
        {
            "code": "510050",
            "name": "上证50ETF",
            "sname": "50ETF",
            "topprice": "3.134",
            "bottomprice": "2.564",
            "status": 0,
            "fivequote": {
                "yesClosePrice": "2.849",
                "openPrice": "2.850",
                "sale1": "2.824",
                "sale2": "2.825",
                "sale3": "2.826",
                "sale4": "2.827",
                "sale5": "2.828",
                "buy1": "2.823",
                "buy2": "2.822",
                "buy3": "2.821",
                "buy4": "2.820",
                "buy5": "2.819",
                "sale1_count": 61790,
                "sale2_count": 31586,
                "sale3_count": 22103,
                "sale4_count": 13738,
                "sale5_count": 13891,
                "buy1_count": 2585,
                "buy2_count": 37367,
                "buy3_count": 44822,
                "buy4_count": 31311,
                "buy5_count": 23973
            },
            "realtimequote": {
                "open": "2.850",
                "high": "2.865",
                "low": "2.820",
                "avg": "2.834",
                "zd": "-0.026",
                "zdf": "-0.91%",
                "turnover": "3.27%",
                "currentPrice": "2.823",
                "volume": "6860602",
                "amount": "1944360640",
                "wp": "4177650",
                "np": "2682952",
                "time": "13:58:02"
            },
            "pricelimit": null,
            "tradeperiod": 0
        }
    """
    def get_info(self):
        url = interface.GetUrl_StockInfo(self.stock_code)
        ret_json = interface.GetHtml(url)
        self.stock_info = json.loads(ret_json[1:-2])
        return 0


    def update(self) -> int:
        self.get_info()
        
        return 0
