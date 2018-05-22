# -*- coding: utf-8 -*-
"""
Created on Fri Aug  04 09:02:41 2017

@author: Jacklin
@Crawler: 139 Mail
"""

import base64
import json
import re
import time
import datetime

from bs4 import BeautifulSoup
import requests
import traceback

from urllib.parse import quote
from math import ceil
# from pip._vendor.distlib.compat import raw_input
from _ast import slice, Str
from builtins import str, int
from math import ceil, floor
from _operator import rshift

from datetime import date

from urllib import parse
#from pip._vendor.distlib.compat import raw_input

    
class Crawler():
    
    #初始化配置信息
    def initCfg(self, params):
        if 'cfg' not in params.keys():
            return
        
        try:
            cfg = json.loads(params['cfg'])
            if 'serviceUrl' in cfg.keys():
                self.crawlerServiceUrl = cfg['serviceUrl']
            if 'logUrl' in cfg.keys():
                self.uploadExceptionUrl = cfg['logUrl']
        except Exception:
            return
    
    def init( self, params = None ):
        print ('139 Mail start to init.......')
        #防止重复初始化覆盖新值
        if not hasattr(self, 'crawlerServiceUrl'):
            self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        if not hasattr(self, 'uploadExceptionUrl'):
            self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        #self.uploadDataUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        #self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        #self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        self.session = requests.Session()
        
        if params :
            self.initCfg(self, params)  
            
        data = {
            'status':'true',
            'again':'true',
            'step':'0',
            'words':[
                {'ID':'UserId','index': 0,'needUserInput':'true', 'label':'用户名或 身份证号', 'type': 'text'},
                {'ID':'password','index': 1,'needUserInput':'true', 'label':'网银密码', 'type': 'password'}
            ]
        }
        return data
    
    def uploadData(self, data):
        #print(data)
        #上传数据到服务器
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        try:
            postData = {
                'heade':{'code':'uploadPersonalBankData','token':'','timestamp':''},
                'body':{
                    'attach':'',
                    'content':data
                }
            }
#             print('uploadData-->[post] PINGAN data to ' + self.crawlerServiceUrl)
            resp = requests.post(self.crawlerServiceUrl, headers = headers, data = {'content':json.dumps(postData, ensure_ascii=False)})
            respText = resp.text;
            #print(resp.text)
            respObj = json.loads(str(resp.text).strip(), encoding = 'utf-8')
            if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
                return True
            else :
                Crawler.uploadException(self, username=self.UserId, step='uploadData', errmsg=respText)
                return False
        except Exception:
            print('uploadData-->[post]  data error, ' + self.crawlerServiceUrl)
            respText = traceback.format_exc()
            Crawler.uploadException(self, username=self.UserId, step='5', errmsg=respText)
            return False
   
        
    #上传异常信息
    def uploadException(self, username = '', step = '', errmsg = ''):
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'139mail','login_account':username}
        try:
            if(self.DEBUG_LOCAL == False):
                requests.post(self.uploadExceptionUrl, headers = headers, data = {'content':json.dumps(data, ensure_ascii=False)})
        except:
            print('uploadException-->[post] exception error')
            
    
    
    def doCapture(self, jsonParams) :
        try:
            return Crawler.doCapture1(self, jsonParams)
        except Exception:
            respText = traceback.format_exc()
            Crawler.uploadException( self, username = '', step = 'doCapture', errmsg = respText+'#'+jsonParams)
            returnData = Crawler.init(self, jsonParams)
            returnData['msg'] = '系统繁忙,请稍后再试,code:139'
            return returnData
    
    def doCapture1( self , jsonParams):
        self.DEBUG_LOCAL = False
        print('139 Mail start to capture with ID............')
        self.params = json.loads(jsonParams, encoding='utf-8')
        self.jsonParams = jsonParams
        try :
            #print(self.params)
            self.flowNo = self.params['flowNo']
            self.UserId = self.params['UserId']
            self.password = self.params['password']
            
            if( self.UserId.find('@') != -1):
                regexp = re.compile(r'(.*?)@')
                regexpstr = re.findall(regexp, self.UserId)
                self.UserId = regexpstr[0]
            
            if('debug' in self.params.keys()):
                self.DEBUG_LOCAL = True
            
            self.result_info = {}
            self.result_info['flow_no'] =  self.flowNo
            self.result_info['mailType'] = '139.com'
            
            Crawler.uploadException(self, self.UserId, 'docapture1', 'init-'+str(self.UserId)+'-'+str(self.password))
            
            data = Crawler.loadLoginPage(self)
            if( data['success1'] == True):
                data = Crawler.doLogin(self)
                if( data['success1'] == True):
                    data = Crawler.getMessageList(self)
                    if( data['success1'] == True ):
                        data = Crawler.getContactList(self)
                        if( data['success1'] == True ):
                            data = Crawler.getLoginDetails(self)
                            if(data['success1'] == True ):
                                return Crawler.doUpload(self)
                            else:
                                return data
                        else:
                            return data
                    else:
                        return data
                else:
                    return data
            else:
                return data
            
        except Exception :
