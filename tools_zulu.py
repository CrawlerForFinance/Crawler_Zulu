#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Feng Letong"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from random import randint
import datetime
from dateutil.parser import parse
import pytz
import traceback
import re
import time
import requests
configfileName = 'config'
filedirectory = u'/Users/flt/Documents/remote_dir/ZuLu'
enable_proxy = True

#For login
urlHost = u'https://zh.zulutrade.com'
urlHost_s = u'http://zh.zulutrade.com'
urlLogin = 'https://zh.zulutrade.com/WebServices/User.asmx/Login'
urlIndex = u'https://zh.zulutrade.com/'

#for excel
headers={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Host':'www.kickstarter.com', 'X-Requested-With':'XMLHttpRequest'}

username = 'fengletong10@gmail.com'
password = 'MakeMoney'
#'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
ipAddress = ['191.234.5.2', '178.98.246.45, 231.67.9.23']
host = 'www.zh.zulutrade.com'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
#headers=[{'User-Agent': userAgent[0], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}, {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent': userAgent[1], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}, {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent': userAgent[2], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}]
HEADERS_NUMBER = 3

TRY_LOGIN_TIMES = 5 #尝试登录次数

#--------------------------------------------------
#读取配置文件，返回目标文件夹地址
def getConfig():
    global filedirectory, username, password, threadCount
    try:
        configfile = open(os.getcwd()+'/'+configfileName, 'r')
        #line = configfile.readline()
        pattern = re.compile(u'\s*(\w+)\s*=\s*(\S+)\s*')
        for line in configfile:
            #print line
            m = pattern.match(line)
            if m:
                if m.group(1) == u'filedirectory':
                    filedirectory =  m.group(2)+'/'
                elif m.group(1) == u'username':
                    username = m.group(2)
                elif m.group(1) == u'password':
                    password = m.group(2)
                elif m.group(1) == u'threadCount':
                    threadCount = m.group(2)
                #print filedirectory
        configfile.close()
    except:
        configfile = open(os.getcwd()+'/'+configfileName, 'wb')
        configfile.write('filedirectory = '+filedirectory+'\n')
        configfile.write('username = '+username+'\n')
        configfile.write('password = '+password+'\n')
        configfile.write('threadCount = '+threadCount+'\n')
        configfile.close()
        print('Create new config file!')
    
    createFolder(filedirectory)
    
    print('[CONFIG]')
    print('filedirectory = '+filedirectory)
    print('username = '+username)
    print('password = '+password)
    return filedirectory
#end def getConfig()
    
#--------------------------------------------------
#登录函数
def login():
    print('Logging in...')
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    tmp_headers = {'Content-Type':'application/json'}
    data = {'username':username, 'password':password};
    s = requests.Session()
    #tmp_headers = {'Content-Type':'JSON'}
    for i in range(TRY_LOGIN_TIMES):
        try:
            #print headers[randint(0, HEADERS_NUMBER-1)]
            #response = requests.post(urlLogin, json.dumps(data), headers=tmp_headers)
            
            response = s.post(urlLogin, json.dumps(data), headers=tmp_headers,verify=False)
            #req = urllib2.Request(urlLogin, postdata, getRandomHeaders())
            #result = urllib2.urlopen(req)
            scriptResult = response.json()
            print scriptResult
            result = scriptResult['d']['redirect']
            if result != "/user#dashboard": #通过返回url判断是否登录成功
                #print result.geturl()
                print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
                return False
            response.close()
            print "hello I'm heare!"
            #req2 = urllib2.Request(urlIndex, headers=getRandomHeaders())
            req2 = s.get(urlIndex,verify=False)
            #result2 = urllib2.urlopen(req2)
            #print result2.read()
            print("LOGIN SUCCESS!")
            
            tokenPage = s.get("https://zh.zulutrade.com/binary-trader/7192?t=10000",verify=False)
            html = tokenPage.text
            soup = BeautifulSoup(html, "html.parser")
            tokenTag = soup.find('input', {'name':'__RequestVerificationToken'})
            if tokenTag:
                token = tokenTag['value']
                print token
            exportUrl = 'https://zh.zulutrade.com/export.ashx?d=binaryprovidertrades&f=csv&c=&id=7192&df=1988-04-08&dt=2015-08-25&token='+token
            exportHeaders = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding':'gzip,deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8','Connection':'keep-alive'}
            exportData = {'d':'binaryprovidertrades','f':'csv','id':7192,'df':'1988-04-08','dt':'2015-08-25'}
            r = s.get(exportUrl,verify=False)
            with open("test.csv", "wb") as code:
                code.write(r.content)
            return True #登录成功
        except Exception, e:
            print e
            print(u'[FAIL]Login failed. Retrying...')
            #return False
    #end for
    print(u'[FAIL]login failed after retrying')
#end def login()

def exportFile(typeName, token, id, s):
    currentDate = getTime('%Y%m%d')
    #每个月一号下载所有的文件，不然只记录数据不下载
    if not currentDate.endswith("01"):
        print "not the 1st of the month, no need to download!!!!"
        return
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    timestart = datetime.date(yesterday.year, yesterday.month, 1)
    exportUrl = urlIndex+"export.ashx?d="
    if typeName == "forex":
        exportUrl += "providertrades"
    else:
        exportUrl += "binaryprovidertrades"
    exportUrl += "&f=csv&c=&id="+id + "&df=" + timestart.strftime("%Y-%m-%d") + "&dt=" + yesterday.strftime('%Y-%m-%d') + "&token="+token
    print exportUrl
    #s = requests.Session()
    r = s.get(exportUrl)
    with open("data/" + typeName+"/records/" + typeName+"_"+str(id)+"_"+currentDate+".csv","wb") as code:
        code.write(r.content)
#--------------------------------------------------
#查看文件夹是否存在：若不存在，则创建
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory) #可以创建多级目录
    return

