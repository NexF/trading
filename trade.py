from action import Action
import interface
import time
import json
# action是一次性的，action结束后就不会再update
# action默认update时间为10周期

class Trade(Action):
    __params = {
        "stockCode": "510050",
        "price": "2.75",
        "amount": "1000",
        "tradeType": "B",           # 买卖类型 B：买  S：卖
        # "zqmc": "上证50ETF",
        # "market": "HA",
    }

    __return_info = 0

    # action有三个状态 初始化完成->发送请求完成（服务器处理中）->服务器处理完成
    def __init__(self, user, stock, trade_type, amount, price=-1, timeout = 10, interval=1):
        self.__user = user
        self.__stock = stock
        self.__price = price
        self.__trade_type = trade_type
        self.__amount = amount
        super().__init__(timeout = timeout,interval = interval)

    def request(self) -> int:
        # try:
        self.__params["stockCode"] = self.__stock.stock_code
        self.__params["tradeType"] = self.__trade_type
        if self.__price == -1:
            self.__price = self.__stock.stock_info['realtimequote']['currentPrice']
        self.__params["price"] = self.__price
        ret_json = interface.PostHtml(interface.GetUrl_Trade(self.__user.get_validatekey()),\
                                                                            cookies = self.__user.get_cookies(),\
                                                                            params=self.__params)

        """
            {
                "Status": 0,
                "Count": 1,
                "Data": [
                    {
                        "Htxh": "1450028353",
                        "Wtbh": "674351"
                    }
                ],
                "Errcode": 0
            }
        """
        ret = json.loads(ret_json)
        # except:
        #     return -1
        
        # 如果请求成功，则保存该笔委托的信息
        if ret["Status"] == 0:
            self.__return_info = ret
            return 0
        
        return -100

    def check_finished(self) -> int:
        ret_json = interface.PostHtml(interface.GetUrl_GetOrderData(self.__user.get_validatekey()), cookies = self.__user.get_cookies())
        ret = json.loads(ret_json)
        """
        {
            "Message": null,
            "Status": 0,
            "Data": [
                {
                    "Wtsj": "141020",
                    "Zqdm": "510050",
                    "Zqmc": "50ETF",
                    "Mmsm": "证券买入",
                    "Mmlb": "B",
                    "Wtsl": "1000",
                    "Wtzt": "已报",
                    "Wtjg": "2.750",
                    "Cjsl": "0",
                    "Cjje": ".00",
                    "Cjjg": "0.000000",
                    "Market": "HA",
                    "Wtbh": "674351",
                    "Gddm": "A676723659",
                    "Dwc": "",
                    "Qqhs": null,
                    "Wtrq": "20230131",
                    "Wtph": "674351",
                    "Khdm": "540860216117",
                    "Khxm": "陈刘柱",
                    "Zjzh": "540860216117",
                    "Jgbm": "5408",
                    "Bpsj": "141020",
                    "Cpbm": "",
                    "Cpmc": "",
                    "Djje": "2750.50",
                    "Cdsl": "0",
                    "Jyxw": "53198",
                    "Cdbs": "F",
                    "Czrq": "20230131",
                    "Wtqd": "9",
                    "Bzxx": "",
                    "Sbhtxh": "1450028353",
                    "Mmlb_ex": "B",
                    "Mmlb_bs": "B"
                },
                {
                    "Wtsj": "133743",
                    "Zqdm": "510050",
                    "Zqmc": "50ETF",
                    "Mmsm": "证券买入",
                    "Mmlb": "B",
                    "Wtsl": "5200",
                    "Wtzt": "已报",
                    "Wtjg": "2.564",
                    "Cjsl": "0",
                    "Cjje": ".00",
                    "Cjjg": "0.000000",
                    "Market": "HA",
                    "Wtbh": "615512",
                    "Gddm": "A676723659",
                    "Dwc": "20230131|615512",
                    "Qqhs": null,
                    "Wtrq": "20230131",
                    "Wtph": "615512",
                    "Khdm": "540860216117",
                    "Khxm": "陈刘柱",
                    "Zjzh": "540860216117",
                    "Jgbm": "5408",
                    "Bpsj": "133743",
                    "Cpbm": "",
                    "Cpmc": "",
                    "Djje": "13335.20",
                    "Cdsl": "0",
                    "Jyxw": "53198",
                    "Cdbs": "F",
                    "Czrq": "20230131",
                    "Wtqd": "9",
                    "Bzxx": "",
                    "Sbhtxh": "1450025674",
                    "Mmlb_ex": "B",
                    "Mmlb_bs": "B"
                }
            ]
        }
        """
        for order in ret['Data']:
            # 遍历返回值，找到此次交易的委托编号
            if order['Wtph'] == self.__return_info['Data'][0]['Wtbh']:
                self.order_info = order
                if int(order['Wtsl']) == order['Cjsl']:     # 如果委托数量等于成交数量则保存当前委托信息并返回0
                    return 0
                break
        return -100

    #  超时就撤单
    def overtimed(self) -> int:
        revoke_param = {"revokes":"20230201_3169"}
        revoke_param["revokes"] = "%s_%s"%(self.order_info['Wtrq'], self.order_info['Wtph'])
        ret_json = interface.PostHtml(interface.GetUrl_RevokeOrders(self.__user.get_validatekey()),\
                                                                            cookies = self.__user.get_cookies(),\
                                                                            params=revoke_param)

        return 0