#             print ('do capture fail' +traceback.format_exc())
            respText = traceback.format_exc()
            Crawler.uploadException(self , username='' , step=self.para['step'] , errmsg=respText + '#' + jsonParams)
            returnData = Crawler.init( self )
            returnData['status'] = 'false'
            returnData['msg'] = '系统异常,请稍后重试,code:100.'
            return returnData
        
    def loadLoginPage(self):
        try:
            print('loadLoginPage')
            
            mailUrl = 'http://mail.10086.cn/'
            mailHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'mail.10086.cn',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            mailResp = self.session.get( mailUrl, headers = mailHeader, allow_redirects = True)
#             print(mailResp.text)
            
            returnData = {
                'msg' : '',
                'success1' : True
                }
            
            return returnData
        except Exception:
            respText = traceback.format_exc()
#             print(respText)
            Crawler.uploadException(self , username='' , step=self.para['step'] , errmsg=respText )
            returnData = Crawler.init( self )
            returnData['status'] = 'false'
            returnData['msg'] = '系统异常,请稍后重试,code:100.'
            returnData['success1'] = False
            return returnData
        
    def doLogin(self):
        try:
            print('doLogin')
            returnData = {
                'msg' : '',
                'success1' : True
                }
            
            rsa = mailEncrypt()
            encPassword = rsa.calcDigest("fetion.com.cn:" + self.password)
            print(encPassword)
            
            loginUrl = 'https://mail.10086.cn/Login/Login.ashx?_fv=4&cguid=1656046312813&_=3c0af1f8d3158b08a440d3ba2201184659d5a1eb&resource=indexLogin'
            loginHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Cache-Control':'max-age=0',
                    'Connection':'keep-alive',
                    'Content-Length':'128',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'mail.10086.cn',
                    'Origin':'http://mail.10086.cn',
                    'Referer':'http://mail.10086.cn/',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            login_data = {
                    'UserName':self.UserId,
                    'verifyCode':'',
                    'auto':'on',
                    'webVersion':'25',
                    'verifyCode':'',
                    'Password': encPassword,
                    'authType':'2'
                }
            loginResp = self.session.post( loginUrl, headers = loginHeader, data = login_data, allow_redirects = False)
            #print(loginResp.text)
            print(loginResp.url)
            
            self.appMailUrl = loginResp.headers['Location']
            appMailUrl = loginResp.headers['Location']
            appArr = appMailUrl.split('&')
            self.sid = ''
            for item in appArr:
                if 'sid=' in item:
                    self.sid = item.split('sid=')[1]
                    break
            if(self.sid != ''):
                print('logined')
                Crawler.uploadException(self , username = self.UserId , step='logined' , errmsg = 'logined'  )
                appMail_header = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cache-Control':'max-age=0',
                        'Connection':'keep-alive',
                        'Host':'appmail.mail.10086.cn',
                        'Referer':'http://mail.10086.cn/',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                    }
                appMailResp = self.session.get( loginResp.headers['Location'], headers = appMail_header, allow_redirects = False)
    #             print(appMailResp.text)
#                 print(appMailResp.url)
            else:
                respText = "Login Fail 帐号或密码错误"
                Crawler.uploadException(self , username = self.UserId , step='doLogin' , errmsg = respText  )
                returnData = Crawler.init( self )
                returnData['status'] = 'false'
                returnData['msg'] = '帐号或密码错误'
                returnData['success1'] = False
                return returnData  
            
            return returnData
            
            
        except Exception:
            respText = traceback.format_exc()