#--------------------------------------------------
#从url读取response
def responseFromUrl(url, formdata = None, headers = None):
    response = None
    #here in kickstarter are all HTTPS
    '''
    proxy_handler = urllib2.ProxyHandler({"http": '186.238.51.149:8080'})
    if enable_proxy:
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    '''
    if formdata != None:
        formdata = urllib.urlencode(formdata)
    if headers == None:
        headers = getRandomHeaders()
    loopCount = 0
    while True:
        loopCount += 1
        if loopCount > 5:
            print('\nFailed when trying responseFromUrl():')
            print('  URL = '+url+'\n')
            break
        try:
            req = urllib2.Request(url, formdata, headers)
            response = urllib2.urlopen(req)
            curUrl = response.geturl()
            break
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('ERROR:'+str(e.code)+' '+str(e.reason))
                print e.code
                if (e.code == 301):
                    return None
                if(e.code == 429):
                    time.sleep(2)
                    continue
        except:
            print 'error: ' + url
            pass
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            #login()
            continue
    #end while
    
    return response

#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers
    
#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url, formdata = None, headers = None):
    response = responseFromUrl(url, formdata, headers)
    if response:
        m = response.read()
        response.close()
        return m
    else:
        return None
#end def readFromUrl

#--------------------------------------------------
def getTime(format = None):
    if format:
        strtime = str(time.strftime(format, time.localtime(time.time())))
    else:
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    return strtime

#--------------------------------------------------
def getWordNumber(str):
    list_word = str.split()
    return len(list_word)
    
#--------------------------------------------------
def cleanString(str):
    str = str.replace('\r\n', ' ')
    str = str.replace('\n', ' ')
    return str.strip()
#--------------------------------------------------
def analyzeForexData(tradeInfo, writers, typeName):
    url = urlHost + "/trader/" + str(tradeInfo['id']) + '?t=30'
