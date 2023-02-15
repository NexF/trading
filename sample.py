# -*- coding: utf-8 -*-

from iFinDPy import *
from datetime import datetime
import pandas as pd
import time as _time
import json
from threading import Thread,Lock,Semaphore
import requests

sem = Semaphore(5)  # 此变量用于控制最大并发数
dllock = Lock()  #此变量用来控制实时行情推送中落数据到本地的锁

# 登录函数
def thslogindemo():
    # 输入用户的帐号和密码
    thsLogin = THS_iFinDLogin("**","**")
    print(thsLogin)
    if thsLogin != 0:
        print('登录失败')
    else:
        print('登录成功')

def datepool_basicdata_demo():
    # 通过数据池的板块成分函数和基础数据函数，提取沪深300的全部股票在2020-11-16日的日不复权收盘价
    data_hs300 = THS_DP('block', '2018-11-16;001005290', 'date:Y,thscode:Y,security_name:Y')
    if data_hs300.errorcode != 0:
        print('error:{}'.format(data_hs300.errmsg))
    else:
        seccode_hs300_list = data_hs300.data['THSCODE'].tolist()
        data_result = THS_BD(seccode_hs300_list, 'ths_close_price_stock', '2020-11-16,100')
        if data_result.errorcode != 0:
            print('error:{}'.format(data_result.errmsg))
        else:
            data_df = data_result.data
            print(data_df)

def datapool_realtime_demo():
    # 通过数据池的板块成分函数和实时行情函数，提取上证50的全部股票的最新价数据,并将其导出为csv文件
    today_str = datetime.today().strftime('%Y-%m-%d')
    print('today:{}'.format(today_str))
    data_sz50 = THS_DP('block', '{};001005260'.format(today_str), 'date:Y,thscode:Y,security_name:Y')
    if data_sz50.errorcode != 0:
        print('error:{}'.format(data_sz50.errmsg))
    else:
        seccode_sz50_list = data_sz50.data['THSCODE'].tolist()
        data_result = THS_RQ(seccode_sz50_list,'latest')
        if data_result.errorcode != 0:
            print('error:{}'.format(data_result.errmsg))
        else:
            data_df = data_result.data
            print(data_df)
            data_df.to_csv('realtimedata_{}.csv'.format(today_str))

def iwencai_demo():
    # 演示如何通过不消耗流量的自然语言语句调用常用数据
    print('输出资金流向数据')
    data_wencai_zjlx = THS_WC('主力资金流向', 'stock')
    if data_wencai_zjlx.errorcode != 0:
        print('error:{}'.format(data_wencai_zjlx.errmsg))
    else:
        print(data_wencai_zjlx.data)

    print('输出股性评分数据')
    data_wencai_xny = THS_WC('股性评分', 'stock')
    if data_wencai_xny.errorcode != 0:
        print('error:{}'.format(data_wencai_xny.errmsg))
    else:
        print(data_wencai_xny.data)

def dlwork(tick_data):
    # 本函数为实时行情订阅新启线程的任务函数
    dllock.acquire()
    with open('dlwork.txt', 'a') as f:
        for stock_data in tick_data['tables']:
            if 'time' in stock_data:
                timestr = _time.strftime('%Y-%m-%d %H:%M:%S', _time.localtime(stock_data['time'][0]))
                print(timestr)
                f.write(timestr + str(stock_data) + '\n')
            else:
                pass
    dllock.release()

def work(codestr,lock,indilist):
    sem.acquire()
    stockdata = THS_HF(codestr, ';'.join(indilist),'','2020-08-11 09:15:00', '2020-08-11 15:30:00','format:json')
    if stockdata.errorcode != 0:
        print('error:{}'.format(stockdata.errmsg))
        sem.release()
    else:
        print(stockdata.data)
        lock.acquire()
        with open('test1.txt', 'a') as f:
            f.write(str(stockdata.data) + '\n')
        lock.release()
        sem.release()

def multiThread_demo():
    # 本函数为通过高频序列函数,演示如何使用多线程加速数据提取的示例,本例中通过将所有A股分100组,最大线程数量sem进行提取
    # 用户可以根据自身场景进行修改
    today_str = datetime.today().strftime('%Y-%m-%d')
    print('today:{}'.format(today_str))
    data_alla = THS_DP('block', '{};001005010'.format(today_str), 'date:Y,thscode:Y,security_name:Y')
    if data_alla.errorcode != 0:
        print('error:{}'.format(data_alla.errmsg))
    else:
        stock_list = data_alla.data['THSCODE'].tolist()

    indi_list = ['close', 'high', 'low', 'volume']
    lock = Lock()

    btime = datetime.now()
    l = []
    for eachlist in [stock_list[i:i + int(len(stock_list) / 10)] for i in
                     range(0, len(stock_list), int(len(stock_list) / 10))]:
        nowstr = ','.join(eachlist)
        p = Thread(target=work, args=(nowstr, lock, indi_list))
        l.append(p)

    for p in l:
        p.start()
    for p in l:
        p.join()
    etime = datetime.now()
    print(etime-btime)

pd.options.display.width = 320
pd.options.display.max_columns = None


def reportDownload():
    df = THS_ReportQuery('300033.SZ','beginrDate:2021-08-01;endrDate:2021-08-31;reportType:901','reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y').data
    print(df)
    for i in range(len(df)):
        pdfName = df.iloc[i,4]+str(df.iloc[i,6])+'.pdf'
        pdfURL = df.iloc[i,5]
        r = requests.get(pdfURL)
        with open(pdfName,'wb+') as f:
            f.write(r.content)


def main():
    # 本脚本为数据接口通用场景的实例,可以通过取消注释下列示例函数来观察效果

    # 登录函数
    thslogindemo()
    # 通过数据池的板块成分函数和基础数据函数，提取沪深300的全部股票在2020-11-16日的日不复权收盘价
    datepool_basicdata_demo()
    #通过数据池的板块成分函数和实时行情函数，提取上证50的全部股票的最新价数据,并将其导出为csv文件
    # datapool_realtime_demo()
    # 演示如何通过不消耗流量的自然语言语句调用常用数据
    # iwencai_demo()
    # 本函数为通过高频序列函数,演示如何使用多线程加速数据提取的示例,本例中通过将所有A股分100组,最大线程数量sem进行提取
    # multiThread_demo()
    data = THS_HF('300033.SZ,600030.SH','open;high;low;close','CPS:no,baseDate:1900-01-01,Fill:Omit,Interval:1','2022-12-09 09:30:00','2022-12-09 09:40:00')
    print(data.data)
    # 本函数演示如何使用公告函数提取满足条件的公告，并下载其pdf
    # reportDownload()

if __name__ == '__main__':
    main()