#             print(respText)
            Crawler.uploadException(self , username='' , step='doLogin' , errmsg=respText )
            returnData = Crawler.init( self )
            returnData['status'] = 'false'
            returnData['msg'] = '系统异常,请稍后重试,code:100.'
            returnData['success1'] = False
            return returnData  
        
    def getMessageList(self):
        try:
            returnData = {
                'msg' : '',
                'success1' : True
                }
            '''smsProxy = 'http://smsrebuild1.mail.10086.cn//proxy.htm'
            getUserInfoSet = 'http://smsrebuild1.mail.10086.cn/setting/s?func=info:getInfoSet&sid='+ self.sid +'&&comefrom=54&cguid=1656159101022'
            getUserInfoHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'8',
                    'Content-Type':'application/xml',
                    'Host':'smsrebuild1.mail.10086.cn',
                    'Origin':'http://smsrebuild1.mail.10086.cn',
                    'Referer':'http://smsrebuild1.mail.10086.cn//proxy.htm',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            getUserInfoSetResp = self.session.post( getUserInfoSet, headers = getUserInfoHeader, allow_redirects = False)
            print(getUserInfoSetResp.text)'''
            
            gethome = 'http://appmail.mail.10086.cn/m2012server/home?Protocol=http%3A&positionCode=web_210&sid='+ self.sid +'&from=preload'
            getHomeHeaders = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'appmail.mail.10086.cn',
                    'Referer':self.appMailUrl,
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            getHomeInfoResp = self.session.get( gethome, headers = getHomeHeaders, allow_redirects = False)
#             print(getHomeInfoResp.text)
            
            getHomeStr = getHomeInfoResp.text
            
            mwInfoSet = re.compile(r'var mwInfoSet = (.*?);').findall(getHomeStr)
#             print(mwInfoSet)
            
            getUserInfor = 'http://appmail.mail.10086.cn/s?func=user:getInitDataConfig&sid=' + self.sid  + '&&comefrom=54&cguid=1656159101022'
            getUserInforHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'60',
                    'Content-Type':'application/xml',
                    'Host':'appmail.mail.10086.cn',
                    'Origin':'http://appmail.mail.10086.cn',
                    'Referer': self.appMailUrl,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            getUserInfoPreLoad  = '<object>'
            getUserInfoPreLoad += '<int name="visiblePurgeBoxFlag">1</int>'
            getUserInfoPreLoad += '</object>'
            getUserInfoResp = self.session.post( getUserInfor, headers = getUserInforHeader, data = getUserInfoPreLoad, allow_redirects = False)
#             print(getUserInfoResp.text)
            getUserInforResp = str(getUserInfoResp.text)
            getUserInforResp = getUserInforResp.replace("'", '"')
            getUserInfoJson = json.loads(str(getUserInforResp), encoding='utf-8')
            userAttrs = getUserInfoJson['var']['userAttrs']
            
            self.result_info['userNickName'] = userAttrs['trueName']
            self.result_info['userMail'] = userAttrs['uid']
            
            folderList = getUserInfoJson['var']['folderList']
            self.total_inbox_items = 0
            for item in folderList:
                if '收件箱' in item['name']:
                    self.total_inbox_items = int(item['stats']['messageCount'])
            
            
#             print(self.total_inbox_items)

            
            
            
            mailList = []
            
            startIndex = 1
            totalPageDisplay = 20
            whileVar = True
            while(whileVar):
                getMessageList = 'http://appmail.mail.10086.cn/s?func=mbox:listMessages&sid=' + self.sid  + '&comefrom=54&cguid=1656159101022'
                getMessageHeader = {
                        'Accept':'*/*',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'258',
                        'Content-Type':'application/xml',
                        'Host':'appmail.mail.10086.cn',
                        'Origin':'http://appmail.mail.10086.cn',
                        'Referer': self.appMailUrl,
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                    }
                getMessagePreLoad  = '<object>' 
                getMessagePreLoad += '<int name="fid">1</int>' 
                getMessagePreLoad += '<string name="order">receiveDate</string>' 
                getMessagePreLoad += '<string name="desc">1</string>' 
                getMessagePreLoad += '<int name="start">'+ str(startIndex) +'</int>' 
                getMessagePreLoad += '<int name="total">'+ str(totalPageDisplay) +'</int>' 
                getMessagePreLoad += '<string name="topFlag">curr_task</string>' 
                getMessagePreLoad += '<int name="sessionEnable">2</int>' 
                getMessagePreLoad += '</object>'
                
                getListResp = self.session.post( getMessageList, headers = getMessageHeader, data = getMessagePreLoad, allow_redirects = False)
