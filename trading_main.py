from updateloop import UpdateLoop
from user import User
import time
loop = UpdateLoop(1)
loop.setDaemon(True)        # 主线程结束以后子线程也退出
loop.start()

print("main thread\n")
loop.add_obj(User("f51a80e6948f456eade448dcc7a32395",30))

time.sleep(50000)
print("main thread\n")
