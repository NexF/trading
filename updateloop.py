import time

from updateobj  import UpdateObj
from typing     import List
from threading  import Thread


class UpdateLoop(Thread):
    target_update : List[UpdateObj] = []    # 保存一些指标信息
    pure_Update : List[UpdateObj] = []      # 保存一些纯需要更新的维度，比如股价、账户余额等

    def __init__(self, interval = 1) -> int:
        self.interval = interval
        self.__loop_counts = 0              # 更新次数的计数，有些指标或维度并不需要次次更新
        super().__init__()

    def add_obj(self, obj : UpdateObj):
        self.pure_Update.append(obj)
    def add_target(self, target : UpdateObj):
        self.target_update.append(target)

    def run(self) -> None:
        while(1):
            time.sleep(self.interval)
            self.__loop()
        
    def __loop(self):
        # 先处理pure_obj
        for pure_obj in self.pure_Update:
            if self.__loop_counts % pure_obj.interval != 0:
                continue

            if pure_obj.update() != 0:
                # 错误处理
                continue

        # 再处理target_obj，因为target可能依赖于pureobj
        for target_obj in self.target_update:
            if self.__loop_counts % target_obj.interval != 0:
                continue

            if target_obj.update() != 0:
                # 错误处理
                continue

        self.__loop_counts = self.__loop_counts + 1