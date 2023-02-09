import time

from updateobj  import UpdateObj
from threading  import Thread, Lock
from typing     import Dict

class UpdateLoop(Thread):
    target_update : Dict = dict()    # 保存一些指标信息
    pure_Update : Dict = dict()      # 保存一些纯需要更新的维度，比如股价、账户余额等

    def __init__(self, interval = 1) -> int:
        self.interval = interval            # 单位 秒
        self.__loop_counts = 0              # 更新次数的计数，有些指标或维度并不需要次次更新
        self.obj_idx = 0                    # 保存loop中存储对象的最大id，用于生成唯一id
        super().__init__()

    def add_obj(self, obj : UpdateObj):
        self.pure_Update[self.obj_idx] = obj
        obj.loop_idx = self.obj_idx
        self.obj_idx = self.obj_idx + 1
        return self.obj_idx - 1

    def add_target(self, target : UpdateObj):
        self.target_update[self.obj_idx] = target
        target.loop_idx = self.obj_idx
        self.obj_idx = self.obj_idx + 1
        return self.obj_idx - 1

    def del_any_idx(self, idx):
        if idx in self.pure_Update:
            self.pure_Update.pop(idx)
        elif idx in self.target_update:
            self.target_update.pop(idx)


    def del_any(self, obj : UpdateObj):
        self.del_any_idx(obj.loop_idx)


    def run(self) -> None:
        last_loop_time = time.time()
        while(1):
            if last_loop_time + self.interval <= time.time():
                last_loop_time = time.time()
                self.__loop()
        
    def __loop(self):
        # 处理pure_obj list()防止循环的时候被修改
        for pure_obj in list(self.pure_Update.values()):
            if self.__loop_counts % pure_obj.interval != 0:
                continue
            
            if pure_obj.update() != 0:
                # 错误处理
                continue

        # 再处理target_obj，因为target可能依赖于pureobj
        for target_obj in list(self.target_update.values()):
            if self.__loop_counts % target_obj.interval != 0:
                continue

            if target_obj.update() != 0:
                # 错误处理
                continue

        self.__loop_counts = self.__loop_counts + 1