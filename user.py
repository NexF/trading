from updateobj import UpdateObj
import trading_interface
import json

class User(UpdateObj):
    def __init__(self, uuid, interval = 1):
        self.__uuid = uuid
        super().__init__(interval)

    def getcookies(self):
        cookies = {
            "Uuid":self.__uuid
        }
        return cookies

    def update(self) -> int:
        try:
            ret_json = trading_interface.GetHtml(trading_interface.UserInfoUrl, cookies = self.getcookies())
            finance_info = json.loads(ret_json)
        except:
            return -1

        print(finance_info['Data'][0]['Kyzj'])
        return 0