#                 print(getListResp.text)
                
                messageListStr = str(getListResp.text)
                messageListStr = messageListStr.replace("'", '"')
                messageListJson = json.loads(str(messageListStr), encoding='utf-8')
                messageList = messageListJson['var']
                
                
                sessionCount = int(messageListJson['sessionCount'])
                if(sessionCount > int(startIndex + totalPageDisplay) - 1):
                    whileVar = True
                    startIndex += totalPageDisplay
                else:
                    whileVar = False
                    
#                 print("startIndex" + str(startIndex))
                
                for item in messageList:
                    subject   = item['subject']
                    reSubject = item['subject']
                    date      = item['receiveDate']
                    fromArr = {}
                    fromVal = item['from']
                    fromEmailIdTxt = re.compile(r'<(.*?)>').findall(fromVal)
                    fromEmailName = re.compile(r'(.*?)<').findall(fromVal)
                    try:
                        fromArr = {
                                'name' : fromEmailName[0],
                                'addr' : fromEmailIdTxt[0]
                            }
                    except:
                        fromArr = {
                                'name' : fromVal,
                                'addr' : fromVal
                            }
                    
                    toArr = []
                    toVal = item['to']
                    toEmailIdTxt = re.compile(r'<(.*?)>').findall(toVal)
                    toEmailName = re.compile(r'(.*?)<').findall(toVal)
                    if(len(toEmailName) == 0) :
                        toEmailNameStr = ''
                        toEmailIdTxtStr = toVal
                    else:
                        toEmailNameStr =  toEmailName[0]
                        toEmailIdTxtStr = toEmailIdTxt[0]
                    toArr.append({
                            'name' : toEmailNameStr,
                            'addr' : toEmailIdTxtStr
                        })
                    
                    toList = []
                    toList.append(toArr)
                    mid = item['mid']
                    mail_size = int(item['size'])
                    
                    if(mail_size > 6500):
#                         print('*****************************')
                        #print(reSubject)
                        viewMail = 'http://appmail.mail.10086.cn/RmWeb/view.do?func=view:readMessage&comefrom=54&cguid=0.9847597206206928&mid='+ mid +'&callback=readMailReady&fid=1&guid=undefined&readTime=undefined'
                        viewMailHeader = {
                                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                                'Accept-Encoding':'gzip, deflate',
                                'Accept-Language':'zh-CN,zh;q=0.8',
                                'Cache-Control':'max-age=0',
                                'Connection':'keep-alive',
                                'Content-Length':'195',
                                'Content-Type':'application/x-www-form-urlencoded',
                                'Host':'appmail.mail.10086.cn',
                                'Origin':'http://appmail.mail.10086.cn',
                                'Referer': self.appMailUrl,
                                'Upgrade-Insecure-Requests':'1',
                                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
                            }
                        viewMail_preload = 'func=view:readMessage&comefrom=54&sid='+self.sid+'&cguid=0.9847597206206928&mid='+ mid +'&callback=readMailReady&fid=1&guid=undefined&readTime=undefined'
                        viewMailResp = self.session.post( viewMail, headers = viewMailHeader, data = viewMail_preload, allow_redirects = False)
                        #print(viewMailResp.text)
                        viewMailRespHtml = BeautifulSoup(viewMailResp.text,'html.parser')
                        divtagdefaultwrapper = viewMailRespHtml.find('div',{"id":"divtagdefaultwrapper"})
                        
                        content = {
                            'bodyText': divtagdefaultwrapper,
                            'body': ''
                        }
                        time.sleep(0.5)
                        
                    else:
                        content = {
                            'bodyText': item['summary'],
                            'body': ''
                        }
                        
                    mailList.append({
                        'from'  : fromArr,
                        'subject' : subject,
                        'reSubject' : reSubject,
                        'date' : date,
                        'reply' : fromArr,
                        'toList' : toList,
                        'content' : content
                    })
                                 