#def analyzeForexData(url, writers,  typeName):
    global filedirectory
    print 'url:'+url
    s = requests.Session()
    try:
        tokenPage = s.get(url,verify=False)
    except:
        tokenPage = s.get(urlHost_s + "/trader/" + str(tradeInfo['id']) + "?t=30")
    html = tokenPage.text
    soup = BeautifulSoup(html, "html.parser")
    #webcontent = readFromUrl(url, headers=headers)
    #print webcontent
    #soup = BeautifulSoup(webcontent, "html.parser")
    buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d %H:%M:%S')
    #currentDate = getTime('%Y-%m-%d')
    #currentClock = getTime('%H:%M:%S')

    link = No = Rank = Type = trader = capital_sum = profit = position = week = customer_sum = trade = ROI = position_avg = win_trade = win_trade_percent = profit_avg = time_avg = time_unit = max_loss = max_loss_percent = max_position = worst_transaction = best_transaction = with_real_follower = lowest_net_assesst = read_times = ''
    link = url
    buffer1.append(link)
    No = url.split('/')[-1].split('?')[0]
    print 'No:' + No
    buffer1.append(No)
    RankTag = soup.find('strong', {'id':'main_LbRanking'})
    if RankTag:
        print "Rank:"+RankTag.text
        Rank = RankTag.text
    buffer1.append(Rank)
    Type = typeName
    print "type:" + Type
    buffer1.append(Type)
    sideBar = soup.find('div',{'id':'thi-content'})
    if sideBar:
        traderTAg = soup('h2',{'id':'main_HdName'})
        if traderTAg:
            trader = traderTAg[0].text
            print 'trader:' + trader
        buffer1.append(trader)
        capitalTag = soup('strong',{'id':'main_LbAmountFollowing'})
        if capitalTag:
            capital_sum = capitalTag[0].text
            print 'capital_sum:' + capital_sum
        buffer1.append(capital_sum)
        profitTag = soup('span',{'id':'main_LbStatsProfitPips'})
        if profitTag:
            profit = profitTag[0].text.split(' ')[0]
            print 'profit:' + profit + '点数'
        buffer1.append(profit)
        positionTag = soup('span',{'id':'main_LbStatsOpenProfit'})
        if positionTag:
            position = positionTag[0].text
        if position == "":
            position = tradeInfo[u'ppt']
        print 'position:' + position
        buffer1.append(position)
        weekTag = soup('span',{'id':'main_LbStatsAge'})
        if weekTag:
            week = weekTag[0].text
            print 'week:' + week
        buffer1.append(week)
        customer_sumTag = soup('span',{'id':'main_LbStatsFollowers'})
        if customer_sumTag:
            customer_sum = customer_sumTag[0].text
            print "customer_sum:" + customer_sum
        buffer1.append(customer_sum)
        tradeTag = soup('span',{'id':'main_LbStatsTrades'})
        if tradeTag:
            trade = tradeTag[0].text
            print 'trade:' + trade
        buffer1.append(trade)
        ROITag = soup('span',{'id':'main_lblROI'})
        if ROITag:
            ROI = ROITag[0].text
            print 'ROI:' + ROI
        buffer1.append(ROI)
        position_avgTag = soup('span',{'id':'main_LbStatsAvgPipsTrade'})
        if position_avgTag:
            position_avg = position_avgTag[0].text
            print 'position_avg:' + position_avg
        buffer1.append(position_avg)
        win_tradeTag = soup('span', {'id':'main_LbStatsWinTrades'})
        patt = re.compile(r"\((.*?)\)", re.I|re.X)
        if win_tradeTag:
            win_trade = win_tradeTag[0].text.split(' ')[0]
            win_trade_percent = patt.findall(win_tradeTag[0].text)
            print 'win_trade:' + win_trade + "    win_trade_percent:" + win_trade_percent[0]
        buffer1.append(win_trade)
        buffer1.append(win_trade_percent)
        time_avgTag = soup('span', {'id':'main_LbStatsAvgHoursTrade'})
        if time_avgTag:
            time_avg = time_avgTag[0].text.split(' ')[0]
            time_unit = ""
            if len(time_avgTag[0].text.split(" ")) > 1:
	            time_unit = time_avgTag[0].text.split(' ')[1]
            print 'time_avg:' + time_avg + " " + time_unit
        max_lossTag = soup('span', {'id':'main_LbStatsDrawdown'})
        buffer1.append(time_avg)
        buffer1.append(time_unit)
        if max_lossTag:
            max_loss_percent = max_lossTag[0].text.split(' ')[0]
            max_loss = patt.findall(max_lossTag[0].text)[0]
            print 'max_loss_percent:' + max_loss_percent + "    max_loss:" + max_loss
        buffer1.append(max_loss)
        buffer1.append(max_loss_percent)
        max_positionTag = soup('span', {'id':'main_LbStatsMaxOpenTrades'})
        if max_positionTag:
            max_position = max_positionTag[0].text
            print 'max_position:' + max_position
        buffer1.append(max_position)
        worst_transactionTag = soup('span', {'id':'main_LbStatsLow'})
        if worst_transactionTag:
            worst_transaction = worst_transactionTag[0].text.split(' ')[0]
            print 'worst_transaction:' + worst_transaction + '点数'
        buffer1.append(worst_transaction)
        best_transactionTag = soup('span', {'id':'main_LbStatsHigh'})
        if best_transactionTag:
            best_transaction = best_transactionTag[0].text.split(' ')[0]
            print 'best_transaction:' + best_transaction + "点数"
        buffer1.append(best_transaction)
        with_real_followerTag = soup('span', {'id':'main_LbStatsLive'})
        if with_real_followerTag:
            with_real_follower = with_real_followerTag[0].text
            print "有真实用户：" + with_real_follower
        buffer1.append(with_real_follower)
        lowest_net_assesstTag = soup('span', {'id':'main_LbStatsNME'})
        if lowest_net_assesstTag:
            lowest_net_assesst = lowest_net_assesstTag[0].text
            print "lowest_net_assesst:" + lowest_net_assesst
        buffer1.append(lowest_net_assesst)
        read_timesTag = soup('span', {'id': 'main_LbStatsVisits'})
        if read_timesTag:
            read_times = read_timesTag[0].text
            print 'read_times:' + read_times
        buffer1.append(read_times)
    writers.writerow(buffer1)
    tokenTag = soup.find('input', {'name':'__RequestVerificationToken'})
    if tokenTag:
        token = tokenTag['value']
        print "token:"+token
    exportFile(typeName, token, No, s)
    #-------------------------------------
