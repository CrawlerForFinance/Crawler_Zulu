#! /usr/bin/python2.7
# -*- coding: utf-8 -*-\

__author__ = "Wang Yuqi, Feng Letong"

import urllib, urllib2, cookielib, threading
import sys, string, time, os, re, json, Queue
import csv, argparse
from bs4 import BeautifulSoup
import socket
from tools_zulu import *
import requests

#global constant
DEBUG = False

#for crawl
urlHost = u'https://zh.zulutrade.com/'
urlStart = u'http://zh.zulutrade.com/'
urlNav = u'https://zh.zulutrade.com/traders'
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Host':'www.kickstarter.com', 'X-Requested-With':'XMLHttpRequest'}

titles = ([u"链接",u"编号",u'排名',u"类型",u"交易者",u'跟随资金总额', u"获利点数",u'头寸点数',u'星期',u'用户',u"交易", u"投资回报率/年率", u"每单平均盈利点数", u"胜出的交易",u"胜出的交易比例", u'平均交易时间', u'平均交易时间单位', u"最大亏损点数", u'最大亏损点数比例', u"最大持仓单数",u"最差的交易点数",u"最好的交易点数", u"是否有真实跟单账户",u"所需的最低资产净值",u"已被阅读次数"], [u"链接",u"编号",u'排名',u"类型",u"交易者", u"投资回报率/年率", u'跟随资金总额', u"获利", u'所需最低资金', u"胜出的交易比例", u'头寸', u'每单平均金额', u"最差头寸",u"最好头寸", u'星期',u'平均交易时间', u'平均交易时间单位', u'用户',u"最大开单数量",  u"是否有真实跟单账户"],[u"投资回报率", u"获利" ,u"所需最低资金", u"胜出的交易", u"头寸", u"每单的平均获利", u"每单的平均金额", u"最差头寸", u"星期", u"每单平均交易时间", u"每单平均交易时间单位", u"最大开单数量", u"用户", u"是否有真实跟单账户"])
sheetName = ['forex', 'binary']
#styleSum = [500000, 8000]
styleSum = [281245, 20]

#----------------------------------------------
def createWriters(filedirectory, typeNo):
    #writers = [] #csv writer list
    startTime = str(time.strftime('%Y%m%d', time.localtime(time.time())))
    name_sheet = filedirectory+sheetName[typeNo-1]+'_'+startTime+'.csv'
    try:
        file_sheet = open(name_sheet, 'wb')
        file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
    
        writer = csv.writer(file_sheet)
        writer.writerow(titles[typeNo-1])
    except Exception, e:
        raise e
    return writer
#----------------------------------------------
class getDataThread(threading.Thread):
    global writer, typeName
    def __init__(self, tId, urlQueue):
        threading.Thread.__init__(self)
        self.tId = tId
        self.q = urlQueue
    def run(self):
        while not exitFlag:
            queueLock.acquire()
            trade = self.q.get()
            #urlid = trade['id']
            #trade = self.q.get()
            queueLock.release()
            print("thread "+ str(self.tId) + ": "+ str(trade['id']))
            if typeName == "forex":
            	print "!!!!analysing forex...."
            	#url = urlHost + "trader/" + str(urlid) + '?t=30'
            	#print trade
            	#analyzeForexData(url, writer, typeName, trade)
                analyzeForexData(trade, writer, typeName)
            else:
            	print "!!!!analysing binary...."
            	#url = urlHost + "binary-trader/" + str(urlid) + '?t=10000'
            	#print trade
            	#analyzeBinaryData(url, writer, typeName, trade)
                analyzeBinaryData(trade, writer, typeName)
        #end while
#end class getDataThread
#----------------------------------------------
class getUrlQueueThread(threading.Thread):
    def __init__(self, tId, urlQueue, typeNo):
        threading.Thread.__init__(self)
        self.tId = tId
        self.q = urlQueue
        self.style = typeNo
    def run(self):
        global pageCount
        print "get into getUrlQueueThread: pageCount = " + str(pageCount)
        # get only active projects, need to be filterd
        typeFinish = False
        typeName = sheetName[typeNo-1]
        while pageCount <= 500:
        	pageLock.acquire()
        	pageCount += 1
        	if pageCount % 5 == 0:
        		print "get page " + str(pageCount) + "..."
        	if typeNo == 1:
	        	values = {"searchFilter":{"NotTradingExotics":'true',"TimeFrame":30,"Page":pageCount,"PageSize":20,"AffiliateId":24889,"SortExpression":"Ranking","SortDirection":"Ascending"}}
	        	pageUrl = "http://zh.zulutrade.com/webservices/performance.asmx/searchproviders"
    		else:
    			values = {"searchFilter":{"Page":pageCount,"PageSize":20,"SortExpression":"Ranking","SortDirection":"Ascending"}}
        		pageUrl = "http://zh.zulutrade.com/webservices/performancebinary.asmx/searchproviders"
        	pageLock.release()
        	#print values
        	headers = {'Content-Type':'application/json'}
        	#pageUrl = "http://zh.zulutrade.com/webservices/performancebinary.asmx/searchproviders"
        	try:
	        	r = requests.post(pageUrl, data = json.dumps(values), headers = headers,verify=False)
        		scriptData = r.json()
        		tradersList = scriptData['d']
        		if (len(tradersList) == 0):
        			break
        		queueLock.acquire()
        		for trade in tradersList:
        			#urlid = trade['id']
        			#if typeNo == 1:
	        		#	urlQueue.put(urlHost + "trader/" + str(urlid) + '?t=30')
    				#else:
    				#	urlQueue.put(urlHost + "binary-trader/" + str(urlid) + '?t=10000')
    				urlQueue.put(trade)
        		queueLock.release()
        	except socket.error as e:
        		print 'I am here'
        		print('[ERROR] Socket error: '+str(e.errno))
        		if str(e.errno.startswith('301')):
        			pageCount += 1
        			continue
        	