#             print(mailList)    
            
            self.result_info['mailList'] = mailList
            
            
            return returnData
            
        except Exception:
            respText = traceback.format_exc()
            #print(respText)
            Crawler.uploadException(self , username=self.UserId , step='getMessageList' , errmsg=respText)
            returnData = Crawler.init( self )
            returnData['status'] = 'false'
            returnData['msg'] = '系统异常,请稍后重试,code:100.'
            returnData['success1'] = False
            return returnData
        
    def getContactList(self):
        try:
            returnData = {
                'msg' : '',
                'success1' : True
                }
            
            getcontactGroup = 'http://smsrebuild1.mail.10086.cn/addrsvr/GetGroupList?sid='+ self.sid +'&formattype=json&&comefrom=54&cguid=1656159101022'
            getContactHeader = {
                'Accept':'*/*',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'64',
                'Content-Type':'application/xml',
                'Host':'smsrebuild1.mail.10086.cn',
                'Origin':'http://smsrebuild1.mail.10086.cn',
                'Referer':'http://smsrebuild1.mail.10086.cn//proxy.htm',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            getContactData  = '<object>'
            getContactData += '<int name="Random">0.5344166795934635</int>'
            getContactData += '</object>'
            
            getcontactGroupResp = self.session.post( getcontactGroup, headers = getContactHeader, data = getContactData, allow_redirects = False)
#             print(getcontactGroupResp.text)
            getContactListStr = str(getcontactGroupResp.text)
            getContactListStr = getContactListStr.replace("'", '"')
            getContactListJson = json.loads(str(getContactListStr), encoding='utf-8')
            contactGroupList = getContactListJson['var']['All']
            GroupId = contactGroupList['id']
            totalContact = contactGroupList['count']
#             print(GroupId)
#             print(totalContact)
            
            getContactListUrl = 'http://smsrebuild1.mail.10086.cn/addrsvr/GetContactsList?sid='+ self.sid +'&formattype=json&&comefrom=54&cguid=1656159101022'
            getContactListPreLoad  = '<object>'
            getContactListPreLoad += '<string name="GroupId">'+ GroupId +'</string>'
            getContactListPreLoad += '<string name="Keyword" />'
            getContactListPreLoad += '<string name="Letter">All</string>'
            getContactListPreLoad += '<string name="Filter" />'
            getContactListPreLoad += '<string name="Sort">name</string>'
            getContactListPreLoad += '<string name="SortType" />'
            getContactListPreLoad += '<string name="Start">0</string>'
            getContactListPreLoad += '<string name="End">'+ str(totalContact) +'</string>'
            getContactListPreLoad += '</object>'
            
            getcontactListResp = self.session.post( getContactListUrl, headers = getContactHeader, data = getContactListPreLoad, allow_redirects = False)
#             print(getcontactListResp.text)
            getContactListStr = str(getcontactListResp.text)
            getContactListStr = getContactListStr.replace("'", '"')
            getContactListJson = json.loads(str(getContactListStr), encoding='utf-8')
            getcontactList = getContactListJson['var']['list']
            contactList = []
            
            for item in getcontactList:
                contactEmail = item['email']
                contactDisplayName = item['fullnameword']
                contactNickName = item['name']
                
                contactList.append({
                        "contactEmail" : contactEmail,
                        "contactDisplayName" : contactDisplayName,
                        "contactNickName" : contactNickName
                    })
                
            
            self.result_info['contactList'] = contactList
            
            return returnData
        except Exception:
            respText = traceback.format_exc()
#             print(respText)
            Crawler.uploadException(self , username = self.UserId , step = 'getContactList' , errmsg = respText)
            returnData = Crawler.init( self )
            returnData['status'] = 'false'
            returnData['msg'] = '系统异常,请稍后重试,code:100.'
            returnData['success1'] = False
            return returnData
    
    def getLoginDetails(self):
        try:
            returnData = {
                'msg' : '',
                'success1' : True
                }
            
            loginHistoryUrl = 'http://smsrebuild1.mail.10086.cn/setting/s?func=user:loginHistory&sid='+ self.sid +'&&comefrom=54&cguid=1656159101022'
            loginHistoryHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'50',
                    'Content-Type':'application/xml',
                    'Host':'smsrebuild1.mail.10086.cn',
                    'Origin':'http://smsrebuild1.mail.10086.cn',
                    'Referer':'http://smsrebuild1.mail.10086.cn//proxy.htm',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
                }
            loginHistoryData  = '<object>'
            loginHistoryData += '<int name="dateType">30</int>'
            loginHistoryData += '</object>'
            
            loginHistoryResp = self.session.post( loginHistoryUrl, headers = loginHistoryHeader, data = loginHistoryData, allow_redirects = False)
