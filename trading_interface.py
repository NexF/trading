from encodings.utf_8 import encode
import requests
from lxml import etree
import os
import json
import threading
import time

UserInfoUrl = "https://jywg.eastmoneysec.com/Com/queryAssetAndPositionV1"

# 得到url对应的html
def GetHtml(
    url,
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"},
    cookies = {},
    params = {}
):
    resp = requests.get(url,headers=headers, cookies=cookies, data = params)
    resp.encoding = 'utf-8'
    return resp.text
