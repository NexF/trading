from updateloop import UpdateLoop
from user import User
from stock import Stock
import time
loop = UpdateLoop(1)
loop.setDaemon(True)        # 主线程结束以后子线程也退出
loop.start()

print("main thread\n")
# loop.add_obj(User("5001820e00b748bebcadc4d6027e1445",2))
loop.add_obj(Stock("510050"))

time.sleep(50000)
print("main thread\n")
