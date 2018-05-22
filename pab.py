# -*- coding: utf-8 -*-
"""
Created on Thu Jan  12 10:02:41 2017

@author: Jacklin
@bank: Pingan Bank
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

    
class Bank():
    '''平安银行爬虫
    '''
    
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
        
    #committed on 2017-04-27 
    def init(self, params = None):
#         print('initt11 ')
#         print('initt11 ')
        #防止重复初始化覆盖新值
        if not hasattr(self, 'crawlerServiceUrl'):
            self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        if not hasattr(self, 'uploadExceptionUrl'):
            self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        
        #self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
#         self.jiamiUrl = 'http://192.168.1.82:8081/creditcrawler/bank/getEncryptParams'
#         self.jiamiUrl = 'http://192.168.1.209:3040/bankEncrypt?'
        self.jiamiUrl = 'http://api.edata.yuancredit.com/bankEncrypt/?'
        #self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'  
        
        if params :
            self.initCfg(self, params)  
   
#         print('initt11 ')
        self.session = requests.Session()
        
        result = {
            'status':'true',
            'again':'true',
            'step':'0',
            'msg':'',
            'words':[
                        {'ID':'UserId','index': 0,'needUserInput':'true', 'label':'用户名或 身份证号', 'type': 'text'},
                        {'ID':'password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                    ]
        }
        self.result_info = {}
            
        return json.dumps(result)
    
        
    def doCapture(self, jsonParams):
        try:
#             print('initt222 ')
            return Bank.doCapture1(self,jsonParams)
        except:
            respText = 'Code_000 except:'+traceback.format_exc()
            #print(respText)
            Bank.uploadException(self, self.login_account, 'doCapture', respText)
            result = {
                'status':'true',
                'again':'true',
                'step':'0',
                'msg':'需要初始化',
                'words':[
                            {'ID':'UserId','index': 0,'needUserInput':'true', 'label':'用户名或 身份证号', 'type': 'text'},
                            {'ID':'password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                        ]
            }
            return json.dumps(result)
    
    def doCapture1(self, jsonParams):
#         print('init 222 ')
        #{"UserId":"","password":"","flowNo":"b6a75af0c95d43fbb0470b27b7567d4e&2","step":"0"}
        self.jsonParams = json.loads(jsonParams)
        
        self.cdata =  ""
        self.flowNo = self.jsonParams['flowNo']
        
        print("do capture")
        #print(self.jsonParams)
        #self.jiamiData1().
        if ( self.jsonParams['step'] == "0"):
            self.countTime = 0
            
            self.UserId =  self.jsonParams['UserId']
            self.password =  self.jsonParams['password']
            self.prevPassword = self.jsonParams['password']
            Bank.uploadException(self, self.UserId, 'docapture', 'init')
            Bank.uploadException(self, self.UserId, 'username_Password', str(self.UserId) +"_"+ str(self.password))
            self.loginSuccess = False
            if (Bank.getCookiesData(self) == True):
                if(self.loginSuccess == False):
                    returnData = Bank.init(self)
                    returnData = json.loads(str(returnData))
                    returnData['msg'] = '系统异常，请稍后再试'
                    returnData['step'] = '0'
                    if(self.bytePicode != None):
                        if(self.countTime == 1):
                            returnData['msg'] = '图形验证码'
                            returnData['step'] = '2'
                            returnData['words'] = [
                                    {'ID' : 'piccode' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '图形验证码' , 'type' : 'piccode' , 'source' : self.bytePicode }
                                ] 
                        else:
                            returnData['msg'] = '用户名或密码错误，请重新输入。同一账户24小时连续输错5次将锁定24小时'
                            returnData['step'] = '2'
                            returnData['words'] = [
                                    {'ID':'UserId','index': 0,'needUserInput':'true', 'label':'用户名或 身份证号', 'type': 'text'},
                                    {'ID':'password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'},
                                    {'ID' : 'piccode' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '图形验证码' , 'type' : 'piccode' , 'source' : self.bytePicode }
                                ] 
                    else:
                        returnData['msg'] = self.loginMsg
                        returnData['step'] = '0'
                        returnData['words'] = [
                                {'ID':'UserId','index': 0,'needUserInput':'true', 'label':'用户名或 身份证号', 'type': 'text'},
                                {'ID':'password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ] 
                    Bank.uploadException(self, self.UserId, 'loginSuccess', returnData['msg'])
                    return returnData
            else: 
                
                data = Bank.init(self)
                data = json.loads(data, encoding = 'utf-8')
                Bank.uploadException(self, self.UserId, 'getCookiesData', data['msg'])
                if(self.bytePicode != None):
                    data['words'] = [
                            {'ID':'UserId','index': 0,'needUserInput':'true', 'label':'用户名或 身份证号', 'type': 'text'},
                            {'ID':'password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'},
                            {'ID' : 'piccode' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '图形验证码' , 'type' : 'piccode' , 'source' : self.bytePicode }
                        ]
                return data
        elif ( self.jsonParams['step'] == "2"):
            self.verfiyFlag = True
            if 'UserId' in self.jsonParams.keys():
                self.UserId =  self.jsonParams['UserId']
            if 'password' in self.jsonParams.keys():
                self.password =  self.jsonParams['password']
                self.prevPassword =  self.jsonParams['password']
            self.piccode = self.jsonParams['piccode']
            if (Bank.getCookiesData(self) == True):
                if(self.loginSuccess == True):
                    self.jsonParams['step'] = '0'
                else:
                    returnData = Bank.init(self)
                    returnData = json.loads(str(returnData))
                    returnData['msg'] = '用户名或密码错误，请重新输入。同一账户24小时连续输错5次将锁定24小时'
                    Bank.uploadException(self, self.UserId, 'step 2 loginSuccess', returnData['msg'])
                    return returnData
            
        elif( self.jsonParams['step'] == "1"):
            self.otpPassword = self.jsonParams['otp']
            data = Bank.checkOTPAndLogin(self)
            Bank.uploadException(self, self.UserId, 'checkOTPAndLogin returndata', str(data))
            return data
        
        if(str(self.otpFlag) == "02"):
            print("need otp ")
            return Bank.sendOTP(self)
        elif ( self.jsonParams['step'] == "0"):
            return Bank.getDatas(self)
            
        
        
        
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
                Bank.uploadException(self, username=self.UserId, step='uploadData', errmsg=respText)
                return False
        except Exception:
            print('uploadData-->[post] PINGAN data error, ' + self.crawlerServiceUrl)
            respText = traceback.format_exc()
            Bank.uploadException(self, username=self.UserId, step='5', errmsg=respText)
            return False
   
        
    #上传异常信息
    def uploadException(self, username = '', step = '', errmsg = ''):
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'pab','login_account':username}
        try:
            if '192.168.1.82' not in self.uploadExceptionUrl:
                requests.post(self.uploadExceptionUrl, headers = headers, data = {'content':json.dumps(data, ensure_ascii=False)})
        except:
            print('uploadException-->[post] exception error')

    def jiamiData1(self):
        #密码加密
        op = True
        #Bank.uploadException(self, self.UserId, 'loginpassword', self.loginpassword)
        jiamiUrl = self.jiamiUrl
        jiamiUrl_headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        #{"bankCode":"ICBC","password":"123456","imgCode":"456z","clientIP":"127.0.0.1","randomId":"rdm123","serviceId":"0500","requestChannelzoneNo":"112233"}
        '''jiamiUrl_params = {
            'bankCode':'PAB',
            'password':self.loginpassword
        }'''
        print('doCapture-->[post] call password service, ' + jiamiUrl)
        #resp = self.session.post(self.jiamiUrl, headers = jiamiUrl_headers, data = {'content':json.dumps(jiamiUrl_params,ensure_ascii=False)}, allow_redirects = True)
        #print('jiami post sucess'+str(resp.text))
#         "平安银行"
        req_url = jiamiUrl + 'content={"bankCode":"ts","password":"'+ self.loginpassword +'"}'
        print(req_url)
        resp = self.session.get(req_url, verify = False, allow_redirects = True)
        #print(resp.text)
        
        jiamiObj = json.loads(resp.text, encoding = 'utf-8')
        op = False
        if 'bankCode' in jiamiObj.keys():
            self.password = jiamiObj["password"]
            self.cdata = jiamiObj["deviceInfo"]
            op = True
        else:
            print('jiamiData1 format incorrect')
            Bank.uploadException(self, self.UserId, 'jiamiData1', str(req_url) + str(jiamiObj))
#         if 'success' in jiamiObj.keys() and jiamiObj['success']:
#             if 'obj' in jiamiObj['obj']:
#                 obj = jiamiObj['obj']
#                 #print('obj:',obj)
#                 obj_json = json.loads(obj)
#                 obj2 = obj_json['obj']
#                 #print(obj2)
#                 obj_json1 = json.loads(json.dumps(obj2))
#                 obj3 = obj_json1['obj']
#                 #print(obj3)
#                 self.password = obj3["password"]
#                 self.cdata = obj3["deviceInfo"]
        #print(self.password)
        #print(self.cdata)
        #self.URI = raw_input('Please Input to ICBC URI:')
        
        return op
    
    def getCookiesData(self):
        try:
            url = 'https://bank.pingan.com.cn/ibp/bank/index.html' 
            headerStr = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'bank.pingan.com.cn',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
                
            getLoginPageresp = self.session.get(url, headers = headerStr, verify = False, allow_redirects = True) 
            #print(self.session.cookies)
            
            noticeUrl = 'https://bank.pingan.com.cn/ibp/ibp4pc/notice/noticeNotLoginQuery.do'
            noticeData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'menu_code':'ibparea000000',
                    'user_name':'',
                    'type':'3'
                }
            noticeHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'77',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"],
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            noticeResp = self.session.post(noticeUrl, data = noticeData, headers = noticeHeader, verify = False, allow_redirects = True) 
#             print(noticeResp.text)
#             print(self.session.cookies)
            
            getConfigUrl = 'https://bank.pingan.com.cn/ibp/ibp4pc/outlogin/getConfigValus.do'
            configData = {
                    'channelType':'d',
                    'responseDataType':'JSON'
                }
            configHeaderStr = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"],
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            getConfigresp = self.session.post(getConfigUrl, data = configData, headers = configHeaderStr, verify = False, allow_redirects = True) 
            #print(getConfigresp.text)
            #print(self.session.cookies)
            
            checkVerifyCodeUrl = "https://bank.pingan.com.cn/ibp/portal/pc/showVerifyCode.do"
            checkVerifyCodeData = {
                    'channelType':'d',
                    'responseDataType':'JSON'
                }
            checkVerifyCodeHeaderStr = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'JSESSIONID='+ self.session.cookies["JSESSIONID"] +';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"],
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            checkVerifyCoderesp = self.session.post(checkVerifyCodeUrl, data = checkVerifyCodeData, headers = checkVerifyCodeHeaderStr, verify = False, allow_redirects = True) 
            #print(checkVerifyCoderesp.text)
            #print(self.session.cookies)
            
            verifyCodeResp = json.loads(checkVerifyCoderesp.text, encoding = 'utf-8')
            vcodeShowFlag = verifyCodeResp["responseBody"]["vcodeShowFlag"]
#             print("vcodeShowFlag "+str(vcodeShowFlag))
            self.verfiyFlag = False
            #self.getVerifyCode()
            self.bytePicode = None
            #print(str(vcodeShowFlag))
            vcodeShowFlag == "0"
            if str(vcodeShowFlag) == "1":
                self.bytePicode = Bank.getVerifyCode(self)
                return False
            else:
                success = Bank.doLogin(self)
            return True
        except Exception:
            #print(traceback.format_exc())
            respText = traceback.format_exc()
            Bank.uploadException(self, username=self.UserId, step='5', errmsg=respText)
            return False
            
             
    def getVerifyCode(self):
        self.countTime = self.countTime + 1
        currentTime = str(round(time.time()))
        #getVerifyUrl = 'https://bank.pingan.com.cn/ibp/portal/pc/getVcode2.do?'+ currentTime +'000'
        getVerifyUrl = 'https://bank.pingan.com.cn/rmb/brcp/uc/cust/uc-core.get-validCode.do'
        getVerifyHeader = {
                'Accept':'image/webp,image/*,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch, br',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Cookie':'JSESSIONID='+ self.session.cookies["JSESSIONID"] +';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"],
                'Host':'bank.pingan.com.cn',
                'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
            }
        data = {
                'channelType':'d',
                'responseDataType':'JSON',
                'channelId':'netbank-pc',
                'deviceType':'window',
                'type':'1'
            }
        getVerifyCoderesp = self.session.post(getVerifyUrl, data = data, headers = getVerifyHeader, verify = False, allow_redirects = True) 
        #print(self.session.cookies)
        #print(getVerifyCoderesp.text)
        Bank.uploadException(self, username=self.UserId, step='getVerifyCode', errmsg=str(getVerifyCoderesp.text))
        self.verfiyFlag = True
        imgbyteBase64Str = base64.b64encode(getVerifyCoderesp.content).decode(encoding = 'utf-8')
            
        '''
        #store it in local
        imgData = base64.b64decode(imgbyteBase64Str)
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
        '''    
        return imgbyteBase64Str
            
    def checkOTPAndLogin(self):
        #checkotpUrl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/pcverifyOTP.do'  
        checkotpUrl = 'https://bank.pingan.com.cn/rmb/brcp/uc/cust/uc-member.sms-validate.do'
        '''checkotp_postData = {
            'channelType':'d',
            'responseDataType':'JSON',
            'password': self.otpPassword
            } '''
        checkotp_postData = {
            'channelType':'d',
            'responseDataType':'JSON',
            'channelId':'netbank-pc',
            'msgType':'12',
            'validCode':self.otpPassword,
            'validType':'2'  
            }
        checkotpHeaderStr = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'Content-Length':'51',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'bank.pingan.com.cn',
            'Origin':'https://bank.pingan.com.cn',
            'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'
            } 
        checkOTPresp = self.session.post(checkotpUrl, data = checkotp_postData, headers = checkotpHeaderStr, verify = False, allow_redirects = True) 
        #print(checkOTPresp.text)
        #print(self.session.cookies)
        responseTxt = json.loads(checkOTPresp.text, encoding = 'utf-8')
        Bank.uploadException(self, self.UserId, 'checkOTP_Response',  str(responseTxt))
        if(int(responseTxt["responseCode"]) == 0):
            Bank.uploadException(self, self.UserId, 'checkOTP', 'OTPSuccess')
            return Bank.getDatas(self)
        else:
            Bank.uploadException(self, self.UserId, 'checkOTP',  str(responseTxt))
            returnData = Bank.init(self)
            returnData =  json.loads(returnData)
            returnData['msg'] = '动态密码错误，未通过校验.'
            return returnData
    
    
        
    def doLogin(self):
        time.sleep(2)
        self.loginMsg = ''
        getSystemTimeUrl = "https://bank.pingan.com.cn/ibp/ibp4pc/outlogin/common/getSystemDateTime.do"
        getSystemTimeData = {
                'channelType':'d',
                'responseDataType':'JSON'
            }
        getSystemTimeHeaderStr = {
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'35',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie':'JSESSIONID='+ self.session.cookies["JSESSIONID"] +';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"],
                'Host':'bank.pingan.com.cn',
                'Origin':'https://bank.pingan.com.cn',
                'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest'
            }
        '''getSystemTimeresp = self.session.post(getSystemTimeUrl, data = getSystemTimeData, headers = getSystemTimeHeaderStr, verify = False, allow_redirects = True) 
        #print(getSystemTimeresp.text)
        #print(self.session.cookies)
        
        responseTxt = json.loads(getSystemTimeresp.text, encoding = 'utf-8')
        current_date_time = responseTxt["response_body"]["current_date_time"]
        
        m = len(str(current_date_time))
        if(m < 10):
            m = "0" + str(m)
            
        v = len(str(self.prevPassword))
        if v < 10 :
            v = "0" + str(v)
            
        #var g = "" + m + f + v + h.val();
        passwordFormat = "" + str(m) + str(current_date_time) + str(v) + str(self.prevPassword)
        print(passwordFormat)
        self.loginpassword = passwordFormat'''

        thirdArg = {
            "e": '10001',
            "maxdigits":"256",
            "n": "BB955F6C6185B341C1A42EBF1FF9971B273878DBDAB252A0F1C305EBB529E116D807E0108BE6EDD47FF8DC5B6720FFE7F413CBB4ACDFB4C6BE609A5D60F5ADB261690A77755E058D4D9C0EC4FC2F5EB623DEBC88896003FBD8AFC4C3990828C66062A6D6CE509A2B0F8E06C4E332673FB86D235164B62B6110C1F1E0625B20ED"
        }
        #self.password = Bank.encryptForm(self, "credit123", thirdArg)
        #self.password = Bank.encryptForm(self, "credit123", thirdArg)
#         self.cdata = 'AAAJpAvsAAAAgIgiaYacc6KcLTeEWtzR%2BJvJsu68cITlTK5Qjyp2oSHo%2FgFew66QdV%2BIxL0gAbH%2FFPZNbPoyctKOxDqxggmJQdunovfuM1sEonQYsDd%2FeGwwux8SHzqTSIbm5t2HrG0nIbsjgVpTJmY9jOxcgWz6kNu2tUt4mczK5z5z7AAVdg6Umi4IQZynKbkXp0%2BlSFIdi5IOKx0U1Agm0MaOwPAhzeo2nyyKZ1KPSYMZj3btfMm9omiQU1G6Ii4dti58CMQRHF140MIGKzlfRwXQ%2F51o5JSek4T4jKLd6Ts0Xn5ElNo1aB6UkfQpqRM4IYEo72nKvGxTqZMsKw05FyXSL3vXBG1SGuZXLkR1COP8SdMy4yT3Esf08Cw2TmqJ6KDOo4yLgF1kQPkGI3uEMaPe374dO4fSuOlKhY0aBSBt0w%2Bnopq3BdFNDe9yjAiv4NwTemUg7W4yqvh3tRF2jqEl847RIE0%2F7jSZ8sLCZaimyNcKck2kNUk94kVnhsLl4zKYQfg0hYXMf1g7m%2FzibPUlSGqz%2Bq%2BgXoab5UY%2BjeBs8XgjPjXjOxon2rUmV9LpiE7qW%2FGD%2BGeQXIr4qtQbmnbr4MUfenFt9P%2B9oGKbQLH4GsaV77U0XoURhuhpETBOA3oZB2NwRbJYDaZItHsH7r9kfVfEbcdYkz5N9WX05UIDKHA0L1rMkbsJIBSa9zdWhcdgAgFssGUsPWA43Oq27r0G8TwV7TuDyDNw39iEIq%2BoXv10n1qpeVI10%2FtsZrFANmXoDgyP7bRQ2FmBJiKk35OcSs28IoBfY%2FNe7yhjDWOZR41LqlUHJTho5M28AJZcmj63%2BT2CP2dRpetTMKna3jRutO3ydx1s7lykOkzjVDKHt1jMgDsNJTho5M28AJZcmj63%2BT2CP%2F6WGvb2LywQ9KCwoGxT9egtbkGyj2%2BLctvx2LLtQWTw%2FEYc6FV8jhA7O3HSz1ZmAQ6SOHs%2FtOhWzLH1ZHnXNJRUlXwF%2BOomuBS69p261yk1oXtrt3556%2F5ysRlsvKtvWj7n9I%2BGVl2E%2FeItwjtqN6yagRRU2a7yihrbRetqEz7iyR5B%2FjvTqigAIcrfnYFG4wx6rUoZI1fxgYnJ2j8jfS18I50ITlaPIrp4Y3RV3gV1azXfo%2F6m0im55PMVlhl06b0Q2b2F3aTRXyCa8hrg12jpb8J9lhz6MKNYHiNJ0f82jOWyjLfZVeiyx7JFUdvBxY98wGqVvEkGhpugJrutvRnNhRmHOwgarMwpWSyrsXPlZ38ccnj9fYpuzrNE0gaBRR1KJl6d3uQ4SzOtXYksCKfecLmozUT%2FwTN3ffJ8jRzEYu1fxnyHzrEIOKwUUNfDj1nUfx8FHd7yMCfROrx40ZryJVW7awiwXuZPZuHjfeFlI5HehZ1KS%2B5n9mgWaYPKgd%2BQPfv4N2r6c2%2FeoNYAJfwfQeBliiqviByRdN4gXfxV40w00mw49do3J5W8ls4xmCU3TG%2FdqWw6zr0URmzkSdycBGhWgRaXiEfmYtelHOinP0mZHhc9uHZxWGqBXYfDGggiJqHNsDz5wtnx7QKqKxO6HrsgNYBv4%2BYmjq52mCd8emVlNmXDTZlH8fl4dsFaRpVkhSL%2BFeblJQn9lHTevIxLGNh6eead9oaR5dPiNWsRs0RHn2Mn1tJwsRu7EKw8skZVs%2BfBq8cxXUzi4AEiPMsJAdVkiBM6u%2BVy1ZIvUCNsempFCJ1gx1JiDhb2J3FSRcBPuXUGO5JlNjCTJEpzBZ22enIif7HyjRfeTVlnK1Mk61JEAQLF5KDsqotOOR7Qx0jWICKaZOk3%2BN17NTADvJH5HrlZ3Oo2L%2BOyRETOgmxWPyYWaDUll8J%2FPfiybLGLkLZ1%2Brk0cVzefe5JXYq883ZGqAybIR8BSPya6XZRwE2FWeyZfLHdn5rszJ3o86Tpk46%2BKRgtgO%2FW4%2Fnqs2Zcy50qSQ%2Bp7M7xLYPy8oVV3gb8KqyOKHO%2B1h4kMt7bj7P%2F2I2dCagG%2FCjJ3pFOhuwQnNXZr5TUMXXnMCuMBZn6OLqXfb52XGD8E%2FhTWMXknLRgKhLEdw8OHYKclWyWH0rq1wUo3vT0%2FMTzIyUoubSM2M62AN5AvJTjGZV3Xt15o9vq9kaZ1lmSitW4a3YF01CcJ5rRllri1jb%2FH%2B4WRpIHHWubBiba4FRK3QTFjZX34ovZmIUpcZ6KtYp%2FFZS%2FkzqkLX67NIadhyNMq7TDA19T0S%2Fde6pVtezj4jleeBlb8YrgjwIsehNUUdMr4BBodhlJ04ECPf52JWMtq5nRlgpMc6tsuFrpm6283eS%2FV%2FPESLHOFHku5l%2BKL%2B9WEzmt%2B2c4R%2BZJWrGhzrGCSIUnkxvbBrkCwU0pyhW3mLe1LSyCs5%2FreJ3g4nk7HWeiG1RZEf4UnIzPPXwr2qzRMBkBWjpYuinXEsjRckqnD2khnS7%2BVvi5gtUk5k2a3Z1CSAfLSmkpnmRYp1Fiov67Ixr50OX074N8rKgH4Y0e441RwxvPgONxm1jcMXnsCEpJelfo8D9Sk0BvRxc68uX5gRcT0OJePtY9pjpW7%2Bd9%2Bgy0HiLJP8Xjyg%2BXiu1RJFoZsKgQc%2FWwrZ3qxa%2FURIb4d5Ezb7wLoPbJjcgOp%2BcYJFYMY%2F69vBFAohO6VOnOk%2FQgIBHV4p37EXmqIu4EwlHmZRTirRCLRUfr%2BsK2ZS%2BKdkuW1llYfSQUX73ij%2FVXIppk2QLnX9iBkjGgSJ4hVzChp6YkKeV2XXBGfQ3HFHACmMX7IQpjFj%2Fg5ZD0E8KUeWo9HmOzXE%2Bqh%2F8FSZMyuAhwmuvr8dziD5nQ5N%2FRns5L6rDavzCQ28CuMmvdxB2X8%2FmWdUFYYrlRMyBssG19LU4Zq4IXPBW3G1NzwOPi0WC4cUgg%2B%2FPfvJZI0aAXU%2BLmaFK2BdzpJF5dUBZNO1nBsjjqD0AKcJTDEFNbrFuShBHewOt6PdUvrb3jJ32dhSjxBp7E44RWoUvYYJZ%2FH4XzVyalCTD6fwe8HCopjSDoU%2FKzoD66DF93AbmC0r0lyPSiyTD%2FIGEet%2B4KZtbNtCxy2RdKH5SmLY1JcllqvcWprpdII%2BFTOrSqWSBe8AVJkzK4CHCa6%2Bvx3OIPmdDk39GezkvqsNq%2FMJDbwK4ya93EHZfz%2BZZ1QVhiuVEzIGywbX0tThmrghc8FbcbU3PA4%2BLRYLhxSCD789%2B8lkjRqKfmDIkgBnMZyoZueNbSoEUPgRfsEKEqlblNvp0lgKFtxvm2xA%2FFU3BEjwGcW4%2Bz2WXnOtcR4iZTSSMiU8gj3zt%2FU9F3%2BcalTKIGdCEXQUI%3D'
# #         self.password = raw_input("encrypted password:")
# #         self.cdata = raw_input("encrypted cdata:")
#         self.password = 'CN-S' + self.password
            
        #if(Bank.jiamiData1(self)):
        if(True):
            time.sleep(0.2)
            self.cdata = 'AAAJ5P9SAAAAgFORGuMYH3B4HWlr5DCbGj6Y8tqAFkmasImMv3Si7yfN7JdE5BWsH3pOFFnP6%2BKBbBLtAFjVx6uA1se3zYrObhZzIzH9twxZEc2fvmn7CRLPQQ14aq8qaZ79Cn03oYNaMShVdCCrFdKbfcZt8zdUzftvd3z70KPtiF83DjdMb8DPE6PM39azbiEwsKzQPjwuzJDA%2BCLrFKGSR3ziSpxaLw7n5Aw56r8nRPPg5Fb5RQbEHda5zWj6cj4gqOjOMD7LrHibkXr0CPtsfgDY%2BuIoKNjrzMZI%2Fr2UPxjlLn%2BSKlnju%2Fnh%2FomDGf8em8ZAuOAtPIfF5nHKKf3BsHD7x24d%2FSPJMHDiO0KYBhomeMF0YkaiwSHcDy2WdfB8RHdINxQcCm4T0bosqcoJbLNef8bZzp4%2Fb33IuAT9WaT9rOpk3UKApaGLizhtUzlditU0HQqm%2FO32%2B1f6OuL4ID3sDV6K9JdF9PkL4xtpCjCEpd6cJvs%2FW0%2BeZG8ZWUKWQjZltmlF71%2BcIAJH7fdV%2BXyj4oOTOn%2BmI0LMezBT7yJsm4%2B5B5eKX7G28zVylpQ7fc8qRsMBRRTVTTaTKWsZVntA6610SjjqjJHXQkiq9IH3pNdR92OonJzmZP8p4I6sxAVzxkhPiOkFzP1kHixDC1LFiNTGe3L1%2Fxtl3c2PLI%2FJvUnZrh08TPVyzPEyXb%2FAJ3IZPcXM%2FNELqhjR1%2BBkG9vWgGroIS90NpbM95nsIea5d1EIA43dIXLx6tlfwsRhqOSkQCAWADSMj4VhPAVlBkCXMbLC3PyzVtrxx%2FGVqx4mPTFo11i%2FGj7XKJl93AcnDt3QW2ECwveY9T9zRJA2MrkdsNPDvYj0%2Bv%2FvfeR0IKvHkA8mYzi472%2F2QxoVesPSAfJozOzMDvKOLPrq1D5ROi0nk4NxQ5s2eTuhu2ahiEr%2BC1Kaxu7kTQZSej%2BsHBpIj9vRBj35fa11GSWQsq1fKzkuY2bC6SQD5N6VEOfdgI9%2Fo1%2BG33ONcsarTryIIS6AieH7WxdRk94FRlwEMChYBCAhYwPqsGP3NoB2kkIGrT%2F707YrqkDnuuYGhlwAiOS8rHa4mu6Vge9P48r4lFbNBgAN8f%2BAqWFeiidUycEabCLaf3Nd%2B2kZMVEAXW7p6SllW4h1DR7FUeKjZGFQ%2Bay%2BEo0wjyQLJYPhNWN7VyZj86ePw0CJWXGDGSqxhPAltpWNCePWcdlPWXYh6i%2FpN9OSoMu6iaBjpdQzp6qKdJPM%2BByBwQ17ZRHVgaS2LEK4Z7johzp2%2BRaQkxkU6ZH6URe%2FfAoKVWdt3LylkY3wwf90aKn%2BzGXB%2FgkmoVNFw%2FPi7QHDyLCiL6hXCTUFrxe3%2BanskiuD9mkAdpEAMC0BgilxvLt4irV9LQk09GnKMZUnfGavbGqUpFTJHwKY2QNBfgVppkP5SIE4MzsLSx0durNU3aLq9djIH2IzXQN4gnqA6J8nT3NStby3Z35%2BXnTy%2BlWUE%2FBvOuih46%2ByTIC2zSiNmqbv%2FYFkU991aLjgq38qS18Dr5%2BKBo%2BY0rvqNI4T%2BG0csU9Pp%2BCg3DRmsnQMHNSTiArRGPZrVIHmWnHdzrbZ89Vj68y6c2IfluzwQqqbkUNJHDsSbTtoLV%2BeO954N0GW68%2BcsxmQ3bF7KJla5xMDIj0%2FnPjQcg2xTzEgKkTL6BqaN0Lp8v%2B0e%2BC39KsMiJQr7QRrPjA5whDXcwLDGEzHs1jtINPkE0pmZ%2B82lP%2F8xzUTL%2BHGG5jwOp8aLtxZDdg7ypSzYAA%2FBePPOfCcU7IOzuwUV3ynU%2FplPhW068VKQp9ZpYNIphc5rmncgII0EfcEC3ukkXV7sCQcspNXWzhXnXe%2Bt6BPFvUqnOE%2Bf3ncdx3drQpxGkn73HEaWLIzOPswPO1J1vXPT%2BZanfWUDIApVIGEYr7g7f%2FmR4Vl2j2nAhyd7jPbkgtBIKRDxx0WJv0Wea1x3LVBArJn1yTfv5O84PwW8yXayApwZgUzAU4fvB4yVECzhKeJOhpYCoqx77bkm9VrzTd48iBfxZ4SAoL2d%2FWyjI80bYJGuejPEfONzvg7VwBdEG0U2S2R5cSMSxOiXtar7Jkql17UdDkmZoOpyltEt%2BZP%2Bs5Kgp2BovMnMfKTFY%2BW47%2Bx4HoyHb1X9T%2FCZJ1V2T%2BLvPlcG9MPga%2FhvTF52AyjoaiUkpiJzY8j3SaXP2cinItC%2BkS2mxvPdj7WqgfY%2FJSIj%2FLGqQKZ0sGiZwKbVmx6v4%2FzSIEmadrnLw68o2fzhK7fokWGm7ZJ46L3YPzwSqwyxUhd3ru8%2FseMLe%2BAMbKNqFZAvmWhsJcWkwyJD9NOMJMOhK3l%2FErxvbvzk5SVpTHy8TubyiyudpFGGLYtvRV8DYlhnSCB8bMMHm8gG%2FVV56u3H3%2BRDwaPbMuvniEt1%2BK6WuNhYjeOGCR1fu6DiDuYAp%2FtiL634gXoqgeIfAZjeNlD%2Bk3NiM6ZN9So3BLS2plPHoOJYg33W0sMGPzBN%2Bm1%2Fyl%2B0gPGKsHhHS1YHMzMUZun8YkMO7K91%2FLQEWi7XBGXZFTsQP2nsQ3sAg8tr1LDjBreCztrlttXvaKGtSOEas%2BcSHvVQeOAJMG2Isrfpbwg2gyvvCgF%2BcBzWr%2BQ%2FqDfpJyHavw0wFEW0TEU7ydWpBsdWcLjqK6ZHPGTwpTYgtlAdXnmELZ%2BX7YaVrH%2Fq5oQKlqwU5qP0lMLjHtc0l5jFk6NpoL3hO98e%2BxUaZIQBUW2e%2Fi5vvjdvda5hXPnw81dKfKddnVU8nZuubf%2FbKJ%2FkUU2ENZWqcbbczO6Ag88vigRxkmZEtECPlgWEK9Yrg7qE26hSRvHm%2FWXFd67U39MYhZnABdN%2Fy23aYFNLFrnNGwyPoNX%2FkycrAf5Z3zYFEc3aeqwfxHJL%2BPIztjbQOPtkFCaJg2zJ9JIZ9kEYm3jPCcp87Eeko245I2fuvoNv6rMVwy5%2Fxwse6WIfTvSm9AGCcow1V4HqiC0jtKPKGjBBZMuuNV2jRGpXAnmNfIh0Cxs6wbL%2Bzcb8jYNCODWwhy4Qyyxja03NoysHtLtjN7naYXHcNovN%2BxcW2cOYu0JIKE%2BQz3Kyor6SXBpVCjmEIkzj8WXu2jo2cvKupyLBcv9S5xpj29HGuiMpKyLl3sJ646AlT1TA4B8OzNTKP1o8j64TqBI27n%2BTJysB%2FlnfNgURzdp6rB%2FEckv48jO2NtA4%2B2QUJomDbMn0khn2QRibeM8JynzsR6SjbjkjZ%2B6%2Bg2%2FqsxXDLn%2FHCx7pYh9O9Kb0AYJyjDVXgeqILSO0o8oaMEFky641XbPx3FXVMLxTsycfJ%2FbsxZDF9NbXaiyBZD3QNgZ%2Fy6olLdZR9RaSHc9t2Vsz2ATxA8ClRyEyaGNz1xGNxK9%2BlcR'
            #self.password = raw_input("encrypted password:")
            
            self.password = Bank.encryptForm(self, self.prevPassword)
            self.password = str(self.password).upper()
    #         print(self.password)
    #         print(self.cdata)
            #self.password = "CN-SDE8B64DCFF61004715F9668216466B5F5A0171F7B4305FCFFD410D3AE4FDED1F9F4089C0BA60DBD63701830DF37D457D9D00B0FECA3B6F07FA74ECC5393F2D259A3EF7646112796D088C7C89F0FFAC22C62840C8C58956823810DD743E09C6D534DD8756ECF06B4CDA841242BC6C1FAB707098415D95CBB9CCF2"
#             self.password = raw_input("encrypted password:")
#             self.cdata = raw_input("encrypted cdata:")
            #loginUrl = "https://bank.pingan.com.cn/ibp/ibp4pc/login.do"
            loginUrl = 'https://bank.pingan.com.cn/rmb/brcp/uc/cust/uc-core.smart-login.do'
            if self.verfiyFlag == True:
                #piccode = raw_input("Please enter verify code: ")
                #piccode = ''
                
                '''loginPostData = {
                   'branch_channel_type': '001',
                   'cdata': self.cdata,
                   'channelType': 'd',
                   'main_channel_type': '001',
                   'responseDataType': 'JSON',
                   'vCode':self.piccode,
                   'rsaPin': self.password  ,
                   'userId': self.UserId
                }'''
                loginPostData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'channelId':'netbank-pc',
                    'deviceType':'window',
                    'pwdEncryptionType':'0',
                    'userId':self.UserId,
                    'loginPwd':self.password,
                    'deviceVersion':'Windows10' 
                    }
   
                '''branch_channel_type: 001
                cdata: AAAJ5P9SAAAAgFORGuMYH3B4HWlr5DCbGj6Y8tqAFkmasImMv3Si7yfN7JdE5BWsH3pOFFnP6%2BKBbBLtAFjVx6uA1se3zYrObhZzIzH9twxZEc2fvmn7CRLPQQ14aq8qaZ79Cn03oYNaMShVdCCrFdKbfcZt8zdUzftvd3z70KPtiF83DjdMb8DPE6PM39azbiEwsKzQPjwuzJDA%2BCLrFKGSR3ziSpxaLw7n5Aw56r8nRPPg5Fb5RQbEHda5zWj6cj4gqOjOMD7LrHibkXr0CPtsfgDY%2BuIoKNjrzMZI%2Fr2UPxjlLn%2BSKlnju%2Fnh%2FomDGf8em8ZAuOAtPIfF5nHKKf3BsHD7x24d%2FSPJMHDiO0KYBhomeMF0YkaiwSHcDy2WdfB8RHdINxQcCm4T0bosqcoJbLNef8bZzp4%2Fb33IuAT9WaT9rOpk3UKApaGLizhtUzlditU0HQqm%2FO32%2B1f6OuL4ID3sDV6K9JdF9PkL4xtpCjCEpd6cJvs%2FW0%2BeZG8ZWUKWQjZltmlF71%2BcIAJH7fdV%2BXyj4oOTOn%2BmI0LMezBT7yJsm4%2B5B5eKX7G28zVylpQ7fc8qRsMBRRTVTTaTKWsZVntA6610SjjqjJHXQkiq9IH3pNdR92OonJzmZP8p4I6sxAVzxkhPiOkFzP1kHixDC1LFiNTGe3L1%2Fxtl3c2PLI%2FJvUnZrh08TPVyzPEyXb%2FAJ3IZPcXM%2FNELqhjR1%2BBkG9vWgGroIS90NpbM95nsIea5d1EIA43dIXLx6tlfwsRhqOSkQCAWADSMj4VhPAVlBkCXMbLC3PyzVtrxx%2FGVqx4mPTFo11i%2FGj7XKJl93AcnDt3QW2ECwveY9T9zRJA2MrkdsNPDvYj0%2Bv%2FvfeR0IKvHkA8mYzi472%2F2QxoVesPSAfJozOzMDvKOLPrq1D5ROi0nk4NxQ5s2eTuhu2ahiEr%2BC1Kaxu7kTQZSej%2BsHBpIj9vRBj35fa11GSWQsq1fKzkuY2bC6SQD5N6VEOfdgI9%2Fo1%2BG33ONcsarTryIIS6AieH7WxdRk94FRlwEMChYBCAhYwPqsGP3NoB2kkIGrT%2F707YrqkDnuuYGhlwAiOS8rHa4mu6Vge9P48r4lFbNBgAN8f%2BAqWFeiidUycEabCLaf3Nd%2B2kZMVEAXW7p6SllW4h1DR7FUeKjZGFQ%2Bay%2BEo0wjyQLJYPhNWN7VyZj86ePw0CJWXGDGSqxhPAltpWNCePWcdlPWXYh6i%2FpN9OSoMu6iaBjpdQzp6qKdJPM%2BByBwQ17ZRHVgaS2LEK4Z7johzp2%2BRaQkxkU6ZH6URe%2FfAoKVWdt3LylkY3wwf90aKn%2BzGXB%2FgkmoVNFw%2FPi7QHDyLCiL6hXCTUFrxe3%2BanskiuD9mkAdpEAMC0BgilxvLt4irV9LQk09GnKMZUnfGavbGqUpFTJHwKY2QNBfgVppkP5SIE4MzsLSx0durNU3aLq9djIH2IzXQN4gnqA6J8nT3NStby3Z35%2BXnTy%2BlWUE%2FBvOuih46%2ByTIC2zSiNmqbv%2FYFkU991aLjgq38qS18Dr5%2BKBo%2BY0rvqNI4T%2BG0csU9Pp%2BCg3DRmsnQMHNSTiArRGPZrVIHmWnHdzrbZ89Vj68y6c2IfluzwQqqbkUNJHDsSbTtoLV%2BeO954N0GW68%2BcsxmQ3bF7KJla5xMDIj0%2FnPjQcg2xTzEgKkTL6BqaN0Lp8v%2B0e%2BC39KsMiJQr7QRrPjA5whDXcwLDGEzHs1jtINPkE0pmZ%2B82lP%2F8xzUTL%2BHGG5jwOp8aLtxZDdg7ypSzYAA%2FBePPOfCcU7IOzuwUV3ynU%2FplPhW068VKQp9ZpYNIphc5rmncgII0EfcEC3ukkXV7sCQcspNXWzhXnXe%2Bt6BPFvUqnOE%2Bf3ncdx3drQpxGkn73HEaWLIzOPswPO1J1vXPT%2BZanfWUDIApVIGEYr7g7f%2FmR4Vl2j2nAhyd7jPbkgtBIKRDxx0WJv0Wea1x3LVBArJn1yTfv5O84PwW8yXayApwZgUzAU4fvB4yVECzhKeJOhpYCoqx77bkm9VrzTd48iBfxZ4SAoL2d%2FWyjI80bYJGuejPEfONzvg7VwBdEG0U2S2R5cSMSxOiXtar7Jkql17UdDkmZoOpyltEt%2BZP%2Bs5Kgp2BovMnMfKTFY%2BW47%2Bx4HoyHb1X9T%2FCZJ1V2T%2BLvPlcG9MPga%2FhvTF52AyjoaiUkpiJzY8j3SaXP2cinItC%2BkS2mxvPdj7WqgfY%2FJSIj%2FLGqQKZ0sGiZwKbVmx6v4%2FzSIEmadrnLw68o2fzhK7fokWGm7ZJ46L3YPzwSqwyxUhd3ru8%2FseMLe%2BAMbKNqFZAvmWhsJcWkwyJD9NOMJMOhK3l%2FErxvbvzk5SVpTHy8TubyiyudpFGGLYtvRV8DYlhnSCB8bMMHm8gG%2FVV56u3H3%2BRDwaPbMuvniEt1%2BK6WuNhYjeOGCR1fu6DiDuYAp%2FtiL634gXoqgeIfAZjeNlD%2Bk3NiM6ZN9So3BLS2plPHoOJYg33W0sMGPzBN%2Bm1%2Fyl%2B0gPGKsHhHS1YHMzMUZun8YkMO7K91%2FLQEWi7XBGXZFTsQP2nsQ3sAg8tr1LDjBreCztrlttXvaKGtSOEas%2BcSHvVQeOAJMG2Isrfpbwg2gyvvCgF%2BcBzWr%2BQ%2FqDfpJyHavw0wFEW0TEU7ydWpBsdWcLjqK6ZHPGTwpTYgtlAdXnmELZ%2BX7YaVrH%2Fq5oQKlqwU5qP0lMLjHtc0l5jFk6NpoL3hO98e%2BxUaZIQBUW2e%2Fi5vvjdvda5hXPnw81dKfKddnVU8nZuubf%2FbKJ%2FkUU2ENZWqcbbczO6Ag88vigRxkmZEtECPlgWEK9Yrg7qE26hSRvHm%2FWXFd67U39MYhZnABdN%2Fy23aYFNLFrnNGwyPoNX%2FkycrAf5Z3zYFEc3aeqwfxHJL%2BPIztjbQOPtkFCaJg2zJ9JIZ9kEYm3jPCcp87Eeko245I2fuvoNv6rMVwy5%2Fxwse6WIfTvSm9AGCcow1V4HqiC0jtKPKGjBBZMuuNV2jRGpXAnmNfIh0Cxs6wbL%2Bzcb8jYNCODWwhy4Qyyxja03NoysHtLtjN7naYXHcNovN%2BxcW2cOYu0JIKE%2BQz3Kyor6SXBpVCjmEIkzj8WXu2jo2cvKupyLBcv9S5xpj29HGuiMpKyLl3sJ646AlT1TA4B8OzNTKP1o8j64TqBI27n%2BTJysB%2FlnfNgURzdp6rB%2FEckv48jO2NtA4%2B2QUJomDbMn0khn2QRibeM8JynzsR6SjbjkjZ%2B6%2Bg2%2FqsxXDLn%2FHCx7pYh9O9Kb0AYJyjDVXgeqILSO0o8oaMEFky641XbPx3FXVMLxTsycfJ%2FbsxZDF9NbXaiyBZD3QNgZ%2Fy6olLdZR9RaSHc9t2Vsz2ATxA8ClRyEyaGNz1xGNxK9%2BlcR
                channelType: d
                main_channel_type: 001
                responseDataType: JSON
                rsaPin: 94B77EB0FF6D43FB8FC06414AF0636B32EED59BBE5B1FEE86320A48E5C4DF5DD5E419C2BA409F4153E68493D833E5608C170B42A4674330F73CE54A6AA0ACABA4B77F00CEEA8517ADD213AD2478F03A5300DB5284DC9422B7C59DA173FC4BA55EF0725A131E65E586751512713D47E80CC80AFBCA480E7F0B7FAA655560AA9E8
                userId: 440921199105133832
                vCode: 7LKA'''
            else:
                
                '''loginPostData = {
                   'branch_channel_type': '001',
                   'cdata': self.cdata,
                   'channelType': 'd',
                   'main_channel_type': '001',
                   'responseDataType': 'JSON',
                   'rsaPin': self.password  ,
                   'userId': self.UserId
                }'''
                loginPostData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'channelId':'netbank-pc',
                    'deviceType':'window',
                    'pwdEncryptionType':'0',
                    'userId':self.UserId,
                    'loginPwd':self.password,
                    'deviceVersion':'Windows10' 
                    }
            #print(loginPostData)
            
            loginHeaders = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'4380',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'pcSysTxt=C761400283900002AA881A8B138E12F2cf8e;JSESSIONID='+ self.session.cookies["JSESSIONID"] +';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"],
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            loginResp = self.session.post(loginUrl, data = loginPostData, headers = loginHeaders, verify = False, allow_redirects = True) 
#             print(loginPostData)
            #print(loginResp.text)
#             print(str(round(time.time() * 1000)))
#             print("current_date_time "+str(current_date_time))
            
            print(self.session.cookies)
            self.brcpSessionTicket =''
            login_responseTxt = json.loads(loginResp.text, encoding = 'utf-8')
            self.otpFlag = "0"
            if(str(login_responseTxt["responseMsg"]) == "成功"):
                self.countTime = -1
                self.loginSuccess = True
                self.brcpSessionTicket =  str(login_responseTxt["brcpSessionTicket"])
                print("LOGGED IN")
                #self.login_JSESSIONID = login_responseTxt["responseBody"]["JSESSIONID"]
                
                self.result_info['flow_no'] = self.flowNo
                #self.otpFlag = login_responseTxt["responseBody"]["otpFlag"]
                if('validToolType' in login_responseTxt.keys()):
                    self.otpFlag = str(login_responseTxt["validToolType"])
                else:
                    self.otpFlag = "0"
                Bank.uploadException(self, self.UserId, 'loginSuccess', 'OTP_' + str(self.otpFlag))
                
                '''if 'telephoneNum' in login_responseTxt["responseBody"].keys():
                    self.result_info["account_mobile"] = login_responseTxt["responseBody"]["telephoneNum"]
                if 'loginName' in login_responseTxt["responseBody"].keys():
                    self.result_info["login_name"] = login_responseTxt["responseBody"]["loginName"]
                if 'cardNo' in login_responseTxt["responseBody"].keys():
                    self.result_info["account_card_no"] = login_responseTxt["responseBody"]["cardNo"]
                if 'cardType' in login_responseTxt["responseBody"].keys():
                    self.result_info["account_card_type"] = login_responseTxt["responseBody"]["cardType"]
                if 'bankUserName' in login_responseTxt["responseBody"].keys():
                    self.result_info["login_account"] = login_responseTxt["responseBody"]["bankUserName"]'''
                #print(self.result_info)
                
                
            else:
                Bank.uploadException(self, self.UserId, 'LoginFail', str(login_responseTxt))
                self.bytePicode = None
                '''if int(login_responseTxt["errCode"]) != 0 :
                    self.bytePicode = Bank.getVerifyCode(self)'''
                self.loginSuccess = False
                self.loginMsg = login_responseTxt["responseMsg"]
        else:
            self.loginSuccess = False
            self.loginMsg = '系统错误，请再试一次！'
            
        return self.loginSuccess
    
    def sendOTP(self):
        #print(self.session.cookies)
        time.sleep(2)
        #otpurl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/common/commonSendOtp.do?t='+str(round(time.time() * 1000))
        otpurl = 'https://bank.pingan.com.cn/rmb/brcp/uc/cust/uc-core.otp-send.do'
        '''otpurl_postData = {
                'channelType':'d',
                'responseDataType':'JSON',
                'otpType':'67'
            }'''
        otpurl_postData = {
            'channelType':'d',
            'responseDataType':'JSON',
            'appId':'netbank-pc',
            'appVersion':'2.0.0',
            'deviceType':'window',
            'deviceId':'netbank-pc',
            'channelId':'netbank-pc',
            'msgType':'12'
            }
        otpHeaderStr = {
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'46',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Host':'bank.pingan.com.cn',
                'Origin':'https://bank.pingan.com.cn',
                'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest'
            }
        otpResp = self.session.post(otpurl, data = otpurl_postData, headers = otpHeaderStr, verify = False, allow_redirects = True) 
        #print(otpResp.text)#741716
        self.otpFlag = "0"
        otpRes = json.loads(otpResp.text)
        #print(otpRes)
        if(int(otpRes["responseCode"]) == 0):
            data = {
                        'status' : 'true',
                        'step' : '1',
                        'gostep': 'otp',
                        'again' : 'true',
                        'msg': '请输入短信验证码',
                        'UserId': self.UserId,
                        'password': self.password,
                        'flowNo': self.flowNo,
                        'words' : [
                                {'ID' : 'otp' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                            ]
                    }
            return data
        else:
            returnData = Bank.init(self)
            returnData = json.loads(returnData, encoding = 'utf-8')
            returnData['msg'] = '动态密码错误，未通过校验.'
            return returnData
        #print(self.session.cookies)
    
    def getDatas(self):
        try:
            print("capture datas")
            #print(self.session.cookies)
            
            loginData = 'https://bank.pingan.com.cn/rmb/brcp/uc/cust/uc-ibank.initLoginData.do'
            userInfoHeaderStr = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'brcpSessionTicket='+self.brcpSessionTicket+';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C7D27DC5D22000024AE8160053981A45422a; BANKIDP=PAICPORTAL; responseDataType=JSON;',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            postData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'cacheFlag':'0',
                    'channelId':'netbank-pc',
                    'resource':'PC'
                }
            userInfoResp = self.session.post(loginData, data = postData, headers = userInfoHeaderStr, verify = False, allow_redirects = True) 
            #print(userInfoResp.text)
            
            msgList = 'https://bank.pingan.com.cn/rsb/brcp/cust/mpp/mc/ibp/getIbpMsgList'
            userInfoHeaderStr = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'brcpSessionTicket='+self.brcpSessionTicket+';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +';BIGipServerBROP-MOP_10.2.166.11_12_80='+ self.session.cookies["BIGipServerBROP-MOP_10.2.166.11_12_80"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            postData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'businessId':'1',
                    'msgChannel':'001'
                }
            userInfoResp = self.session.post(msgList, data = postData, headers = userInfoHeaderStr, verify = False, allow_redirects = True) 
            #print(userInfoResp.text)
            
            
            #self.login_JSESSIONID = self.session.cookies['JSESSIONID']
            time.sleep(1)
            userInfoUrl = "https://bank.pingan.com.cn/ibp/ibp4pc/work/account/acctInfoForIndex.do"
            userInfo_postdata = {
                    'channelType':'d',
                    'responseDataType':'JSON'
                }
            userInfoHeaderStr = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'brcpSessionTicket='+self.brcpSessionTicket+';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +';BIGipServerBROP-MOP_10.2.166.11_12_80='+ self.session.cookies["BIGipServerBROP-MOP_10.2.166.11_12_80"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            userInfoResp = self.session.post(userInfoUrl, data = userInfo_postdata, headers = userInfoHeaderStr, verify = False, allow_redirects = True) 
            #print(userInfoResp.text)
            user_responseTxt = json.loads(userInfoResp.text, encoding = 'utf-8')
            self.result_info["bank_code"] = 'PAB'
            self.result_info["bankName"] = '平安银行'
            self.accNum = ''
            if('responseBody' in user_responseTxt.keys()):
                cardlist = user_responseTxt['responseBody']['cardList']
                #print(cardlist)
                self.accNum = str(cardlist[0]['accNum'])
                account_balance = str(int(float(str(user_responseTxt["responseBody"]["totalBalance"])) * 100))
                self.result_info["account_balance"] = account_balance
                
                
                self.result_info["account_status"] = str(cardlist[0]["accStatus"])
                self.result_info["regist_date"] = str(cardlist[0]["openAccDate"])
                self.result_info["account_type"] = str(cardlist[0]["accType"])
            else:
                Bank.uploadException(self, self.UserId, 'user_responseTxt', str(user_responseTxt))
                if('errCode' in user_responseTxt.keys()):
                    #{'errMsg': '用户已在别处登录, 强制下线, 请重新登录', 'errCode': '900'}
                    Bank.uploadException(self, username=self.UserId, step='getDatas', errmsg=user_responseTxt['errMsg'])
                    data = Bank.init(self)
                    data = json.loads(data, encoding = 'utf-8')
                    data["msg"] = user_responseTxt['errMsg']
                    return data
                
             
            #CREDIT CARD DETAILS
            
            crdCardUrl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/creditcard/qryCreditCardRepayForIndex.do'
            crdCardHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            startPCSSOData = {
                        'channelType':'d',
                        'responseDataType':'JSON'    
                    }
            credResp = self.session.post(crdCardUrl, data = startPCSSOData, headers = crdCardHeader, verify = False, allow_redirects = False) 
#             print(credResp.text)
            #print(self.login_JSESSIONID)
            
            receiptsAnalysis = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/account/qryReceiptsAnalysis.do'
            receiptsAnalysisHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies['BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337'] +'; pcSysTxt=C7839CFC52D000028444115AB3E073F0920a; timeTxt=1493862326; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                } 
            receiptPostData = {
                    'channelType':'d',
                    'responseDataType':'JSON'
                }
            receiptsAnalysisResp = self.session.post(receiptsAnalysis, data = receiptPostData, headers = receiptsAnalysisHeader, verify = False, allow_redirects = True) 
            print("receiptsAnalysisResp Response")
#             print(receiptsAnalysisResp.text)
            
            crediturl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/creditcard/pcBindCredit.do'
            creditHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'60',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +';  pcSysTxt=C7834DFF65D00002A2E6357015401B8D81aa; timeTxt=1493779501; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            creditPostData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'urlIndex':'1',
                    'systemIndex':'1'
                }
            creditResp = self.session.post(crediturl, data = creditPostData, headers = creditHeader, verify = False, allow_redirects = True) 
            print("creditResp Response")
            #print(self.session.cookies)
            creditRespTxt = json.loads(creditResp.text, encoding = 'utf-8')
            Bank.uploadException(self, self.UserId, 'CreditResponse', str(creditRespTxt))
            
            r = creditRespTxt['response_body']['result']
            creditMsg = 'have credit card'
            
            if( r == "0"):
                try:
                    #startSSO =  "https://bank.pingan.com.cn/ibp/mobileDeviceSso/startPCSSO.jsp",
                    startPCSSO = 'https://bank.pingan.com.cn/ibp/mobileDeviceSso/startPCSSO.jsp'
                    startPCSSOHeader = {
                            'Accept':'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding':'gzip, deflate, br',
                            'Accept-Language':'zh-CN,zh;q=0.8',
                            'Connection':'keep-alive',
                            'Content-Length':'35',
                            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                            'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies['BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337'] +'; pcSysTxt=C7834DFF65D00002A2E6357015401B8D81aa; timeTxt=1493779501; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON;',
                            'Host':'bank.pingan.com.cn',
                            'Origin':'https://bank.pingan.com.cn',
                            'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                            'X-Requested-With':'XMLHttpRequest'
                        }
                    startPCSSOData = {
                            'channelType':'d',
                            'responseDataType':'JSON'    
                        }
                    startPCSSOResp = self.session.post(startPCSSO, data = startPCSSOData, headers = startPCSSOHeader, verify = False, allow_redirects = False) 
    #                 print(startPCSSOResp.text)
                    Bank.uploadException(self, self.UserId, 'credit startPCSSOResp Response', str(startPCSSOResp.text))
                    print("startPCSSOResp  Response")
                    
                    bussinessReq =  "https://bank.pingan.com.cn/ibp/ibp4pc/work/sendRequest.do"
                    bussinessHeader = {
                        'Accept':'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding':'gzip, deflate, br',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'60',
                        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                        'Cookie':'JSESSIONIDCC='+ self.session.cookies['JSESSIONIDCC'] +';BIGipServerEBANK_PrdPool='+ self.session.cookies['BIGipServerEBANK_PrdPool'] +';BIGipServerIBANK-IBP-JTC-DMZWEB-LOGIN_10.2.161.16_20_30113='+self.session.cookies['BIGipServerIBANK-IBP-JTC-DMZWEB-LOGIN_10.2.161.16_20_30113']+';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                        'Host':'bank.pingan.com.cn',
                        'Origin':'https://bank.pingan.com.cn',
                        'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html#creditCard/creditcard/index',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest'
                    }
                    bussinessPostData = {
                            'channelType':'d',
                            'responseDataType':'JSON',
                            'urlIndex':'1',
                            'systemIndex':'1'
                        }
                    bussinessResp = self.session.post(bussinessReq, data = bussinessPostData, headers = bussinessHeader, verify = False, allow_redirects = True) 
                    print("credit bussiness  Response")
                    bussinessRespTxt = json.loads(bussinessResp.text, encoding = 'utf-8')
                    Bank.uploadException(self, self.UserId, 'credit bussiness Response', str(bussinessRespTxt))
                    creditCardInfos = []
                    if int(bussinessRespTxt['errCode']) == 0:
                        
                        SERVICE_RESPONSE_RESULT = bussinessRespTxt['responseBody']['SERVICE_RESPONSE_RESULT']
                        billingCycle = bussinessRespTxt['responseBody']['billingCycle']
                        AccountNo_1 = SERVICE_RESPONSE_RESULT['accountNo']
                        AccountIndex_1 = SERVICE_RESPONSE_RESULT['accountIndex']
                        creditCardObj = {}
                        creditCardObj["actName"] = ""
                        creditCardObj["currencyName"] = ""
                        creditCardObj["creditLimit"] = ""
                        creditCardObj["availableLimit"] = ""
                        creditCardObj["cashLimit"] = ""
                        creditCardObj["openDate"] = ""
                        creditCardObj["billDay"] = str(billingCycle)
                        creditCardObj["billType"] = ""
                        creditCardObj["dueDate"] = ""
                        creditCardObj["email"] = ""
                        creditCardObj["mobile"] = ""
                        creditCardObj["homeTel"] = ""
                        creditCardObj["houseAddr"] = ""
                        creditCardObj["homeAddr"] = ""
                        creditCardObj["companyTel"] = ""
                        creditCardObj["companyName"] = ""
                        creditCardObj["companyAddr"] = ""
                        creditCardObj["billAddr"] = ""
                        creditCardObj["rmbNewBalance"] = ""
                        creditCardObj["rmbMinPay"] = ""
                        creditCardObj["rmbPaidAmt"] = ""
                        creditCardObj["ctcName"] = ""
                        creditCardObj["ctcMobile"] = ""
                        creditCardObj['actName'] = SERVICE_RESPONSE_RESULT['acctLogoDesc']
                        creditCardObj['currencyName'] = 'RMB'
                        
                        creditLimit = int(float(SERVICE_RESPONSE_RESULT['limit'])*100)
                        creditCardObj['creditLimit'] = creditLimit
                        availableLimit = int(float(SERVICE_RESPONSE_RESULT['availableLimit'])*100)
                        creditCardObj['availableLimit'] = availableLimit
                        cashLimit = int(float(SERVICE_RESPONSE_RESULT['cashLimit'])*100)
                        creditCardObj['cashLimit'] = cashLimit
                        
                        dateOpen = SERVICE_RESPONSE_RESULT['dateOpen']
                        dateOpen = dateOpen.replace('-','')
                        dateOpen = dateOpen.replace(' ','')
                        creditCardObj['openDate'] = dateOpen
                        
                        billDate = SERVICE_RESPONSE_RESULT['billDate']
                        billDate = billDate.replace('-','')
                        billDate = billDate.replace(' ','')
                        creditCardObj['billDate'] = billDate
                        
                        creditCardObj['billType'] = ''
                        dueDate = SERVICE_RESPONSE_RESULT['payOffDate']
                        dueDate = dueDate.replace('-','')
                        dueDate = dueDate.replace(' ','')
                        creditCardObj['dueDate'] = dueDate
                        
                        creditCardObj['email'] = ''
                        creditCardObj['mobile'] = ''
                        creditCardObj['homeTel'] = ''
                        creditCardObj['houseAddr'] = ''
                        creditCardObj['homeAddr'] = ''
                        creditCardObj['companyTel'] = ''
                        creditCardObj['companyName'] = ''
                        creditCardObj['companyAddr'] = ''
                        creditCardObj['billAddr'] = ''
                        cardsInfo = []
                        cardsInfoObj = {}
                        
                        sendRequestReq =  "https://bank.pingan.com.cn/ibp/ibp4pc/work/sendRequest.do"
                        sendRequestHeader = {
                            'Accept':'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding':'gzip, deflate, br',
                            'Accept-Language':'zh-CN,zh;q=0.8',
                            'Connection':'keep-alive',
                            'Content-Length':'60',
                            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                            'Cookie':'JSESSIONIDCC='+ self.session.cookies['JSESSIONIDCC'] +';BIGipServerEBANK_PrdPool='+ self.session.cookies['BIGipServerEBANK_PrdPool'] +';BIGipServerIBANK-IBP-JTC-DMZWEB-LOGIN_10.2.161.16_20_30113='+self.session.cookies['BIGipServerIBANK-IBP-JTC-DMZWEB-LOGIN_10.2.161.16_20_30113']+';BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                            'Host':'bank.pingan.com.cn',
                            'Origin':'https://bank.pingan.com.cn',
                            'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html#creditCard/creditcard/index',
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                            'X-Requested-With':'XMLHttpRequest'
                        }
                        sendRequestPostData = {
                                'channelType':'d',
                                'responseDataType':'JSON',
                                'urlIndex':'2',
                                'systemIndex':'1'
                            }
                        sendRequestResp = self.session.post(sendRequestReq, data = sendRequestPostData, headers = sendRequestHeader, verify = False, allow_redirects = True) 
                        print("credit bussiness  Response")
                        sendRequestRespTxt = json.loads(sendRequestResp.text, encoding = 'utf-8')
                        Bank.uploadException(self, self.UserId, 'credit sendRequest', str(sendRequestRespTxt))
                    
                        '''sendRequestResp = '{"errMsg":"","responseBody":{"ret_code":"000","ret_message":"success","hasUnPaidBill":true,"RMBTotalAmt":5200,"userSex":"F","userName":"杨证掬","ACCOUNT_SUMMARY_BILL":{"ORG":"242","accountBlockCode1":"","accountBlockCode2":"","accountIndex":-1093342847,"accountMemo2":"","accountNo":"2998009937968981","accountNoIndex":0,"accountSign":"1","accountType":"","accountUSBlockCode1":"","accountUSBlockCode2":"","accountsOfBill":["2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981","2998009937968981"],"acctDesc":"","acctLogoDesc":"","acountType":0,"adjustIntegral":0,"affinityUnitCode":"","available":false,"availableLimit":"","billDate":"","billTime":"","cardBlockCode":"","cardNo":"","cardSet":[],"cashLimit":"","chgIntegralTotal":0,"cpAdjustIntegral":0,"cpNewIntegralTotal":0,"currentPoint":0,"date1":"","date2":"","dateOpen":"","ddAcctNbr":"","ddAcctNbrF":"","ddBankId":"","ddBankIdF":"","ddPmt":"","ddPmtF":"","ddStatus":"","ddStatusF":"","defaultBillDate":"","dollarAmountToPayOffTotal":0,"dollarAmtTotal":0,"dollarMinAmountToPayOff2Total":0,"dollarMinAmountToPayOffTotal":0,"dollarMinRemianAmountPayOffTotal":0,"dollarRemianAmountPayOffTotal":0,"emailAddr":"","entitySubscribeFlag":false,"firstSetDate":"","flag":"","foreignORG":"","haveTwoOldAccount":"","initialLimit":0,"isDoubleCurr":false,"isShowTOACard":"","lastIntegral":0,"limit":"","localORG":"","logo":"","maskAccountNo":"2998********8981","maskMasterCardNo":"","maskOldaccountNo":"","monthlistYYYYMM":["201704","201703","201702","201701","201612","201611","201610","201609","201608","201607","201606","201605"],"monthsOfBill":["201704","201703","201702","201701","201612","201611","201610","201609","201608","201607","201606","201605"],"newIntegralTotal":0,"nextDate":"","nextaccountNo":"","oldaccountNo":"","oldaccountNoIndex":0,"partyNo":"","payOffDate":"","payoffDetail":[{"accrualAmount":0,"adjustAmount":0,"amountToPayOff":0,"amountToPayOff2":0,"availableLimit":"","billAmount":0,"cashLimit":"","creditLimit":"","creditLmt":"","currencyType":"242","currendPage":"1","limit":"","minAmountToPayOff":0,"minAmountToPayOff2":0,"newPayBackMoney":"0","pageSize":"100","payBackMoney":"0.0","payOffDate":"","payRecords":[],"preAmountPaidOff":0,"preBillAmount":0,"remaindAmount":0,"remaindAmountValue":0,"summaryRecords":[{"currentPaymentDue":"4972.79","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201704","month2":"2017-04","month3":"2017年04月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5055.89","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201703","month2":"2017-03","month3":"2017年03月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"4948.76","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201702","month2":"2017-02","month3":"2017年02月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5068.88","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201701","month2":"2017-01","month3":"2017年01月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5003.72","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201612","month2":"2016-12","month3":"2016年12月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5107.6","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201611","month2":"2016-11","month3":"2016年11月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"4990.21","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201610","month2":"2016-10","month3":"2016年10月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5067.21","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201609","month2":"2016-09","month3":"2016年09月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5041.28","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201608","month2":"2016-08","month3":"2016年08月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"5028.12","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201607","month2":"2016-07","month3":"2016年07月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"4881.95","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201606","month2":"2016-06","month3":"2016年06月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"},{"currentPaymentDue":"4988.37","dollarcurrentPaymentDue":"","maskQryAccountNo":"2998********8981","month":"201605","month2":"2016-05","month3":"2016年05月","qryAccountIndex":-1093342847,"qryAccountNo":"2998009937968981"}],"totalConsumeAmt":"0","totalConsumeAmt2":"0","totalPage":"","totalRecNum":""}],"platinumFlg":"","postBillFlag":false,"preDate":"","prePayOffDate":"","preaccountNo":"","rmbAmountToPayOffTotal":0,"rmbAmtTotal":0,"rmbMinAmountToPayOff2Total":0,"rmbMinAmountToPayOffTotal":0,"rmbMinRemianAmountPayOffTotal":0,"rmbRemianAmountPayOffTotal":0,"settleDate":"","status":"","subscribeFlag":false,"thisBillIsNull":"","totalIntegral":0,"userAmt1":"","userAmt2":"","userCode1":"","yearIntegral":0,"ztype":false},"APPLYDISBILLDTO":{"accountNo":"","allDisBillMoney":4724.15,"amountToPayOff":4972.79,"beginDate":"","billDate":"2017-04-13","billMonth":"","billMonth2":"","cardNo":"","cardNoIndex":"","channelCode":"","constomerType":"","currentDate":{"date":2,"day":2,"hours":0,"minutes":0,"month":4,"seconds":0,"time":1493654400000,"timezoneOffset":-480,"year":117},"currentOrders":[],"currentPage":1,"deratenum":"","disbillCost":[],"discount":"","endDate":"","hasApplyDisBill":"N","hintMessage":" ● 账单分期申请时间为账单日次日至账单到期还款日","holdCardExpired":false,"ibFeeAmt":"","ibFlag":"","inputBillMonth":"","instFeeRate":"","isNewVersionFlag":"","iscanApply":"N","minAmountToPayOff":248.64,"nextTenPageIndex":10,"orderId":"","orderSet":[],"pageCount":1,"pagesShowAccount":10,"pagesize":10,"partyNo":"","payOffDate":"2017-05-01","postPattern1":"","postPattern2":"","preCost":"","preTenPageIndex":1,"procepayType":"","productCode":"","recordCount":0,"remaindAmountValue":0,"remark":"","sstageSum":"","stageNum":"","stageOption":"","stageSum":"","waiveFeeAmt":""},"SERVICE_RESPONSE_RESULT":{"ORG":"242","accountBlockCode1":"","accountBlockCode2":"","accountIndex":-1093342847,"accountMemo2":"","accountNo":"2998009937968981","accountNoIndex":0,"accountSign":"1","accountType":"","accountUSBlockCode1":"","accountUSBlockCode2":"","accountsOfBill":[],"acctDesc":"","acctLogoDesc":"","acountType":0,"adjustIntegral":0,"affinityUnitCode":"","available":false,"availableLimit":"","billDate":"","billTime":"","cardBlockCode":"","cardNo":"","cardSet":[],"cashLimit":"","chgIntegralTotal":0,"cpAdjustIntegral":0,"cpNewIntegralTotal":0,"currentPoint":0,"date1":"","date2":"","dateOpen":"","ddAcctNbr":"","ddAcctNbrF":"","ddBankId":"","ddBankIdF":"","ddPmt":"","ddPmtF":"","ddStatus":"","ddStatusF":"","defaultBillDate":"","dollarAmountToPayOffTotal":0,"dollarAmtTotal":0,"dollarMinAmountToPayOff2Total":0,"dollarMinAmountToPayOffTotal":0,"dollarMinRemianAmountPayOffTotal":0,"dollarRemianAmountPayOffTotal":0,"emailAddr":"","entitySubscribeFlag":false,"firstSetDate":"","flag":"","foreignORG":"","haveTwoOldAccount":"","initialLimit":0,"isDoubleCurr":false,"isShowTOACard":"","lastIntegral":0,"limit":"","localORG":"","logo":"","maskAccountNo":"2998********8981","maskMasterCardNo":"","maskOldaccountNo":"","monthlistYYYYMM":[],"monthsOfBill":[],"newIntegralTotal":0,"nextDate":"","nextaccountNo":"","oldaccountNo":"","oldaccountNoIndex":0,"partyNo":"","payOffDate":"","payoffDetail":[],"platinumFlg":"","postBillFlag":false,"preDate":"","prePayOffDate":"","preaccountNo":"","rmbAmountToPayOffTotal":0,"rmbAmtTotal":5200,"rmbMinAmountToPayOff2Total":0,"rmbMinAmountToPayOffTotal":0,"rmbMinRemianAmountPayOffTotal":0,"rmbRemianAmountPayOffTotal":0,"settleDate":"","status":"","subscribeFlag":false,"thisBillIsNull":"","totalIntegral":0,"userAmt1":"","userAmt2":"","userCode1":"","yearIntegral":0,"ztype":false}},"errCode":"000"}'
                        sendRequestRespTxt = json.loads(sendRequestResp, encoding = 'utf-8')'''
                        cardsInfoObj1 = {}
                        
                        cardsInfoObj1['historyBills'] = []
                        cardsInfoObj1['historyBillDetail'] = []
                        cardsInfoObj1['unsettledBillDetail'] = []
                        if int(sendRequestRespTxt['errCode']) == 0:
                            responseBody = sendRequestRespTxt['responseBody']
                        
                            cardsInfoObj['cardNo'] = ''
                            cardsInfoObj['cardType'] = ''
                            cardsInfoObj['cardAliasName'] = ''
                            cardsInfoObj['ownerName'] = responseBody['userName']
                            cardsInfoObj['openFlag'] = ''
                            
                            
                            
                            payoffDetail = responseBody['ACCOUNT_SUMMARY_BILL']['payoffDetail']
                            accountIndex = responseBody['ACCOUNT_SUMMARY_BILL']['accountIndex']
                            accountNo = responseBody['ACCOUNT_SUMMARY_BILL']['accountNo']
                            
                            monthsOfBill = responseBody['ACCOUNT_SUMMARY_BILL']['monthsOfBill']
                            
                            historyBills = []
                            for item in payoffDetail:
                                summaryRecords = item['summaryRecords']
                                for sumItem in summaryRecords:
                                    
                                    historyBillsObj = {}
                                    historyBillsObj['billMonth'] = sumItem['month']
                                    
                                    currentPaymentDue = int(float(sumItem['currentPaymentDue'])*100)
                                    historyBillsObj['totalCost'] = currentPaymentDue
                                    historyBillsObj['minPaymentAmt'] = ''
                                    historyBills.append(historyBillsObj)
                            
                            sendRequestaccountIndexPostData = {
                                    'channelType':'d',
                                    'responseDataType':'JSON',
                                    'urlIndex':'4',
                                    'systemIndex':'1',
                                    'accountNo': accountNo,
                                    'accountIndex': accountIndex
                                }
                            sendRequestaccountIndexResp = self.session.post(sendRequestReq, data = sendRequestaccountIndexPostData, headers = sendRequestHeader, verify = False, allow_redirects = True) 
                            print("credit bussiness  Response")
                            sendRequestaccountIndexTxt = json.loads(sendRequestaccountIndexResp.text, encoding = 'utf-8')
                            Bank.uploadException(self, self.UserId, 'credit sendRequest accountIndex', str(sendRequestaccountIndexTxt))
                            
                            '''sendRequestaccountIndexResp = '{"errMsg":"","responseBody":{"ret_code":"000","CUSTOMER_ACCOUNT_LIST":[{"ORG":"242","accountBlockCode1":"","accountBlockCode2":"","accountIndex":-1093342847,"accountMemo2":"","accountNo":"2998009937968981","accountNoIndex":0,"accountSign":"1","accountType":"","accountUSBlockCode1":"","accountUSBlockCode2":"","accountsOfBill":[],"acctDesc":"","acctLogoDesc":"个人信用卡","acountType":0,"adjustIntegral":0,"affinityUnitCode":"","available":true,"availableLimit":"","billDate":"","billTime":"","cardBlockCode":"","cardNo":"","cardSet":[{"LMTFlag":"","accountNo":"2998009937968981","accrCount":"","act":"N","activated":true,"activatedFlag":true,"annualFeeAmt":"","barCode":"","blockOperation":"","canPay":false,"cardAnnualFeeType":"","cardBlockCode":"","cardCategory":"G","cardConsumeAmt":"","cardCrlim":"","cardCrlimF":"","cardCrlimFlag":"","cardCrlimFlagF":"","cardFaceDescription":"","cardIndex":12820724,"cardKind":"1","cardLink":"","cardMemoDb":"","cardMemoDbF":"","cardName1":"","cardName2":"","cardNo":"6221********9772","cardNoIndex":-1440578092,"cardNoIndexMap":null,"cardRemainConsumeAmt":"","cardStat":"0","cardTechnology":"1","cardType":"C","changeCardFlag":false,"changeOrBreak":"N","coBrandNbr":"","creditLMT":"","dailySum":0,"date1":"","date2":"2018-04-16","dateA":"2013-04-16","dateNextFee":"","dateOpen":"2013-04-16","description":"平安车主卡银联金卡","dkpbBin":"","expireDate":"1804","lastDateExpire":"2016-04-15","lastYearRemainAmt":"","lastYearRemainCount":"","logo":"804","logoFCC":false,"maskCard":"","maskCardNo":"6221********9772","masterCardFlag":true,"org":"242","overdueCard":"N","partyNo":"600037757770","payOnlineLimit":0,"photoCardFlag":false,"picCardType":"0","pinOptionFlag":false,"priorActiveFlag":"N","privateLabelCreditCard":"0004","pwdFlag":"Y","queryPwd":"","queryPwdAgain":"","remainCount":"","toaCard":false,"txnPwd":""}],"cashLimit":"","chgIntegralTotal":0,"cpAdjustIntegral":0,"cpNewIntegralTotal":0,"currentPoint":0,"date1":"","date2":"","dateOpen":"2013-04-16","ddAcctNbr":"","ddAcctNbrF":"","ddBankId":"","ddBankIdF":"","ddPmt":"","ddPmtF":"","ddStatus":"","ddStatusF":"","defaultBillDate":"","dollarAmountToPayOffTotal":0,"dollarAmtTotal":0,"dollarMinAmountToPayOff2Total":0,"dollarMinAmountToPayOffTotal":0,"dollarMinRemianAmountPayOffTotal":0,"dollarRemianAmountPayOffTotal":0,"emailAddr":"","entitySubscribeFlag":false,"firstSetDate":"","flag":"","foreignORG":"","haveTwoOldAccount":"","initialLimit":0,"isDoubleCurr":false,"isShowTOACard":"","lastIntegral":0,"limit":"500000","localORG":"","logo":"998","maskAccountNo":"2998********8981","maskMasterCardNo":"6221********9772","maskOldaccountNo":"","monthlistYYYYMM":[],"monthsOfBill":[],"newIntegralTotal":0,"nextDate":"","nextaccountNo":"","oldaccountNo":"","oldaccountNoIndex":0,"partyNo":"","payOffDate":"","payoffDetail":[],"platinumFlg":"1","postBillFlag":false,"preDate":"","prePayOffDate":"","preaccountNo":"","rmbAmountToPayOffTotal":0,"rmbAmtTotal":0,"rmbMinAmountToPayOff2Total":0,"rmbMinAmountToPayOffTotal":0,"rmbMinRemianAmountPayOffTotal":0,"rmbRemianAmountPayOffTotal":0,"settleDate":"","status":"A","subscribeFlag":false,"thisBillIsNull":"","totalIntegral":0,"userAmt1":"","userAmt2":"","userCode1":"","yearIntegral":0,"ztype":false}],"SERVICE_RESPONSE_RESULT":{"ORG":"242","accountBlockCode1":"","accountBlockCode2":"","accountIndex":-1093342847,"accountMemo2":"","accountNo":"2998009937968981","accountNoIndex":0,"accountSign":"1","accountType":"","accountUSBlockCode1":"","accountUSBlockCode2":"","accountsOfBill":[],"acctDesc":"","acctLogoDesc":"","acountType":0,"adjustIntegral":0,"affinityUnitCode":"","available":false,"availableLimit":"","billDate":"","billTime":"","cardBlockCode":"","cardNo":"","cardSet":[],"cashLimit":"","chgIntegralTotal":0,"cpAdjustIntegral":0,"cpNewIntegralTotal":0,"currentPoint":0,"date1":"","date2":"","dateOpen":"","ddAcctNbr":"","ddAcctNbrF":"","ddBankId":"","ddBankIdF":"","ddPmt":"","ddPmtF":"","ddStatus":"","ddStatusF":"","defaultBillDate":"","dollarAmountToPayOffTotal":0,"dollarAmtTotal":0,"dollarMinAmountToPayOff2Total":0,"dollarMinAmountToPayOffTotal":0,"dollarMinRemianAmountPayOffTotal":0,"dollarRemianAmountPayOffTotal":0,"emailAddr":"","entitySubscribeFlag":false,"firstSetDate":"","flag":"","foreignORG":"","haveTwoOldAccount":"","initialLimit":0,"isDoubleCurr":false,"isShowTOACard":"","lastIntegral":0,"limit":"","localORG":"","logo":"","maskAccountNo":"2998********8981","maskMasterCardNo":"","maskOldaccountNo":"","monthlistYYYYMM":[],"monthsOfBill":[],"newIntegralTotal":0,"nextDate":"","nextaccountNo":"","oldaccountNo":"","oldaccountNoIndex":0,"partyNo":"","payOffDate":"","payoffDetail":[{"accrualAmount":0,"adjustAmount":0,"amountToPayOff":0,"amountToPayOff2":0,"availableLimit":"","billAmount":0,"cashLimit":"","creditLimit":"","creditLmt":"","currencyType":"242","currendPage":"1","limit":"","minAmountToPayOff":0,"minAmountToPayOff2":0,"newPayBackMoney":"5175.0","pageSize":"10","payBackMoney":"5175.0","payOffDate":"","payRecords":[{"accountNo":"","cardNo":"9772","consumeAmount":"1610.0","consumeArea":"西山康美美容养生会所","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"西山康美美容养生会所","settleDate":"0428","stxnDescTxt":"西山康美美容养生会所","txnAmount":"1610.0","txnDate":"20170427","txnDateView":"","txnDescTxt":"西山康美美容养生会所","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"1430.0","consumeArea":"昆明市盘龙区黄金鑫茶叶经营部","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"昆明市盘龙区黄金鑫茶叶经营部","settleDate":"0427","stxnDescTxt":"昆明市盘龙区黄金鑫茶叶经营部","txnAmount":"1430.0","txnDate":"20170426","txnDateView":"","txnDescTxt":"昆明市盘龙区黄金鑫茶叶经营部","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"590.0","consumeArea":"昆明市盘龙区林玲工艺品店","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"昆明市盘龙区林玲工艺品店","settleDate":"0426","stxnDescTxt":"昆明市盘龙区林玲工艺品店","txnAmount":"590.0","txnDate":"20170425","txnDateView":"","txnDescTxt":"昆明市盘龙区林玲工艺品店","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"-155.0","consumeArea":"财付通还款","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"财付通还款","settleDate":"0425","stxnDescTxt":"财付通还款","txnAmount":"-155.0","txnDate":"20170424","txnDateView":"","txnDescTxt":"财付通还款","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"1370.0","consumeArea":"昆明潮人汇娱乐会所","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"昆明潮人汇娱乐会所","settleDate":"0424","stxnDescTxt":"昆明潮人汇娱乐会所","txnAmount":"1370.0","txnDate":"20170423","txnDateView":"","txnDescTxt":"昆明潮人汇娱乐会所","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"200.0","consumeArea":"年费","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"年费","settleDate":"0416","stxnDescTxt":"年费","txnAmount":"200.0","txnDate":"20170415","txnDateView":"","txnDescTxt":"年费","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"-1100.0","consumeArea":"跨行还款","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"跨行还款","settleDate":"0426","stxnDescTxt":"跨行还款","txnAmount":"-1100.0","txnDate":"20170426","txnDateView":"","txnDescTxt":"跨行还款","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"-1900.0","consumeArea":"跨行还款","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"跨行还款","settleDate":"0425","stxnDescTxt":"跨行还款","txnAmount":"-1900.0","txnDate":"20170425","txnDateView":"","txnDescTxt":"跨行还款","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"-20.0","consumeArea":"还款","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"还款","settleDate":"0422","stxnDescTxt":"还款","txnAmount":"-20.0","txnDate":"20170422","txnDateView":"","txnDescTxt":"还款","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"-2000.0","consumeArea":"跨行还款","consumeCurType":"RMB","currencyType":"242","ntxnDescTxt":"跨行还款","settleDate":"0422","stxnDescTxt":"跨行还款","txnAmount":"-2000.0","txnDate":"20170422","txnDateView":"","txnDescTxt":"跨行还款","txnMonth":""}],"preAmountPaidOff":0,"preBillAmount":0,"remaindAmount":0,"remaindAmountValue":0,"summaryRecords":[],"totalConsumeAmt":"5200.0","totalConsumeAmt2":"0","totalPage":"","totalRecNum":"10"}],"platinumFlg":"","postBillFlag":false,"preDate":"","prePayOffDate":"","preaccountNo":"","rmbAmountToPayOffTotal":0,"rmbAmtTotal":0,"rmbMinAmountToPayOff2Total":0,"rmbMinAmountToPayOffTotal":0,"rmbMinRemianAmountPayOffTotal":0,"rmbRemianAmountPayOffTotal":0,"settleDate":"","status":"","subscribeFlag":false,"thisBillIsNull":"","totalIntegral":0,"userAmt1":"","userAmt2":"","userCode1":"","yearIntegral":0,"ztype":false}},"errCode":"000"}'
                            sendRequestaccountIndexTxt = json.loads(sendRequestaccountIndexResp, encoding = 'utf-8')    '''
                            if int(sendRequestaccountIndexTxt['errCode']) == 0:
                                CUSTOMER_ACCOUNT_LIST = sendRequestaccountIndexTxt['responseBody']['CUSTOMER_ACCOUNT_LIST']
                                for custItem in CUSTOMER_ACCOUNT_LIST:
                                    cardSet = custItem['cardSet']
                                    for cardItem in cardSet:
                                        cardsInfoObj['cardNo'] = cardItem['cardNo']
                                        cardsInfoObj['cardAliasName'] = cardItem['description']
                                    
                        
                            cardsInfoObj1['historyBills'] = historyBills
                            
                            unsettledBillDetail = []
                            unSettledBill = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/sendRequest.do'
                            unSettledData = {
                                    'channelType':'d',
                                    'responseDataType':'JSON',
                                    'urlIndex':'3',
                                    'accountNo': accountNo,
                                    'accountSign':'',
                                    'accountNoIndex':AccountIndex_1,
                                    'queryMonth':monthsOfBill[0],
                                    'acountType':'0',
                                    'currentPage':'1',
                                    'defaultBillDate':AccountIndex_1,
                                    'systemIndex':'1'
                                }
                            
                            unSettledResp = self.session.post(unSettledBill, data = unSettledData, headers = sendRequestHeader, verify = False, allow_redirects = True) 
                            print("credit unSettledResp  Response")
                            unSettledRespTxt = json.loads(unSettledResp.text, encoding = 'utf-8')
#                             print(unSettledResp)
                            Bank.uploadException(self, self.UserId, 'credit unSettledResp', str(unSettledRespTxt))
                            if int(unSettledRespTxt['errCode']) == 0:
                                responseBody = unSettledRespTxt['responseBody']
                                payRecords = responseBody['payoffDetailDto']['payRecords']
                                for items in payRecords:
                                    unsettledBillDetailObj = {}
                                    tranDate = items['txnDate']
                                    tranDate = tranDate.replace('-', '')
                                    bookedDate =  items['settleDate']
                                    bookedDate = bookedDate.replace('-', '')
                                    tranSummary =  items['txnDescTxt']
                                    tranPlace =  items['consumeArea']
                                    cardNum =  items['cardNo']
                                    if( '-' in  items['txnAmount']):
                                        payMoney = '0'
                                        incomeMoney = items['txnAmount']
                                    else:
                                        payMoney = items['txnAmount']
                                        incomeMoney = '0'
                                        
                                    incomeMoney = incomeMoney.replace(',', '')
                                    incomeMoney =  str(int(float(float(incomeMoney) * 100)))
                                    incomeMoney = incomeMoney.replace('.', '')
                                    incomeMoney = incomeMoney.replace('-', '')
                                    
                                    payMoney = payMoney.replace(',', '')
                                    payMoney =  str(int(float(float(payMoney) * 100)))
                                    payMoney = payMoney.replace('.', '')
                                    
                                    unsettledBillDetailObj["tranDate"] = tranDate
                                    unsettledBillDetailObj["bookedDate"] = bookedDate
                                    unsettledBillDetailObj["tranSummary"] = tranSummary
                                    unsettledBillDetailObj["tranPlace"] = tranPlace
                                    unsettledBillDetailObj["cardNum"] = cardNum
                                    unsettledBillDetailObj["incomeMoney"] = incomeMoney
                                    unsettledBillDetailObj["payMoney"] = payMoney
                                    
                                    unsettledBillDetail.append(unsettledBillDetailObj)
                            
                        
                            cardsInfoObj1['unsettledBillDetail'] = unsettledBillDetail
                        historyBillDetail = []
                        for month in monthsOfBill:
                            settledBill = {
                                    'channelType':'d',
                                    'responseDataType':'JSON',
                                    'urlIndex':'3',
                                    'accountNo':AccountNo_1,
                                    'accountSign':'1',
                                    'accountNoIndex': AccountIndex_1,
                                    'queryMonth': month,
                                    'acountType':'0',
                                    'currentPage':'1',
                                    'defaultBillDate': AccountIndex_1,
                                    'systemIndex':'1'
                                }
    #                         print(settledBill)
                            sendRequestMonthResp = self.session.post(sendRequestReq, data = settledBill, headers = sendRequestHeader, verify = False, allow_redirects = True) 
                            print("credit sendRequestMonthResp  Response")
                            sendRequestMonthTxt = json.loads(sendRequestMonthResp.text, encoding = 'utf-8')
                            #Bank.uploadException(self, self.UserId, 'credit sendRequestMonth', month + "_" +str(sendRequestMonthTxt))
                            
                            '''sendRequestMonthResp = '{"errMsg":"","responseBody":{"ret_code":"000","payoffDetailDto":{"accountNo":"2998009937968981","accountNoIndex":-1093342847,"acountType":0,"billType":0,"currentPage":1,"currentPayRecords":[{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"支付宝还款","settleDate":"2017-03-03","stxnDescTxt":"支付宝还款","txnAmount":"-250.0","txnDate":"2017-03-02","txnDateView":"","txnDescTxt":"支付宝还款","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"支付宝（快捷支付）","settleDate":"2017-03-03","stxnDescTxt":"支付宝（快捷支付）","txnAmount":"270.0","txnDate":"2017-03-02","txnDateView":"","txnDescTxt":"支付宝（快捷支付）","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"财付通（快捷支付）","settleDate":"2017-02-23","stxnDescTxt":"财付通（快捷支付）","txnAmount":"10.0","txnDate":"2017-02-22","txnDateView":"","txnDescTxt":"财付通（快捷支付）","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"利息","settleDate":"2017-03-13","stxnDescTxt":"利息","txnAmount":"77.13","txnDate":"2017-03-13","txnDateView":"","txnDescTxt":"利息","txnMonth":""}],"maskCardNo":"2998********8981","nextTenPageIndex":10,"oldaccountNo":"","pageCount":1,"pagesShowAccount":10,"pagesize":100,"payRecords":[{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"支付宝还款","settleDate":"2017-03-03","stxnDescTxt":"支付宝还款","txnAmount":"-250.0","txnDate":"2017-03-02","txnDateView":"","txnDescTxt":"支付宝还款","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"支付宝（快捷支付）","settleDate":"2017-03-03","stxnDescTxt":"支付宝（快捷支付）","txnAmount":"270.0","txnDate":"2017-03-02","txnDateView":"","txnDescTxt":"支付宝（快捷支付）","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"财付通（快捷支付）","settleDate":"2017-02-23","stxnDescTxt":"财付通（快捷支付）","txnAmount":"10.0","txnDate":"2017-02-22","txnDateView":"","txnDescTxt":"财付通（快捷支付）","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"利息","settleDate":"2017-03-13","stxnDescTxt":"利息","txnAmount":"77.13","txnDate":"2017-03-13","txnDateView":"","txnDescTxt":"利息","txnMonth":""}],"preTenPageIndex":1,"queryMonth":"201703","recordAccount":4},"ret_message":"success","paybackmoney":"11","SERVICE_RESPONSE_RESULT":{"ORG":"242","accountBlockCode1":"","accountBlockCode2":"","accountIndex":-1093342847,"accountMemo2":"","accountNo":"2998009937968981","accountNoIndex":0,"accountSign":"1","accountType":"","accountUSBlockCode1":"","accountUSBlockCode2":"","accountsOfBill":[],"acctDesc":"","acctLogoDesc":"","acountType":0,"adjustIntegral":0,"affinityUnitCode":"","available":false,"availableLimit":"","billDate":"2017-03-13","billTime":"","cardBlockCode":"","cardNo":"","cardSet":[],"cashLimit":"","chgIntegralTotal":0,"cpAdjustIntegral":0,"cpNewIntegralTotal":0,"currentPoint":0,"date1":"","date2":"","dateOpen":"","ddAcctNbr":"","ddAcctNbrF":"","ddBankId":"","ddBankIdF":"","ddPmt":"","ddPmtF":"","ddStatus":"","ddStatusF":"","defaultBillDate":"","dollarAmountToPayOffTotal":0,"dollarAmtTotal":0,"dollarMinAmountToPayOff2Total":0,"dollarMinAmountToPayOffTotal":0,"dollarMinRemianAmountPayOffTotal":0,"dollarRemianAmountPayOffTotal":0,"emailAddr":"","entitySubscribeFlag":false,"firstSetDate":"","flag":"","foreignORG":"","haveTwoOldAccount":"","initialLimit":0,"isDoubleCurr":false,"isShowTOACard":"","lastIntegral":0,"limit":"","localORG":"","logo":"","maskAccountNo":"2998********8981","maskMasterCardNo":"","maskOldaccountNo":"","monthlistYYYYMM":[],"monthsOfBill":[],"newIntegralTotal":0,"nextDate":"","nextaccountNo":"","oldaccountNo":"","oldaccountNoIndex":0,"partyNo":"","payOffDate":"2017-03-31","payoffDetail":[{"accrualAmount":77.13,"adjustAmount":0,"amountToPayOff":5055.89,"amountToPayOff2":0,"availableLimit":"","billAmount":280,"cashLimit":"","creditLimit":"","creditLmt":"","currencyType":"242","currendPage":"1","limit":"","minAmountToPayOff":252.79,"minAmountToPayOff2":0,"newPayBackMoney":"0","pageSize":"100","payBackMoney":"250.0","payOffDate":"","payRecords":[{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"支付宝还款","settleDate":"2017-03-03","stxnDescTxt":"支付宝还款","txnAmount":"-250.0","txnDate":"2017-03-02","txnDateView":"","txnDescTxt":"支付宝还款","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"支付宝（快捷支付）","settleDate":"2017-03-03","stxnDescTxt":"支付宝（快捷支付）","txnAmount":"270.0","txnDate":"2017-03-02","txnDateView":"","txnDescTxt":"支付宝（快捷支付）","txnMonth":""},{"accountNo":"","cardNo":"9772","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"财付通（快捷支付）","settleDate":"2017-02-23","stxnDescTxt":"财付通（快捷支付）","txnAmount":"10.0","txnDate":"2017-02-22","txnDateView":"","txnDescTxt":"财付通（快捷支付）","txnMonth":""},{"accountNo":"","cardNo":"","consumeAmount":"","consumeArea":"","consumeCurType":"","currencyType":"C001","ntxnDescTxt":"利息","settleDate":"2017-03-13","stxnDescTxt":"利息","txnAmount":"77.13","txnDate":"2017-03-13","txnDateView":"","txnDescTxt":"利息","txnMonth":""}],"preAmountPaidOff":250,"preBillAmount":4948.76,"remaindAmount":0,"remaindAmountValue":0,"summaryRecords":[],"totalConsumeAmt":"107.13","totalConsumeAmt2":"0","totalPage":"","totalRecNum":"4"}],"platinumFlg":"","postBillFlag":false,"preDate":"","prePayOffDate":"","preaccountNo":"","rmbAmountToPayOffTotal":0,"rmbAmtTotal":0,"rmbMinAmountToPayOff2Total":0,"rmbMinAmountToPayOffTotal":0,"rmbMinRemianAmountPayOffTotal":0,"rmbRemianAmountPayOffTotal":0,"settleDate":"201703","status":"","subscribeFlag":false,"thisBillIsNull":"","totalIntegral":0,"userAmt1":"","userAmt2":"","userCode1":"","yearIntegral":0,"ztype":false}},"errCode":"000"}'
                            sendRequestMonthTxt = json.loads(sendRequestMonthResp, encoding = 'utf-8') '''
                            
                            payoffDetailDto = sendRequestMonthTxt['responseBody']['payoffDetailDto']
                            payRecords = payoffDetailDto['payRecords']
                            for payRecItem in payRecords:
                                unsettledBillDetailObj = {}
                                settleDate = payRecItem['settleDate']
                                settleDate = settleDate.replace('-','')
                                settleDate = settleDate.replace(' ','')
                                unsettledBillDetailObj['tranDate'] =  settleDate
                                
                                txnDate = payRecItem['txnDate']
                                txnDate = txnDate.replace('-','')
                                txnDate = txnDate.replace(' ','')
                                unsettledBillDetailObj['bookedDate'] =  txnDate
                                
                                unsettledBillDetailObj['tranSummary'] = payRecItem['txnDescTxt']
                                unsettledBillDetailObj['tranPlace'] = ''
                                unsettledBillDetailObj['cardNum'] = payRecItem['cardNo']
                                
                                txnAmount = int(float(payRecItem['txnAmount'])*100)
                                #unsettledBillDetailObj['tranAmt'] = txnAmount
                                if( '-' in  payRecItem['txnAmount']):
                                    payMoney = '0'
                                    incomeMoney = payRecItem['txnAmount']
                                else:
                                    payMoney = payRecItem['txnAmount']
                                    incomeMoney = '0'
                                    
                                incomeMoney = incomeMoney.replace(',', '')
                                incomeMoney =  str(int(float(float(incomeMoney) * 100)))
                                incomeMoney = incomeMoney.replace('.', '')
                                incomeMoney = incomeMoney.replace('-', '')
                                
                                payMoney = payMoney.replace(',', '')
                                payMoney =  str(int(float(float(payMoney) * 100)))
                                payMoney = payMoney.replace('.', '')
                                
                                unsettledBillDetailObj["incomeMoney"] = incomeMoney
                                unsettledBillDetailObj["payMoney"] = payMoney
                                
                                historyBillDetail.append(unsettledBillDetailObj)
                        
                        cardsInfoObj1['historyBillDetail'] = historyBillDetail
                        
                        cardsInfo.append(cardsInfoObj)
                        
                        creditCardObj['cardsInfo'] = cardsInfo
                        creditCardObj['historyBills'] = cardsInfoObj1['historyBills']
                        creditCardObj['historyBillDetail'] = cardsInfoObj1['historyBillDetail']
                        creditCardObj['unsettledBillDetail'] = cardsInfoObj1['unsettledBillDetail']
                        
                        creditCardInfos.append(creditCardObj)
                    
                    
    #                 print(creditCardInfos)
                    self.result_info['creditCardInfos'] = creditCardInfos
                    Bank.uploadException(self, self.UserId, 'creditCardInfos', str(creditCardInfos))
                except Exception:
                    respText = traceback.format_exc()
#                     print(respText)
                    Bank.uploadException(self, username=self.UserId, step='creditCardException', errmsg=respText)
                
            elif( r ==  "1"):
                creditMsg = '您还未持有平安信用卡， 如需申请'
            elif( r ==   "2"):
                creditMsg = '您目前没有已设置查询密码的信用卡或卡片状态异常，或您目前一账通卡的信用账户未核发。若有疑问请拨打24小时客服热线：95511-2。'
            elif( r ==  "3"):
                creditMsg = '您的查询密码未设置，请点击'
            elif( r ==  "4"):
                creditMsg = "网络繁忙，请稍后再试。"
            else:
                creditMsg = "网络繁忙，请稍后再试。"
                
            Bank.uploadException(self, self.UserId, 'CreditResponse creditMsg', str(creditMsg))   
                
            time.sleep(1)
            #print(self.accNum)#6029071037006033
            transListUrl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/pcqryTransList.do'
            startDate = ( ( datetime.date.today()  + datetime.timedelta(1) ) + datetime.timedelta((-12)*365/12)).strftime("%Y%m%d")#(datetime.date.today() + datetime.timedelta((-12)*365/12)).strftime("%Y%m%d")
            endDate = datetime.date.today().strftime("%Y%m%d")
            transPostData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'startDate':str(startDate),
                    'endDate':str(endDate),
                    'bankType':'0',
                    'currType':'RMB',
                    'accNo':self.accNum,
                    'pageIndex':'1',
                    'accNumSelected':self.accNum,
                    'queryAccType':'1'
                }
            transHeaderStr = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'177',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            transResp = self.session.post(transListUrl, data = transPostData, headers = transHeaderStr, verify = False, allow_redirects = True) 
#             print(str(transPostData))
            transfer_responseTxt = json.loads(transResp.text, encoding = 'utf-8')
            #print(transfer_responseTxt)
            self.result_info["translist"] = []
            transList = []
            transList = transfer_responseTxt['responseBody']['transList']
            
            transListArr = []
            count = int(transfer_responseTxt['responseBody']['count'])
            pageSize = int(transfer_responseTxt['responseBody']['pageSize'])
            pageIndex = int(transfer_responseTxt['responseBody']['pageIndex'])
            
#             print("cature datas" )
#             print(str(transPostData))
            for data in transList:
                #print(data)
                income_money = "0"
                pay_money = "0"
                other_acount = data["targetAccNo"]
                other_acount_name = data["targetAccName"]
                trans_channel = data["typeName"]
                trans_currency = data["currType"]
                #trans_effect = data["typeName"]
                trans_desc = data["userRemark"]
                if(trans_desc == None):
                    trans_desc = ''
                trans_address = data["tranAddress"]
                trans_time = data["tranDate"]
                trans_type =  data["typeName"]
                trans_way = data["typeName"]
                if (str(data["ipFlag"]) == "0"): # Received money(income_money)
                    income_money = str(data["tranAmt"])
                    income_money = str(int(float(income_money) * 100))
                else:
                    pay_money = str(data["tranAmt"])
                    pay_money = str(int(float(pay_money) * 100))
                    
                balance = str(int(float(data["balance"]) * 100))   
                transListArr.append({
                        "balance": balance,
                        "other_acount":other_acount,
                        "other_acount_name" : other_acount_name,
                        "trans_channel": trans_channel,
                        "trans_currency": trans_currency,
                        "income_money": income_money,
                        "pay_money": pay_money,
                        #"trans_effect": trans_effect,
                        "trans_desc" : trans_desc,
                        "trans_address": trans_address,
                        "trans_time": trans_time,
                        "trans_type": trans_type,
                        "trans_way": trans_way
                    })
#             print(len(transListArr))
            if(count > pageSize):
                looptime = (ceil(count / pageSize)) - 1
                i = 0
                while(i < looptime):  
                    i += 1
                    pageIndex += 1
                    transPostData = {
                        'channelType':'d',
                        'responseDataType':'JSON',
                        'startDate':str(startDate),
                        'endDate':str(endDate),
                        'bankType':'0',
                        'currType':'RMB',
                        'accNo':self.accNum,
                        'pageIndex': str(pageIndex),
                        'accNumSelected':self.accNum,
                        'queryAccType':'1'
                    }
                    transResp = self.session.post(transListUrl, data = transPostData, headers = transHeaderStr, verify = False, allow_redirects = True) 
                    #print(transResp.text)
#                     print(str(transPostData))
                    transfer_responseTxt = json.loads(transResp.text, encoding = 'utf-8')
                    #print(transfer_responseTxt)
                    self.result_info["translist"] = []
                    transList = []
                    transList = transfer_responseTxt['responseBody']['transList']
                    
                    
                    count = int(transfer_responseTxt['responseBody']['count'])
                    pageSize = int(transfer_responseTxt['responseBody']['pageSize'])
                    pageIndex = int(transfer_responseTxt['responseBody']['pageIndex'])
                    
                    
                    for data in transList:
                        #print(data)
                        income_money = "0"
                        pay_money = "0"
                        other_acount = data["targetAccNo"]
                        other_acount_name = data["targetAccName"]
                        trans_channel = data["typeName"]
                        trans_currency = data["currType"]
                        #trans_effect = data["typeName"]
                        trans_desc = data["userRemark"]
                        trans_address = data["tranAddress"]
                        trans_time = data["tranDate"]
                        trans_type =  data["typeName"]
                        trans_way = data["typeName"]
                        if (str(data["ipFlag"]) == "0"): # Received money(income_money)
                            income_money = str(data["tranAmt"])
                            income_money = str(int(float(income_money) * 100))
                        else:
                            pay_money = str(data["tranAmt"])
                            pay_money = str(int(float(pay_money) * 100))
                            
                        balance = str(int(float(data["balance"]) * 100))   
                        transListArr.append({
                                "balance": balance,
                                "other_acount":other_acount,
                                "other_acount_name" : other_acount_name,
                                "trans_channel": trans_channel,
                                "trans_currency": trans_currency,
                                "income_money": income_money,
                                "pay_money": pay_money,
                                #"trans_effect": trans_effect,
                                "trans_desc" : trans_desc,
                                "trans_address": trans_address,
                                "trans_time": trans_time,
                                "trans_type": trans_type,
                                "trans_way": trans_way
                            })
            
            #print(transListArr)
            self.result_info["translist"] = transListArr
            
            
            getCustomerloanDetailUrl = "https://bank.pingan.com.cn/ibp/ibp4pc/work/loan/qryLoanInfoList.do"
            getloan_postData = {
                    'channelType':'d',
                    'responseDataType':'JSON',
                    'loan_status':'1',
                    'app_type':'01',
                    'back_end_sys_flag':'0'
                }
            getCustomerLoanHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'81',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            customerLoanResp = self.session.post(getCustomerloanDetailUrl, data = getloan_postData, headers = getCustomerLoanHeader, verify = False, allow_redirects = True) 
            print("loan Response")
            #print(customerLoanResp.text)
            custLoanresponseTxt = json.loads(customerLoanResp.text, encoding = 'utf-8')
            Bank.uploadException(self, self.UserId, 'loanResponse', str(custLoanresponseTxt))
            loanDetail = []
            if('response_body' in custLoanresponseTxt):
                acc_array = custLoanresponseTxt['response_body']['acc_array']
                # print(acc_array)
                
                if(type(acc_array) is list):
                    if(len(acc_array) != 0):
                        
                        loan_list = custLoanresponseTxt["response_body"]["loan_list"]
                        
                        for item in loan_list:
                            loanListObj = {}
                            
                            
                
                            d0 = date(int(item["loan_start_date"][0:4]), int(item["loan_start_date"][4:6]), int(item["loan_start_date"][6:]))
                            d1 = date(int(item["loan_end_date"][0:4]), int(item["loan_end_date"][4:6]), int(item["loan_end_date"][6:]))
                            delta = d0 - d1
                            months = int(floor(abs(delta.days) / 30))
                            loanListObj["loanLimit"] =  str(months)
                #             print(loanListObj["loanLimit"])
                            
                            loanListObj["loanAct"] = item["loan_acc_no"]
                            loanListObj["loanType"] = "O"
                            loanListObj["loanTypeName"] = item["show_business_type"]
                            loanListObj["openDate"] = item["loan_start_date"]
                            loanListObj["expiryDate"] = item["loan_end_date"]
                            loanAmt = str(int(abs(float(item["loan_amt"].replace(',',''))*100)))
                            loanListObj["loanAmt"] = loanAmt
                            availableAmt =  str(int(abs(float(item["availabel_amt"].replace(',',''))*100)))
                            loanListObj["availableAmt"] = availableAmt
                            loanListObj["remaPeriod"] =  str(item["residual_loan_term"])
                            loanListObj["currPeriod"] = str( int( item["residual_loan_term"] ) - 1 )
                            loanListObj["loanRate"] =  str(item["curr_rate"])
                            loanListObj["totalPenalty"] = item["penalty_amt"]
                            loanListObj["openOrg"] = str(item["loan_branch_name"])
                            loanListObj["cutPayAct"] = ""
                            loanListObj["loanBalance"] = str(int(abs(float(item["normal_corpus"].replace(',',''))*100)))#str(item["normal_corpus"])
                #             loanDetail.append(loanListObj)
                            
                            qryHistoryListurl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/loan/qryHistoryList.do'
                            qryHistoryLoanHeader = {
                                    'Accept':'application/json, text/javascript, */*; q=0.01',
                                    'Accept-Encoding':'gzip, deflate, br',
                                    'Accept-Language':'zh-CN,zh;q=0.8',
                                    'Connection':'keep-alive',
                                    'Content-Length':'81',
                                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                                    'Host':'bank.pingan.com.cn',
                                    'Origin':'https://bank.pingan.com.cn',
                                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                    'X-Requested-With':'XMLHttpRequest'
                                }
                            startDate = ( ( datetime.date.today()  + datetime.timedelta(1) ) + datetime.timedelta((-12)*365/12)).strftime("%Y-%m-%d")#(datetime.date.today() + datetime.timedelta((-12)*365/12)).strftime("%Y%m%d")
                            endDate = datetime.date.today().strftime("%Y-%m-%d")
                            qryHistory_postData = {
                                    'channelType':'d',
                                    'responseDataType':'JSON',
                                    'start_date': startDate,
                                    'end_date': endDate,
                                    'back_end_sys_flag': '0',
                                    'loan_acc_no': str(item["loan_acc_no"]),
                                    'page_index':'1',
                                    'page_size': '50'
                                }
    #                         print(qryHistory_postData)
                            qryHistoryResp = self.session.post(qryHistoryListurl, data = qryHistory_postData, headers = qryHistoryLoanHeader, verify = False, allow_redirects = True)
                            qryHistoryTxt =  json.loads(qryHistoryResp.text, encoding = 'utf-8')
    #                         qryHistoryResp = '{"ret_msg":"","ret_code":"000000","response_body":{"page_index":0,"page_size":0,"record_list":[{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"0.00","act_repay_date":"2017-04-28","act_repay_interest":"336.00","business_rate":"18.3600","ccy":"人民币","corpus_balance":"162,078.75","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"8,293.28","due_repay_date":"2017-04-26","due_repay_interest":"2,606.69","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"336.00","repay_type":"按月等额","repayment_num":"19","system_no":"947444","term":"19","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"8,168.30","act_repay_date":"2017-03-26","act_repay_interest":"2,731.67","business_rate":"18.3600","ccy":"人民币","corpus_balance":"170,372.03","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"8,168.30","due_repay_date":"2017-03-26","due_repay_interest":"2,731.67","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"18","system_no":"947444","term":"18","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"8,045.21","act_repay_date":"2017-02-26","act_repay_interest":"2,854.76","business_rate":"18.3600","ccy":"人民币","corpus_balance":"178,540.33","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"8,045.21","due_repay_date":"2017-02-26","due_repay_interest":"2,854.76","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"17","system_no":"947444","term":"17","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,923.97","act_repay_date":"2017-01-27","act_repay_interest":"2,976.00","business_rate":"18.3600","ccy":"人民币","corpus_balance":"186,585.54","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,923.97","due_repay_date":"2017-01-26","due_repay_interest":"2,976.00","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"16","system_no":"947444","term":"16","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,804.56","act_repay_date":"2016-12-27","act_repay_interest":"3,095.41","business_rate":"18.3600","ccy":"人民币","corpus_balance":"194,509.51","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,804.56","due_repay_date":"2016-12-26","due_repay_interest":"3,095.41","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"15","system_no":"947444","term":"15","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,686.95","act_repay_date":"2016-11-26","act_repay_interest":"3,213.02","business_rate":"18.3600","ccy":"人民币","corpus_balance":"202,314.07","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,686.95","due_repay_date":"2016-11-26","due_repay_interest":"3,213.02","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"14","system_no":"947444","term":"14","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,571.12","act_repay_date":"2016-10-27","act_repay_interest":"3,328.85","business_rate":"18.3600","ccy":"人民币","corpus_balance":"210,001.02","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,571.12","due_repay_date":"2016-10-26","due_repay_interest":"3,328.85","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"13","system_no":"947444","term":"13","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,457.02","act_repay_date":"2016-09-27","act_repay_interest":"3,442.95","business_rate":"18.3600","ccy":"人民币","corpus_balance":"217,572.14","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,457.02","due_repay_date":"2016-09-26","due_repay_interest":"3,442.95","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"12","system_no":"947444","term":"12","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,344.65","act_repay_date":"2016-08-26","act_repay_interest":"3,555.32","business_rate":"18.3600","ccy":"人民币","corpus_balance":"225,029.16","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,344.65","due_repay_date":"2016-08-26","due_repay_interest":"3,555.32","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"11","system_no":"947444","term":"11","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,233.97","act_repay_date":"2016-07-26","act_repay_interest":"3,666.00","business_rate":"18.3600","ccy":"人民币","corpus_balance":"232,373.81","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,233.97","due_repay_date":"2016-07-26","due_repay_interest":"3,666.00","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"10","system_no":"947444","term":"10","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,124.96","act_repay_date":"2016-06-26","act_repay_interest":"3,775.01","business_rate":"18.3600","ccy":"人民币","corpus_balance":"239,607.78","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,124.96","due_repay_date":"2016-06-26","due_repay_interest":"3,775.01","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"9","system_no":"947444","term":"9","total_count":"36"},{"acc_name":"兰倩","acct_manage_fee":"0.00","act_penalty_interest":"0.00","act_repay_acct_manage_fee":"0.00","act_repay_corpus":"7,017.59","act_repay_date":"2016-05-26","act_repay_interest":"3,882.38","business_rate":"18.3600","ccy":"人民币","corpus_balance":"246,732.74","due_penalty_interest":"0.00","due_repay_acct_manage_fee":"0.00","due_repay_corpus":"7,017.59","due_repay_date":"2016-05-26","due_repay_interest":"3,882.38","loan_acc_no":"RL20150926000438","loan_amt":"300,000.00","loan_date":"2015-09-26","loan_status":"未结清","maturity_date":"2018-09-26","poundage":"0.00","rate_type":"年","remain_corpus":"170,372.03","repay_amt":"10,899.97","repay_type":"按月等额","repayment_num":"8","system_no":"947444","term":"8","total_count":"36"}],"total_rows":0}}'
    #                         qryHistoryTxt =  json.loads(qryHistoryResp, encoding = 'utf-8')
                            record_list = qryHistoryTxt['response_body']['record_list']
                            loanHisDetail = []
                            if(type(record_list) is list):
                                if(len(record_list) != 0):
                #                     print(record_list)
                                    for item in record_list:
                                        loanHistory = {}
                                        tranDate = item['act_repay_date']
                                        
                                        endDatestr = time.strptime(tranDate,"%Y-%m-%d")
                                        tranDate = time.strftime("%Y%m%d",endDatestr)
                                        
                                        tranType = item['repay_type']
                                        
                                        tranAmt = item['repay_amt']
                                        tranAmt = str(int(abs(float(item["repay_amt"].replace(',',''))*100)))
                                        
                                        principle = item['act_repay_corpus']
                                        principle = str(int(abs(float(item["act_repay_corpus"].replace(',',''))*100)))
                                        interest = item['act_repay_interest']
                                        interest = str(int(abs(float(item["act_repay_interest"].replace(',',''))*100)))
                                        penalty = item['act_penalty_interest']
                                        penalty = str(int(abs(float(item["act_penalty_interest"].replace(',',''))*100)))
                                        
                                        term = item['term']
                                        loanHistory = {
                                                "tranDate" : tranDate,
                                                "tranType" : tranType,
                                                "tranAmt" : tranAmt,
                                                "principle" : principle,
                                                "interest" : interest,
                                                "penalty": penalty
                                            }
                                        loanHisDetail.append(loanHistory)
                                        
                                        
                            loanListObj["loanDetail"] = loanHisDetail
                            loanDetail.append(loanListObj)
                            Bank.uploadException(self, self.UserId, 'loanDetail', str(loanDetail))
            
            self.result_info['loanList'] = loanDetail
            #print(self.result_info)
            
            
            
            logouturl = 'https://bank.pingan.com.cn/ibp/ibp4pc/work/logout.do'
            logoutData = {
                    'channelType':'d',
                    'responseDataType':'JSON'
                }
            logoutHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'35',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie':'BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337='+ self.session.cookies["BIGipServerIBANK-IBP-WLS-DMZWEB_10.2.161.16_23_30336_30337"] +'; pcSysTxt=C761400283900002AA881A8B138E12F2cf8e; JSESSIONID='+ self.session.cookies['JSESSIONID'] +'; BANKIDP=PAICPORTAL; responseDataType=JSON; ',
                    'Host':'bank.pingan.com.cn',
                    'Origin':'https://bank.pingan.com.cn',
                    'Referer':'https://bank.pingan.com.cn/ibp/bank/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            logoutResp = self.session.post(logouturl, data = logoutData, headers = logoutHeader, verify = False, allow_redirects = True) 
            print("logoutResp")
#             print(logoutResp.text)
            
            if self.result_info :
                print('-----------PINGAN Successful List------------')
                self.isSuccess = Bank.uploadData( self, self.result_info)
                if self.isSuccess :
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : '操作成功'
                    }
                    Bank.uploadException(self, self.UserId, 'UploadedDatas', str(len(self.result_info['translist'])))
                    Bank.uploadException(self, self.UserId, 'Upload Data', 'Upload Data Success')
                    return returnData
                else:
                    returnData = Bank.init(self)
                    returnData = json.loads(returnData, encoding = 'utf-8')
                    returnData['msg'] = '系统繁忙,请稍后重试,code:500'
                    return returnData
        
        except Exception:
            respText = traceback.format_exc()
#             print(respText)
            Bank.uploadException(self, username=self.UserId, step='5', errmsg=respText)
            data = Bank.init(self)
            data = json.loads(data, encoding = 'utf-8')
            data["msg"] = "操作失败,请稍后重试,code:1000"
            return data
    
    def encryptForm(self , passwordstr):
        rsa = RSAKey();
        rsa.setPublic( "BB955F6C6185B341C1A42EBF1FF9971B273878DBDAB252A0F1C305EBB529E116D807E0108BE6EDD47FF8DC5B6720FFE7F413CBB4ACDFB4C6BE609A5D60F5ADB261690A77755E058D4D9C0EC4FC2F5EB623DEBC88896003FBD8AFC4C3990828C66062A6D6CE509A2B0F8E06C4E332673FB86D235164B62B6110C1F1E0625B20ED", "10001");
        res = rsa.encrypt(passwordstr);
        #print(res)   
        return res
    

import time
import math
from _operator import rshift
import random
class RSAKey():
    
    def __init__(self):
        self.n = None;
        self.e = 0;
        d = None;
        p = None;
        q = None;
        dmp1 = None;
        dmq1 = None;
        coeff = None;
        rng_state = None
        rng_pool = None
        rng_pptr = None
        this = []
        BI_RC = []
    
    
    def setPublic(self, N,E):
        self.BI_RC = []
        self.this = []
        if(N != None and E != None and len(N) > 0 and len(E) > 0):
            self.n = self.parseBigInt(N,16);
            self.e = int(E,16);
            #print(self.n.this)
            #print("end public")
        else:
            print("Invalid RSA public key");
            
    def parseBigInt(self, str,r):
        
        return BigInteger(str, r)
    
    def encrypt(self, text):
        m = self.pkcs1pad2(text, (self.n.bitLength()+7)>>3);
        '''print("Encrypt MMMM :: ")
        print(m.this)
        print(m.t)'''
        if(m == None):
            return None;
        c = self.doPublic(m)
        '''print("ccccc")
        print(c.this)
        print(c.t)'''
        if(c == None):
            return None;
        #print(c)
        h = c.toString(16);
        i = 256 - len(h);
        #for (var s = 0; s < i; s += 1)
        for s in range ( 0, i , 1):
            h = "0" + h;
        return h

          
        
    def doPublic(self, x):
        '''print("SELF.N XXXXX ")
        print(self.n.this)
        print("doPublic XXXXX ")
        print(x.this)
        print(x.t)'''
        return x.modPowInt(self.e, self.n);
        
    
    def pkcs1pad2(self, s, n):
        if(n < len(s) + 2):
            print("Message too long for RSA");
            return None;
        
        ba = [None] * 128
        i = len(s) - 1
        ii = len(s)
        if (ii < 100):
            ba[0] = 48 + ii / 10
            ba[1] = 48 + ii % 10
            ss = 2
            i = 0
            while (i < ii and n > 0):
                
                ba[ss] = ord(s[i])#s[i+1]
                i = i + 1
                ss = ss + 1
                #print(ba)
                
            u = SecureRandom()
            a = [None] * 2
            while (ss < n):
                a[0] = 0
                while (a[0] == 0):
                    u.nextBytes(a)
                ba[ss] = a[0]
                ss = ss+1
            #print(ba)
            return BigInteger(ba);  
        
    
class Arcfour():
    
    def __init__(self):
        self.thisi = 0
        self.thisj = 0
        self.thisS = [None] * 256
        
        

    def init(self, key):
        i = 0
        j = 0
        t = 0
        for i in range(256):
            self.thisS[i] = i;
        j = 0;
        for i in range(256):
            j = (j + self.thisS[i] + key[i % len(key)]) & 255;
            t = self.thisS[i];
            self.thisS[i] = self.thisS[j];
            self.thisS[j] = t;
        
        self.thisi = 0;
        self.thisj = 0;


    def next(self):
        t = None
        self.thisi = (self.thisi + 1) & 255;
        self.thisj = (self.thisj + self.thisS[self.thisi]) & 255;
        t = self.thisS[self.thisi];
        self.thisS[self.thisi] = self.thisS[self.thisj];
        self.thisS[self.thisj] = t;
        return self.thisS[(t + self.thisS[self.thisi]) & 255];


def prng_newstate():
    return Arcfour()
    
    
def nbi(): 
    return BigInteger(None)
   

class BigInteger():
    this = []
    def __init__(self, a = None, b = None, c = None):
        self.t = 0
        self.s = 0   
        self.DB = 0
        self.BI_RC = [None] * 123
        self.DM = 0
        self.this = [None] * 128
        
        dbits = 28
        
        self.DB = dbits
        self.DM = ((1<<dbits)-1)
        self.DV = (1<<dbits)
        
        self.BI_FP = 52
        self.FV = math.pow(2, self.BI_FP)
        self.F1 = self.BI_FP - dbits
        self.F2 = 2 * dbits - self.BI_FP
        
        # Digit conversions
        self.BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz";
        rr = 0
        vv = 0
        #rr = "0".charCodeAt(0);
        rr = ord("0"[0])
        #print(rr)
        for vv in range(0, 10, 1):
            self.BI_RC[rr] = vv;
            rr = rr+1
            
        #print(self.BI_RC)
        #rr = "a".charCodeAt(0);
        rr = ord("a"[0])
        #print(rr)
        #for(vv = 10; vv < 36; ++vv) BI_RC[rr++] = vv;
        for vv in range(10, 36, 1):
            #print("inside :  "+str(rr))
            self.BI_RC[rr] = vv;
            rr = rr+1
            
        #print(self.BI_RC)
        #rr = "A".charCodeAt(0);
        rr = ord("A"[0])
        #print(rr)
        #for(vv = 10; vv < 36; ++vv) BI_RC[rr++] = vv;
        for vv in range(10, 36, 1):
            self.BI_RC[rr] = vv;
            rr = rr+1
        #print(self.BI_RC)
        
        if(a != None):
            if(int == type( a) ):
                #fromNumber(a,b,c);
                print("fromnumber")
            elif(b == None and str != type(a)):
                self.fromString(a,256);
            else: 
                self.fromString(a,b);
        
    
    def ONE(self):
        return self.nbv(1)
    
    def ZERO(self):
        return self.nbv(0)
        
    def nbv(self, i):
        r = nbi()
        r.fromInt(i)
        return r
   
    
    def squareTo(self, r):
        x = self.abs()
         
        r.t = 2*x.t
        i = r.t
        i = i - 1
        while(i >= 0):
            r.this[i] = 0;
            i = i - 1
        #for(i = 0; i < x.t-1; ++i) {
        for i in range(0, x.t-1, 1):
            c = x.am(i,x.this[i],r,2*i,0,1)
            r.this[i + x.t] += x.am(i+1,2*x.this[i],r,2*i+1,c,x.t-i-1)
            if( r.this[i + x.t] >= x.DV):
                r[i+x.t] -= x.DV;
                r[i+x.t+1] = 1;
            i = i
        i = i + 1
#         print(i)
        if(r.t > 0):
            r.this[r.t-1] += x.am(i,x.this[i],r,2*i,0,1)
        r.s = 0;
        r.clamp();
       
    def multiplyTo(self, a,r):
        x = self.abs()
        y = a.abs()
        i = x.t
        r.t = i+y.t
        i = i - 1
        while(i >= 0):
            r.this[i] = 0
            i = i - 1
        #for(i = 0; i < y.t; ++i)
        for i in range( 0, y.t , 1):
            r.this[i+x.t] = x.am(0,y.this[i],r,i,0,x.t);
        r.s = 0;
        r.clamp();
        if(self.s != a.s):
            zero = BigInteger.ZERO
            zero.subTo(r,r);
        
    
    def am(self, i,x,w,j,c,n):
        xl = x&0x3fff
        xh = x>>14
        
        while(n >= 0):
            n = n - 1
            if( n != -1):
                l = self.this[i]&0x3fff
                h = self.this[i] >> 14
                i = i + 1
                m = xh*l+h*xl
                if(j == -1):
                    l = 0
                else:
                    l = xl*l+((m&0x3fff)<<14)+w.this[j]+c
                c = (l>>28)+(m>>14)+xh*h
                w.this[j] = l&0xfffffff
                j = j + 1
            
          
        
        return c;
        
    def toString(self, b):
        if(self.s < 0):
            return "-"+ self.negate().toString(b);
        k = None
        if(b == 16):
            k = 4
        elif(b == 8):
            k = 3;
        elif(b == 2):
            k = 1;
        elif(b == 32):
            k = 5;
        elif(b == 4):
            k = 2;
        else:
            return self.toRadix(b);
        km = (1<<k)-1
        d = None
        m = False
        r = ""
        i = self.t
        p = self.DB-(i*self.DB)%k;
        #i = i -1
        if(i > 0):
            i = i -1
            d = self.this[i]>>p
            if(p < self.DB and (d) > 0):
                m = True
                r = self.int2char(d)
            while(i >= 0):
                if(p < k): 
                    d = (self.this[i]&((1<<p)-1))<<(k-p);
                    
                    p = p + self.DB-k
                    d |= self.this[i]>>(p)
                    i = i -1
                else:
                    p = p - k
                    d = (self.this[i]>>(p))&km
                    if(p <= 0):
                        p += self.DB; 
                        i = i - 1
                
                if(d > 0):
                    m = True
                if(m):
                    r += self.int2char(d)
          
        if(m):
            returnstr = r
        else:
            returnstr = "0"
        return returnstr
        
    def int2char(self, n):
        return self.BI_RM[n]
       
    def intAt(self,s,i):
        #print(s)
        #print(i)
        #print(s[i])
        #print(ord(s[i]))
        c = self.BI_RC[ord(s[i])]
        #print(c)
        if(c == None):
            returnval = -1
        else:
            returnval = c
        return returnval
    
    
    
    def fromString(self,ss,b):
        k = 0
        #print(self.this)
        #print(self.BI_RC)
        
        if(b == 16):
            k = 4
        elif(b == 8): 
            k = 3
        elif(b == 256): 
            k = 8
        elif(b == 2): 
            k = 1
        elif(b == 32): 
            k = 5
        elif(b == 4): 
            k = 2
        else:
            print("fromRadix(s,b)")
            return
        self.t = 0;
        self.s = 0;
        i = len(ss)
        mi = False
        sh = 0;
        self.this = [None] * i
        
        while(i > 0):
            #print(i)
            i = i - 1
            #x = (k==8)?s[i]&0xff:intAt(s,i);
            x = 0
            if(k==8):
                if(type(ss[i]) is int):
                    x = ss[i]&0xff
                else:
                    ss[i] = int(ss[i])
                    x = ss[i]&0xff
            else:
                x = self.intAt(ss,i)
            
            if(x < 0):
                if(ss[i] == "-"):
                    mi = True;
                continue;
            
            mi = False;
            if(sh == 0):
                self.this[self.t] = x
                self.t = self.t+1
            elif(( sh + k ) > self.DB):
                
                self.this[self.t-1] |= (x & ( ( 1 << (self.DB-sh) ) -1) ) << sh
                self.this[self.t] = (x >> ( self.DB - sh ))
                self.t = self.t + 1
            
            else:
                self.this[self.t-1] |= x << sh
            sh += k
            if(sh >= self.DB):
                sh -= self.DB
            
#         print(ss[0])
        #if(k == 8 and (ss[0]&0x80) != 0):
        if(k == 8 and (int(ss[0]) &0x80) != 0):
            self.s = -1;
            if(sh > 0):
                
                self.this[self.t - 1] |= ((1<<(self.DB-sh))-1)<<sh
        
        self.clamp()
        if(mi):
            BigInteger.ZERO.subTo(self.this,self.this);
            
    def clamp(self):
        c = self.s & self.DM
        while(self.t > 0 and self.this[self.t-1] == c):
            self.t = self.t - 1;
            
    '''def Clamp(self):
      c = s & DM
      while(t > 0 and this[t-1] == c):
        --t'''
        
    def bitLength(self):
        if(self.t <= 0):
            return 0;
        return self.DB * (self.t-1) + self.nbits( self.this[self.t-1] ^ ( self.s & self.DM) )
        
    def nbits(self,x):
        r = 1
        t = rshift(x, 16)#x >>>16
        if((t) != 0):
            x = t;
            r += 16;
        t = x>>8
        if(t != 0):
            x = t; 
            r += 8; 
        t=x>>4
        if(t != 0):
            x = t; 
            r += 4;
        t = x>>2
        if((t) != 0):
            x = t; 
            r += 2; 
        t=x>>1
        if(t != 0):
            x = t; 
            r += 1; 
        return r;
            
    def modPowInt(self,e,m):
        z = None
        
        if(e < 256 or m.isEven()):
            z = Classic(m)
        else:
            z = Montgomery(m);
        return self.exp1(e,z);
    
    
    
    
    
    def exp1(self,e,z) :
        if(e > 0xffffffff or e < 1):
            return  BigInteger.ONE(self)
        r = nbi()
        #print("RRRRRRRr")
        #print(r.this)
        r2 = nbi()
        #print("RRRRRRR32222222")
        #print(r2.this)
        g = z.convert(self)
        i = self.nbits(e)-1;
        g.copyTo(r);
        #print("AFTER  RRRRRRRr")
        #print(r.this)
        
#         print("EXP1")
        #print(self.this)
#         print(i)
        while(i > 0):
            i = i -1
#             print("inside while ")
#             print(i)
            z.sqrTo(r,r2);
            if((e&(1<<i)) > 0):
                z.mulTo(r2,g,r);
            else:
                t = r; 
                r = r2; 
                r2 = t;
        
        return z.revert(r);
        

    
            
    def isEven(self):
        returnVal  = None
        if(self.t>0):
            val = (self.this[0]&1)
        else: 
            val = self.s
        
        returnVal = (val == 0)
        return returnVal
    
    def invDigit(self):
        if(self.t < 1):
            return 0;
        x = self.this[0];
        if((x&1) == 0):
            return 0;
        y = x&3
        y = (y*(2-(x&0xf)*y))&0xf
        y = (y*(2-(x&0xff)*y))&0xff
        y = (y*(2-(((x&0xffff)*y)&0xffff)))&0xffff
        y = (y*(2-x*y%self.DV))% self.DV
        returnval = None
        if( y>0):
            returnval = self.DV -y
        else:
            returnval = -y
        return returnval
    
    def compareTo(self, a):
        r = self.s - a.s;
        if(r != 0):
            return r
        i = self.t
        r = i - a.t
        if(r != 0):
            returnval = None
            if (self.s < 0):
                returnval = -r
            else:
                returnval = r
            return returnval
        
        while(i >= 0):
            i = i - 1
            r=self.this[i]-a.this[i]
            if(r != 0):
                return r;
            #i = i - 1
        return 0;
    
    def mod(self, a):
        r = nbi();
        abs().divRemTo(a,None,r);
        if(self.s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            a.subTo(r,r);
        return r;
    
    def copyTo(self, r):
        #for(i = this.t-1; i >= 0; --i):
        for i in range(self.t-1, -1,-1):
            r.this[i] = self.this[i];
        r.t = self.t;
        r.s = self.s;
        
    
    def fromInt(self, x):
        self.t = 1;
        if (x<0):
            self.s = -1
        else:
            self.s= 0
        if(x > 0):
            self.this[0] = x
        elif(x < -1):
            self.this[0] = x + self.DV
        else: 
            self.t = 0
        
    def lShiftTo(self, n,r):
        bs = n%self.DB
        cbs = self.DB-bs
        bm = (1<<cbs) -1
        ds = math.floor( n/self.DB)
        c = (self.s<<bs) & self.DM
        i = 0
        
#        for(i = this.t-1; i >= 0; --i) {
        #i = self.t-1
        #while(i >= 0):
        for i in range(self.t-1, -1, -1):
            if(self.this[i] != None):
                r.this[i+ds+1] = (self.this[i]>>cbs)|c
                c = (self.this[i]&bm)<<bs
            
        
        #for(i = ds-1; i >= 0; --i) r[i] = 0;
        i = ds-1
        for i in range(ds-1,  -1, -1):
            r.this[i] = 0;
        r.this[ds] = c;
        r.t = self.t+ds+1;
        r.s = self.s;
        r.clamp();
        #i = i - 1

    

            
    def rShiftTo(self, n,r):
        r.s = self.s;
        ds = math.floor(n/ self.DB);
        if(ds >= self.t):
            r.t = 0
            return
        bs = n%self.DB;
        cbs = self.DB-bs
        bm = (1<<bs)-1
        r.this[0] = self.this[ds]>>bs
#         for(var i = ds+1; i < this.t; ++i) {
        for i in range(ds+1, self.t, 1):
            r.this[i-ds-1] |= (self.this[i]&bm)<<cbs
            r.this[i-ds] = self.this[i]>>bs
        
        if(bs > 0):
            r.this[self.t-ds-1] |= (self.s&bm)<<cbs
        r.t = self.t-ds
        r.clamp()
        
        
    def dlShiftTo(self, n,r):
        #print(len(self.this))
#         for(i = this.t-1; i >= 0; --i) r[i+n] = this[i];
        for i in range(self.t-1, -1 , -1):
            r.this[i+n] = self.this[i]
#         for(i = n-1; i >= 0; --i) r[i] = 0;
        for i in range(n-1, -1, -1):
            r.this[i] = 0
        r.t = self.t+n;
        r.s = self.s;
    
    def drShiftTo(self, n,r):
#         for(var i = n; i < this.t; ++i) r[i-n] = this[i];
        for i in range(n, self.t, 1):
            r.this[i-n] = self.this[i]
            
        r.t = max(self.t-n,0);
        r.s = self.s;
        

        
    def subTo(self, a,r):
        i = 0
        c = 0
        m = min(a.t,self.t)
        while(i < m):
            #print(i)
            #print(self.this[i])
            #print(a.this[i])
            c = c +  self.this[i]-a.this[i]
            r.this[i] = c&self.DM;
            i = i+1
            c >>= self. DB;
        
        if(a.t < self.t):
            c -= a.s;
            while(i < self.t):
                c += self.this[i];
                r.this[i] = c&self.DM;
                c >>= self.DB;
                i = i+1
          
            c += self.s;
        
        else:
            c += self.s;
            while(i < a.t):
                c -= a.this[i]
                r.this[i] = c&self.DM
                c >>= self.DB
                i = i+1
          
            c -= a.s
        
#         r.s = (c<0)?-1:0;
        if (c<0) :
            r.s = -1
        else:
            r.s = 0
        if(c < -1):
            r.this[i] = self.DV+c
            i = i+1
        elif(c > 0):
            r.this[i] = c
            i = i+1
        r.t = i
        r.clamp()
        

    
    def divRemTo(self, m,q,r):
        pm = m.abs()
        if(pm.t <= 0):
            return
        pt = self.abs()
        if(pt.t < pm.t):
            if(q != None):
                q.fromInt(0);
            if(r != None):
                self.copyTo(r);
            return;
        
        if(r == None):
            r = nbi()
        y = nbi()
        ts = self.s
        ms = m.s
        nsh = self.DB - self.nbits(pm.this[pm.t-1])
        if(nsh > 0):
            pm.lShiftTo(nsh,y) 
            pt.lShiftTo(nsh,r)
        else:
            pm.copyTo(y)
            pt.copyTo(r); 
        ys = y.t
        y0 = y.this[ys-1]
        if(y0 == 0):
            return;
#         yt = y0*(1<<this.F1)+((ys>1)?y[ys-2]>>this.F2:0)
        if(ys>1):
            val = y.this[ys-2]>>self.F2
        else: 
            val = 0
        #print("1")
        #print(self.this)
        yt =  y0*(1<<self.F1) + val
        d1 = self.FV/yt
        d2 = (1<<self.F1)/yt
        e = 1<<self.F2;
        i = r.t
        j = i-ys
        #print("2")
        #print(self.this)
#         t = (q==null)?nbi():q;
        if (q==None):
            t = nbi()
        else:
            t = q
        y.dlShiftTo(j,t)
        #print("3")
        #print(self.this)
        if(r.compareTo(t) >= 0):
            r.this[r.t] = 1
            r.t = r.t+1
            r.subTo(t,r);
        one = BigInteger.ONE(self)
        #print("4")
        #print(self.this)
        one.dlShiftTo(ys,t);
        #print("5")
        #print(self.this)
        t.subTo(y,y);    
        while(y.t < ys):
            y.this[y.t] = 0
            y.t = y.t+1
        
        while(j >= 0):
            j = j -1
            if( j != -1):
                #if(j != -1):
        #             qd = (r[--i]==y0)?this.DM:Math.floor(r[i]*d1+(r[i-1]+e)*d2);
        
                ifcop = r.this[i]
                i = i - 1
                if  (ifcop ==y0) :
                    qd = self.DM
                else:
                    qd = math.floor(r.this[i]*d1+(r.this[i-1]+e)*d2)
                    
                r.this[i] = r.this[i] + y.am(0,qd,r,j,0,ys)
                if((r.this[i]) < qd):
                    y.dlShiftTo(j,t);
                    r.subTo(t,r);
                    #qd = qd - 1
                    while(r.this[i] < qd):
                        qd = qd - 1
                        r.subTo(t,r);
                    
            
        if(q != None):
            r.drShiftTo(ys,q);
            if(ts != ms):
                BigInteger.ZERO.subTo(q,q);
        
        r.t = ys;
        r.clamp();
        if(nsh > 0):
            r.rShiftTo(nsh,r)
        if(ts < 0):
            BigInteger.ZERO.subTo(r,r);
        

        
        
    def abs(self):
        returnVal = None
        if (self.s<0):
            returnVal = self.negate()
        else:
            returnVal = self
        return returnVal
    
    def negate(self):
        r = nbi()
        #BigInteger.ZERO.subTo(this,r)
        return r
        
        
m = None
class Classic():
    def __init__(self, m):
        self.thism = m
    def convert(self, x):
        if(x.s < 0 or x.compareTo(self.thism) >= 0):
            return x.mod(self.thism);
        else:
            return x;
    
m = None    
class  Montgomery():
    def __init__(self, m):
        self.thism = m;
        self.thismp = m.invDigit();
        self.thismpl = self.thismp&0x7fff;
        self.thismph = self.thismp>>15;
        self.thisum = (1<<(m.DB-15))-1;
        self.thismt2 = 2*m.t;
    
    def convert(self, x):
        r = nbi()
        x.abs().dlShiftTo(self.thism.t,r)
        r.divRemTo(self.thism,None,r);
        if(x.s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            self.thism.subTo(r,r)
        return r
    
    def reduce(self, x):
        while(x.t <= self.thismt2):
            x.this[x.t] = 0
            x.t = x.t + 1
        #for(var i = 0; i < this.m.t; ++i) {
        i = 0
        for  i in range( 0, self.thism.t, 1):
            j = x.this[i]&0x7fff;
            u0 = (j*self.thismpl+(((j*self.thismph+(x.this[i]>>15)*self.thismpl)&self.thisum)<<15))&x.DM;
            j = i+self.thism.t;
            x.this[j] += self.thism.am(0,u0,x,i,0,self.thism.t);
          
            while(x.this[j] >= x.DV):
                x.this[j] = x.this[j] - x.DV; 
                j = j + 1
                x.this[j] = x.this[j] + 1
        
        x.clamp();
        x.drShiftTo(self.thism.t,x);
        if(x.compareTo(self.thism) >= 0):
            x.subTo(self.thism,x);
        

    
    def sqrTo(self, x,r):
        x.squareTo(r)
        self.reduce(r)
        
    def mulTo(self, x,y,r):
        x.multiplyTo(y,r)
        self.reduce(r)
        
    def revert(self, x):
        r = nbi()
        x.copyTo(r);
        self.reduce(r);
        return r;
        
    

class SecureRandom():
    
    def __init__(self):
        self.rng_state = None
        self.rng_pool = None
        self.rng_ppt = None
        self.rng_psize = 256
        if(self.rng_pool == None):
            self.rng_pool = [None] * 256
            self.rng_pptr = 0;
            
            while(self.rng_pptr < self.rng_psize):
                t = math.floor(65536 * random.random())
                #t = math.floor(65536 * 2)
                self.rng_pool[self.rng_pptr] = rshift(t, 8)#t >>> 8
                self.rng_pptr = self.rng_pptr + 1
                
                self.rng_pool[self.rng_pptr] = t & 255
                self.rng_pptr = self.rng_pptr + 1
            
            self.rng_pptr = 0;
            self.rng_seed_time();

            
    
    def rng_get_byte(self):
        if(self.rng_state == None):
            self.rng_seed_time();
            self.rng_state = prng_newstate()
            self.rng_state.init(self.rng_pool)
            #for(rng_pptr = 0; rng_pptr < rng_pool.length; ++rng_pptr)
            rng_pptr = 0
            for rng_pptr in range(0, len(self.rng_pool), 1):
                self.rng_pool[rng_pptr] = 0;
            self.rng_pptr = 0;
          
        return self.rng_state.next();
    
    
    def nextBytes(self, ba):
        i = 0
        lencount = 0
        for jj in range( len(ba) ):
            if(ba[jj] != None):
                lencount = lencount + 1
        for i in range( 0 , lencount, 1):# (i = 0; i < ba.length; ++i):
            ba[i] = self.rng_get_byte()
            
    
    def rng_seed_int(self, x) :
        self.rng_pool[self.rng_pptr] ^= x & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 8) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 16) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 24) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        if(self.rng_pptr >= self.rng_psize):
            self.rng_pptr = self.rng_pptr - self.rng_psize
        
    
    def rng_seed_time(self):
        self.rng_seed_int(round(time.time() * 1000))
        #self.rng_seed_int(1498555878795)
    
    


