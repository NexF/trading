from updateobj import UpdateObj
import interface
import json
from lxml import etree

class User(UpdateObj):
    def __init__(self, uuid, interval = 10):
        self.__uuid = uuid
        self.update()                   # 在最开始就update一次，防止最开始交易失败
        super().__init__(interval)

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
            ret_html = interface.GetHtml(interface.PositionUrl, cookies = self.get_cookies())
            doc = etree.HTML(ret_html)
            self.__validatekey = doc.xpath('//*[@id="em_validatekey"]/@value')[0]


            ret_json = interface.GetHtml(interface.UserInfoUrl, cookies = self.get_cookies())
            finance_info = json.loads(ret_json)
        except:
            return -1

        print(finance_info['Data'][0]['Kyzj'])
        return 0