#end analyzeData()
def analyzeBinaryData(trade, writers, typeName):
    url = urlHost + "/binary-trader/" + str(trade['id']) + '?t=10000'
#def analyzeBinaryData(url, writers,  typeName):
    global filedirectory
    print 'url:'+url
    #webcontent = readFromUrl(url, headers=headers)
    #print webcontent
    #soup = BeautifulSoup(webcontent, "html.parser")
    s = requests.Session()
    try:
        tokenPage = s.get(url,verify=False)
    except:
        tokenPage = s.get(urlHost_s + "/binary-trader/" + str(trade['id']) + "?t=10000")
    html = tokenPage.text
    soup = BeautifulSoup(html, "html.parser")
    buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d %H:%M:%S')
    #currentDate = getTime('%Y-%m-%d')
    #currentClock = getTime('%H:%M:%S')

    link = No = Rank = Type = trader = ROI = profit = lowest_assesst = position = week = customer_sum = profit_avg = win_trade_percent = capital_avg = time_avg = time_unit = max_order = with_real_follower = best_position = worst_position = ''
    link = url
    buffer1.append(link)
    No = url.split('/')[-1].split('?')[0]
    print 'No:' + No
    buffer1.append(No)
    RankTag = soup.find('strong', {'id':'main_LbRanking'})
    if RankTag:
        print "Rank:"+RankTag.text
        Rank = RankTag.text
    buffer1.append(Rank)
    Type = typeName
    print "type:" + Type
    buffer1.append(Type)
    sideBar = soup.find('div',{'id':'thi-content'})
    if sideBar:
        traderTAg = soup('h2',{'id':'main_HdName'})
        if traderTAg:
            trader = traderTAg[0].text
            print 'trader:' + trader
        buffer1.append(trader)
        ROITag = soup('strong',{'id':'main_LbStatsROI'})
        if ROITag:
            ROI = ROITag[0].text
            print 'ROI:' + ROI
        buffer1.append(ROI)
        profitTag = soup('span',{'id':'main_LbProfit'})
        if profitTag:
            profit = profitTag[0].text.split(' ')[0]
            print 'profit:' + profit + '点数'
        buffer1.append(profit)
        lowest_assesstTag = soup('span', {'id':'main_LbMinRequiredCapital'})
        if lowest_assesstTag:
            lowest_assesst = lowest_assesstTag[0].text
            print "lowest_assesst:" + lowest_assesst
        buffer1.append(lowest_assesst)
        win_tradeTag = soup('span', {'id':'main_LbStatsWinPercent'})
        if win_tradeTag:
            win_trade_percent = win_tradeTag[0].text
            print "win_trade_percent:" + win_trade_percent
        buffer1.append(win_trade_percent)
        positionTag = soup('span',{'id':'main_LbStatsTrades'})
        if positionTag:
            position = positionTag[0].text
            print 'position:' + position
        buffer1.append(position)
        profit_avgTag = soup('span', {'id':'main_LbStatsAverageProfitPerTrade'})
        if profit_avgTag:
            profit_avg = profit_avgTag[0].text
            print 'profit_avg:' + profit_avg
        buffer1.append(profit_avg)
        capital_avgTag = soup('span',{'id':'main_LblStatsAvgAmountPerPosition'})
        if capital_avgTag:
            capital_avg = capital_avgTag[0].text
            print 'capital_avg:' + capital_avg
        buffer1.append(capital_avg)
        worst_positionTag = soup('span', {'id':'main_LbStatsLow'})
        if worst_positionTag:
            worst_position = worst_positionTag[0].text
            print "worst_position:" + worst_position
        buffer1.append(worst_position)
        best_positionTag = soup('span', {'id':'main_LbStatsLow'})
        if best_positionTag:
            best_position = best_positionTag[0].text
            print "best_position:" + best_position
        buffer1.append(best_position)
        weekTag = soup('span',{'id':'main_LbStatsAge'})
        if weekTag:
            week = weekTag[0].text
            print 'week:' + week
        buffer1.append(week)
        time_avgTag = soup('span', {'id':'main_LbStatsAvgHoursTrade'})
        if time_avgTag:
            time_avg = time_avgTag[0].text.split(' ')[0]
            time_unit = time_avgTag[0].text.split(' ')[1]
            print 'time_avg:' + time_avg + " " + time_unit
        buffer1.append(time_avg)
        buffer1.append(time_unit)
        max_orderTag = soup('span', {'id':'main_LbStatsMaxOpenTrades'})
        if max_orderTag:
            max_order = max_orderTag[0].text
            print 'max_order:' + max_order
        buffer1.append(max_order)
        customer_sumTag = soup('span',{'id':'main_LbStatsFollowers'})
        if customer_sumTag:
            customer_sum = customer_sumTag[0].text
            print "customer_sum:" + customer_sum
        buffer1.append(customer_sum)
        with_real_followerTag = soup('span', {'id':'main_LbStatsLive'})
        if with_real_followerTag:
            with_real_follower = with_real_followerTag[0].text
            print "有真实用户：" + with_real_follower
        buffer1.append(with_real_follower)
    writers.writerow(buffer1)
    tokenTag = soup.find('input', {'name':'__RequestVerificationToken'})
    if tokenTag:
        token = tokenTag['value']
        print "token:"+token
    exportFile(typeName, token, No, s)
    #-------------------------------------
#end analyzeData()