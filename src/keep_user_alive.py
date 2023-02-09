from updateloop import UpdateLoop
from user import User
from stock import Stock
import time
import interface
import json
loop = UpdateLoop(interval=1)
loop.setDaemon(True)        # 主线程结束以后子线程也退出
loop.start()

print("main thread\n")
user = User("eac060faf4004ac1a12e54604fa6f0a5")
user_id = loop.add_obj(user)

ret_json = interface.PostHtml(interface.GetUrl_GetOrderData(user.get_validatekey()),\
                                                            cookies = user.get_cookies(),\
                                                            )
ret = json.loads(ret_json)
time.sleep(60*60*24*365*10)     # 10年的keepalive
print("main thread\n")
