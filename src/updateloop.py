import time

from updateobj  import UpdateObj
from threading  import Thread, Lock
from typing     import Dict

class UpdateLoop(Thread):
    service_update : Dict = dict()    # 保存一些指标信息
    obj_Update : Dict = dict()      # 保存一些纯需要更新的维度，比如股价、账户余额等

    def __init__(self, interval = 1) -> int:
        self.interval = interval            # 单位 秒
        self.__loop_counts = 0              # 更新次数的计数，有些指标或维度并不需要次次更新
        self.obj_idx = 0                    # 保存loop中存储对象的最大id，用于生成唯一id
        super().__init__()

    def add_obj(self, obj : UpdateObj):
        self.obj_Update[self.obj_idx] = obj
        obj.loop_idx = self.obj_idx
        self.obj_idx = self.obj_idx + 1
        return self.obj_idx - 1

    def add_service(self, target : UpdateObj):
        self.service_update[self.obj_idx] = target
        target.loop_idx = self.obj_idx
        self.obj_idx = self.obj_idx + 1
        return self.obj_idx - 1

    def del_any_idx(self, idx):
        if idx in self.obj_Update:
            self.obj_Update.pop(idx)
        elif idx in self.service_update:
            self.service_update.pop(idx)


    def del_any(self, obj : UpdateObj):
        self.del_any_idx(obj.loop_idx)


    def run(self) -> None:
        last_loop_time = time.time()
        while(1):
            if last_loop_time + self.interval <= time.time():
                last_loop_time = time.time()
                self.__loop()
    
    # TODO：采用异步方式实现
    def __loop(self):
        # 处理pure_obj list()防止循环的时候被修改
        for pure_obj in list(self.obj_Update.values()):
            if self.__loop_counts % pure_obj.interval != 0:
                continue
            
            if pure_obj.update() != 0:
                # 错误处理
                continue

        # 再处理target_obj，因为target可能依赖于pureobj
        for service_obj in list(self.service_update.values()):
            if self.__loop_counts % service_obj.interval != 0:
                continue

            if service_obj.update() != 0:
                # 错误处理
                continue

        self.__loop_counts = self.__loop_counts + 1