#             print(loginHistoryResp.text)
            
            loginHistoryStr = str(loginHistoryResp.text)
            loginHistoryStr = loginHistoryStr.replace("'", '"')
            loginHistoryJson = json.loads(str(loginHistoryStr), encoding='utf-8')
            loginHistoryList = loginHistoryJson['var']['datalist']
            loginList = []
            
            for item in loginHistoryList:
                loginMode = item['type']
                if(str(loginMode) == '1'):
                    loginMode = 'PC网页登录'
                elif(str(loginMode) == '2'):
                    loginMode = '手机网页登录'
                else:
                    loginMode = '飞信跳转登录'
                    
                loginDatetime = item['loginDate']
                loginDatetime = loginDatetime.replace(' ', '')
                loginDatetime = loginDatetime.replace('-', '')
                loginDatetime = loginDatetime.replace(':', '')
                
                location = item['city']
                
                loginList.append({
                        "loginMode" : loginMode,
                        "time" : loginDatetime,
                        "location" : location
                    })
            
            self.result_info['loginList'] = loginList
            
#             print(self.result_info)
            
            return returnData
        
        except Exception:
            respText = traceback.format_exc()
#             print(respText)
            Crawler.uploadException(self , username = self.UserId , step = 'getLoginDetails' , errmsg = respText)
            returnData = Crawler.init( self )
            returnData['status'] = 'false'
            returnData['msg'] = '系统异常,请稍后重试,code:100.'
            returnData['success1'] = False
            return returnData
        
    def doUpload(self):
        try:
            if self.result_info :
               
                print('-----------139 Mail doUpload List------------')
                
                
                self.isSuccess = Crawler.uploadData( self, self.result_info)
#                 print(self.result_info)
                print('-----------139 Mail Successful List------------')
                if self.isSuccess :
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : 'success'
                    }
                    Crawler.uploadException(self, self.UserId, 'Upload Data', 'Upload Data Success')
                    Crawler.uploadException(self, self.UserId, 'Uploaded loginList_mailList_contactList', str(len(self.result_info['loginList'])) + "_" + str(len(self.result_info['mailList'])) + "_" + str(len(self.result_info['contactList'])) )
                    
                    return returnData
                else:
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : 'false'
                    }
                    return returnData 
            else:
                Crawler.uploadException( self, username = self.UserId, step = 'doUpload', errmsg = 'result_info empty' )
                returnData = Crawler.init( self )
                returnData['msg'] = '统异常,请稍后重试,code:1005'
                return returnData   
        except Exception:
            Crawler.uploadException( self, username = self.UserId, step = 'doUpload', errmsg = traceback.format_exc() )
            returnData = Crawler.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData 
            
        

from _operator import rshift
import random
import traceback
import ctypes

