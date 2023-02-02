import json
from redis import Redis         # 用来存储交易数据，做一个先进后出的交易数据栈


# 通过redis实现一个持久化栈
class PStack:
    def __init__(self, stackname, redis_host='127.0.0.1', redis_port=6379) -> None:
        self.__client = Redis(host=redis_host, port=redis_port)
        self.__LIST_NAME = stackname

    def _push(self, obj):
        self.__client.lpush(self.__LIST_NAME, json.dumps(obj))
    
    def _pop(self):
        return self.__client.lpop(self.__LIST_NAME)
    
    def _get_top(self):
        return self.__client.lindex(self.__LIST_NAME, 0)

    def _get_len(self):
        return self.__client.llen(self.__LIST_NAME)