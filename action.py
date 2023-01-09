from updateobj import UpdateObj

# action是一次性的，action结束后就不会再update
# action默认update时间为10周期

class Action(UpdateObj):
    # action有三个状态 初始化完成->发送请求完成（服务器处理中）->服务器处理完成
    INITED      = 0
    IN_PROCESS  = 1
    FINISHED    = 2
    def __init__(self, interval = 10):
        super().__init__(interval)
        self.status = self.INITED       # 初始化完成

    def update(self) -> int:
        if self.status == self.INITED:
            if self.request() == 0:     # 发送请求成功，则改变状态
                self.status = self.IN_PROCESS
        elif self.status == self.IN_PROCESS:
            if self.check_finished() == 0:
                self.status = self.FINISHED
        return 0
    
    def request(self) -> int:
        return 0

    def check_finished(self) -> int:
        return 0