from updateobj import UpdateObj
from auto_login import login
from lxml import etree
import interface
import json
import logging


class User(UpdateObj):
    def __init__(self, uuid, interval = 10):
        self.__uuid = uuid
        self.update()                   # 在最开始就update一次，防止最开始交易失败
        super().__init__(interval)

    def __init__(self, user, passwd, interval = 10):

        self.__user = user
        self.__passwd = passwd

        self.refresh_cookies()

        self.update()                   # 在最开始就update一次，防止最开始交易失败
        super().__init__(interval)

    def refresh_cookies(self):
        try:
            cookies = -1
            # 轮询直到获得cookie
            while cookies == -1:
                cookies = login(user=self.__user, passwd=self.__passwd)

            for item in cookies:
                if item['name'] == 'Uuid':
                    self.__uuid = item['value']
                    break
        except AttributeError as e:
            pass

    def get_cookies(self):
        cookies = {
            "Uuid":self.__uuid
        }
        return cookies

    def get_validatekey(self):
        return self.__validatekey

    '''
    {
    "Bz": "RMB",
    "Cbjg": "2.673",
    "Cbjgex": "2.725",
    "Ckcb": "16305.12",
    "Ckcbj": "2.673",
    "Ckyk": "530.88",
    "Cwbl": "0.25724",
    "Djsl": "0",
    "Dqcb": "16620.21",
    "Dryk": "",
    "Drykbl": "",
    "Gddm": "A676723659",
    "Gfmcdj": "0",
    "Gfmrjd": "0",
    "Gfssmmce": "0",
    "Gfye": "6100",
    "Jgbm": "5408",
    "Khdm": "540860216117",
    "Ksssl": "6100",
    "Kysl": "6100",
    "Ljyk": "530.88",
    "Market": "HA",
    "Mrssc": "0",
    "Sssl": "0",
    "Szjsbs": "1",
    "Ykbl": "0.032548",
    "Zjzh": "540860216117",
    "Zqdm": "510050",
    "Zqlx": "E",
    "Zqlxmc": "E",
    "Zqmc": "50ETF",
    "Zqsl": "6100",
    "Ztmc": "0",
    "Ztmr": "0",
    "Zxjg": "2.760",
    "Zxsz": "16836.00",
    "zqzwqc": "上证50ETF"
    }
    '''
    # 得到当前账户的持仓数据
    def get_holding_stocksinfo(self):
        return self.finance_info['Data'][0]['positions']

    def get_holding_stockinfo(self, stockID):
        for stock in self.finance_info['Data'][0]['positions']:
            if stock['Zqdm'] == stockID:
                return stock
        return -1

    # 得到当前账户的总资产
    def get_totalassets(self):
        return self.finance_info['Data'][0]['Zzc']

    # 得到当前账户的可用资产
    def get_availableassets(self):
        return self.finance_info['Data'][0]['Kyzj']
    
    def update(self) -> int:
        try:
            # 获取交易时需要的validatekey
            ret_json = interface.GetHtml(interface.UserInfoUrl, cookies = self.get_cookies())
            self.finance_info = json.loads(ret_json)
            ret_html = interface.GetHtml(interface.PositionUrl, cookies = self.get_cookies())
            doc = etree.HTML(ret_html)
            self.__validatekey = doc.xpath('//*[@id="em_validatekey"]/@value')[0]
        except json.decoder.JSONDecodeError as e:       # 如果登录状态失败
            logging.exception(f"{e.msg}")
            self.refresh_cookies()
            return -101
        except:
            logging.exception(f"更新用户信息失败")
            return -1

        logging.info(f"当前账户可用资金：{self.finance_info['Data'][0]['Kyzj']}，总资产：{self.finance_info['Data'][0]['Zzc']}")
        return 0