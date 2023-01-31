import interface
from lxml import etree

params = {
    "stockCode": "510050",
    "price": "2.8",
    "amount": "100000",
    "tradeType": "S",           # 买卖类型 B：买  S：卖
    # "zqmc": "上证50ETF",
    # "market": "HA",
}

cookies = {
    "Uuid":"56bac1a6b3034768adb2176a39d21dc5"
}

str = interface.PostHtml("https://jywg.eastmoneysec.com/Trade/SubmitTradeV2?validatekey=456fe2d4-37cc-414c-b759-33f9a0e58efa", cookies=cookies,params=params)
print(str)
# //*[@id="em_validatekey"]