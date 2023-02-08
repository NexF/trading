from updateobj import UpdateObj

# action是一次性的，action结束后就不会再update
# action默认update时间为10周期

class Action(UpdateObj):
    # action有三个状态 初始化完成->发送请求完成（服务器处理中）->服务器处理完成 （或 超时）
    INITED      = 0
    IN_PROCESS  = 1
    FINISHED    = 2
    OVERTIME    = 3
    ERROR       = 4
    def __init__(self, timeout = 100, interval = 10):
        super().__init__(interval)
        self.status = self.INITED       # 初始化完成
        self.__timeout = timeout
        self.__used_time    = 0
    def update(self) -> int:
        self.__used_time = self.__used_time + self.interval
        if self.status == self.INITED:
            ret = self.request()
            if ret == 0:     # 发送请求成功，则改变状态
                self.status = self.IN_PROCESS
            else:
                self.status = self.ERROR

        elif self.status == self.IN_PROCESS:
            if self.check_finished() == 0:  # 服务器处理完成，改变状态
                self.status = self.FINISHED
        if self.__used_time >= self.__timeout and self.status != self.OVERTIME and self.status != self.ERROR:  # 超时
            self.status = self.OVERTIME
            self.overtimed()

        return 0
    
    def request(self) -> int:
        return 0

    def check_finished(self) -> int:
        return 0

    def overtimed(self) -> int:
        return 0