def test(page, typeName, writers):
	for i in xrange(2000):
		pageUrl = urlHost + "trader/" + str(page + i) + '?t=30'
		print pageUrl
		m = readFromUrl(pageUrl, headers = headers)
		if m is None:
			print 'no website'
			continue
		soup = BeautifulSoup(m, 'html.parser')
		main_content = soup.find('section', {'class':'main-content'})
		if main_content:
			tag_error = main_content('div', {'class':'static error general'})
			if tag_error:
				print "invalid:" + pageUrl
				continue
			noInfo = main_content('p',{'id':'main_PhNoStats'})
			if noInfo:
				print 'No new information in recent 1 month:' + pageUrl
				continue
			print "start analysing"
			if typeName == "forex":
				analyzeForexData(pageUrl, writers, typeName)
			else:
				analyzeBinaryData(pageUrl, writers, typeName)
		else:
			print "no content"
        i += 1  
        #end while
#end class getUrlQueueThread(threading.Thread):            
#----------------------------------------------
def getUrlQueue(typeNo):
    global urlQueue
    global urlNum
    urlNum = 0
    typeName = sheetName[typeNo-1]
    print("Start: get projects list in type "+typeName+"...")
    startTime = time.clock()
    threads = []
    
    for i in xrange(threadCount):
        thread = getUrlQueueThread(i, urlQueue, typeNo)
        threads.append(thread)
    print urlQueue.qsize()
    #print "over"
    # return
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    endTime = time.clock()
    print("Finish: get projects list in type "+typeName)
    print("Projects count: "+str(urlQueue.qsize()))
    print(u'time: '+str(endTime-startTime)+'s\n')
    #end while
#end getUrlQueue()
#---------------------------
def getInput():
    global typeNo
    while True:
        try:
            raw_typeNo = raw_input(u'Input type number(1 or 2, default=1):\n')
            typeNo = int(raw_typeNo)
            if typeNo < 1 or typeNo > 2:
                print('type number illegal! Please input again!')
                continue
            break
        except:
            if(raw_typeNo == ''):
                typeNo = 1
                break
            print('Not a number. Please input again!')
            continue

#----------------------------
#global variable
urlQueue = Queue.Queue()
exitFlag = 0
pageCount = -1 #已遍历的总量
threadCount = 8 #并发线程数
urlNum = 281241
typeNo = 1
writer = None
#----------------------------
#main
if __name__=='__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
    sys.setrecursionlimit(1000000)#设置递归调用深度
    
    #参数解析器
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-tn', '--typeno', action='store', dest='typeNo', help='Set Found Type, 1 for Forex and 2 for Binary')
    parser.add_argument('-t', '--threadcount', action='store', dest='threadCount', help='Set thread number', default=8)

    args = parser.parse_args()
    if(args.typeNo == None):
        getInput()
    else:
        typeNo = int(args.typeNo)
    threadCount = int(args.threadCount)
    
    filedirectory = getConfig()
    print 'try to log in!'
    #if login():
    
    print '------------INPUT INFORMATION---------------------'
    print '- type ='+ sheetName[typeNo - 1]
    print '- ThreadCount='+str(threadCount)
    print '------------INPUT INFORMATION---------------------'
    queueLock = threading.Lock()
    pageLock = threading.Lock()
    
    pageCount = -1
    getUrlQueue(typeNo)
    typeName = sheetName[typeNo - 1]
    print 'typeName:' + typeName
    subFolder = filedirectory+typeName+'/'
    print subFolder
    createFolder(subFolder)
    writer = createWriters(subFolder, typeNo)
    #test(pageCount, 'forex', writers)
    
    startTime = time.clock()
    print startTime
    threads = []
    for i in xrange(threadCount):
        thread = getDataThread(i+1, urlQueue)
        threads.append(thread)
        
    for t in threads:
        t.start()
    
    while not urlQueue.empty():
        pass
    
    exitFlag = 1
    
    for t in threads:
        t.join()
    print("Exiting Main Thread")
    endTime = time.clock()
    print(u'[Total execute time]:'+str(endTime-startTime)+'s')
    
    #login()
    