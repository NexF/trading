from encodings.utf_8 import encode
import requests
# from lxml import etree
import os
import json
import threading
import time

UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"


UserInfoUrl = "https://jywg.eastmoneysec.com/Com/queryAssetAndPositionV1"
StockInfoUrl = "https://hsmarketwg.eastmoney.com/api/SHSZQuoteSnapshot?id=600022&callback="
# 得到股票的基本信息
def GetUrl_StockInfo(stock_id):
    return "https://hsmarketwg.eastmoney.com/api/SHSZQuoteSnapshot?id=%s&callback="%(stock_id)

# 得到股票的基本信息
def GetUrl_BuyStock(stock_id):
    return "https://jywg.eastmoneysec.com/Trade/SubmitTradeV2?validatekey=8ab67df8-4e3d-4c47-ab38-e8c993c20c6a"


# 得到股票的历史价格走势
def GetUrl_StockHistoryTrend(stock_id, days):
    if days >=1 and days <= 5:
        return "https://66.push2his.eastmoney.com/api/qt/stock/trends2/sse?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f17&fields2=f51,f52,f53,f54,f55,f56,f57,f58&secid=%s&ndays=%d"%(stock_id, days)
    return -1

# 得到url对应的html
def GetHtml(
    url,
    headers = {"user-agent": UserAgent},
    cookies = {},
    params = {}
):
    resp = requests.get(url,headers=headers, cookies=cookies, data = params)
    resp.encoding = 'utf-8'
    return resp.text

# 得到url对应的html
def PostHtml(
    url,
    headers = {"user-agent": UserAgent},
    cookies = {},
    params = {}
):
    resp = requests.post(url,headers=headers, cookies=cookies, data = params)
    resp.encoding = 'utf-8'
    return resp.text
