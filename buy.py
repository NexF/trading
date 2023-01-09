from action import Action
import trading_interface

# action是一次性的，action结束后就不会再update
# action默认update时间为10周期

class Buy(Action):
    # action有三个状态 初始化完成->发送请求完成（服务器处理中）->服务器处理完成
    
    def request(self) -> int:
        return 0

    def check_finished(self) -> int:
        return 0