class mailEncrypt():
    
    def funca(self, a, d):
        c = (a & 65535) + (d & 65535);
        return self.bitwiseLessthan( ((self.bitwiseGreaterthan(a , 16)) + (self.bitwiseGreaterthan(d , 16)) + (self.bitwiseGreaterthan(c , 16)) ), 16) | c & 65535
    
    def bitwiseLessthan(self, val, point):
        try:
            return ctypes.c_int(val << point ^ 0).value
        except:
            print(traceback.format_exc())   
            return 0
        
    def bitwiseGreaterthan(self, val, point):
        try:
            return ctypes.c_int(val >> point ^ 0).value
        except:
            print(traceback.format_exc())   
            return 0
        
    def rshift1(self, val, n): 
        return (val % 0x100000000) >> n
    
    def calcDigest(self, b):
        try:
            #for (var d = (b.length + 8 >> 6) + 1, c = Array(16 * d), e = 0; e < 16 * d; e++)
            c = [0] * 16
            e = 0
            d = 1
            
            #for (e = 0; e < b.length; e++)
            for e in range (0, len(b), 1):
                #c[e >> 2] |= b.charCodeAt(e) << 24 - 8 * (e & 3);
                c[e >> 2] |= ord(b[e]) << 24 - 8 * (e & 3);
            e = e + 1
            c[e >> 2] |= 128 << 24 - 8 * (e & 3);
            c[16 * d - 1] = 8 * len(b)
            b = [None] * 80
    #         for (var d = 1732584193, e = -271733879, f = -1732584194, h = 271733878, j = -1009589776, k = 0; k < c.length; k += 16) {
            e = -271733879
            f = -1732584194
            h = 271733878
            j = -1009589776
            k = 0
            d = 1732584193
            for  k in range ( 0, len(c), 16) :
                
                #for (var m = d, n = e, p = f, q = h, r = j, g = 0; 80 > g; g++) {
                m = d
                n = e
                p = f
                q = h
                r = j
                g = 0
                for g in range( 0,  80, 1):
                    
                    b[g] = c[k + g] if 16 > g else self.bitwiseLessthan((b[g - 3] ^ b[g - 8] ^ b[g - 14] ^ b[g - 16]) , 1) | self.rshift1((b[g - 3] ^ b[g - 8] ^ b[g - 14] ^ b[g - 16]), 31)
                    
                    #l = d << 5 | d >>> 27, s
                    #l =  d << 5 | rshift(d ,27)
                    l = self.bitwiseLessthan(d, 5)  | self.rshift1(d ,27)
                    #s = 20 > g ? e & f | ~e & h : 40 > g ? e ^ f ^ h : 60 > g ? e & f | e & h | f & h : e ^ f ^ h;
                    if (20 > g):
                        cond1 = e & f | ~e & h
                    else:
                        if(40 > g):
                            cond1 = e ^ f ^ h
                        else:
                            if(60 > g): 
                                cond1 = e & f | e & h | f & h
                            else:
                                cond1 = e ^ f ^ h
                    
                    s = cond1       
                    #l = a(a(l, s), a(a(j, b[g]), 20 > g ? 1518500249 : 40 > g ? 1859775393 : 60 > g ? -1894007588 : -899497514));
                    #l = a(a(l, s), a(a(j, b[g]), 20 > g ? 1518500249 : 40 > g ? 1859775393 : 60 > g ? -1894007588 : -899497514));
                    
                    l = self.funca(self.funca(l, s), self.funca(self.funca(j, b[g]), 1518500249 if 20 > g else 1859775393 if 40 > g else -1894007588 if 60 > g else -899497514))

                    
                           
                    j = h;
                    h = f;
                    #rishi = e >>> 2
#                     rishi = rshift(e, 2)
                    #f = e << 30 | rishi
                    f = self.bitwiseLessthan(e, 30) | self.rshift1(e, 2)
                    e = d
                    d = l
                
                d = self.funca(d, m)
                e = self.funca(e, n)
                f = self.funca(f, p)
                h = self.funca(h, q)
                j = self.funca(j, r)
            
            c = [d, e, f, h, j]
            b = ""
            #for (d = 0; d < 4 * c.length; d++)
            for d in range( 0,  4 * len(c), 1):
                #b += "0123456789abcdef".charAt(c[d >> 2] >> 8 * (3 - d % 4) + 4 & 15) + "0123456789abcdef".charAt(c[d >> 2] >> 8 * (3 - d % 4) & 15)
                b += "0123456789abcdef"[c[d >> 2] >> 8 * (3 - d % 4) + 4 & 15] + "0123456789abcdef"[(c[d >> 2] >> 8 * (3 - d % 4) & 15)]
                
            return b
        except Exception:
            print(traceback.format_exc())
            return b