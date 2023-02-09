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
        
    def update(self) -> int:
        try:
            # 获取交易时需要的validatekey
            ret_json = interface.GetHtml(interface.UserInfoUrl, cookies = self.get_cookies())
            self.finance_info = json.loads(ret_json)
            ret_html = interface.GetHtml(interface.PositionUrl, cookies = self.get_cookies())
            doc = etree.HTML(ret_html)
            self.__validatekey = doc.xpath('//*[@id="em_validatekey"]/@value')[0]
        except json.decoder.JSONDecodeError as e:       # 如果登录状态失败
            self.refresh_cookies()
            return -101
        except:
            return -1

        logging.info(f"当前账户可用资金：{self.finance_info['Data'][0]['Kyzj']}")
        return 0