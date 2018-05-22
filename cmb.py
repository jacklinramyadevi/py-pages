# -*- coding: utf-8 -*-

"""
Created on Wed Dec  7 16:13:18 2016

@author: lwx
@bank: CMB Bank
"""

import requests
import time
import datetime
import json
from bs4 import BeautifulSoup
import re
import traceback
import calendar

class Bank():
    '''招商银行爬虫
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
    
    def init(self, params = None):
        #防止重复初始化覆盖新值
        if not hasattr(self, 'crawlerServiceUrl'):
            self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        if not hasattr(self, 'uploadExceptionUrl'):
            self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        #self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        self.jiamiUrl = 'http://api.edata.yuancredit.com/bankEncrypt'
        #self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'    
        
        if params :
            self.initCfg(self, params)  
                
        self.session = requests.Session()

        self.errExceptInfo = {}
        self.transList = {}
        self.status = 'true'
        
        self.exp_ac = ''
        self.exp_step = ''
        self.exp_msg = ''
        self.login_account = ''


        result = {
            'status':'true',
            'again':'true',
            'step':'0',
            'words':[
                        {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                        {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                    ]
        }

        return json.dumps(result)

    def doCapture(self,jsonParams):
        try:
            return Bank.doCapture1(self,jsonParams)
        except:
            ErrCode = ''
            if 'requests.exceptions.ConnectionError' in traceback.format_exc():
                ErrCode = '网络连接异常'
            respText = 'Code_000 except:'+traceback.format_exc()
            Bank.uploadException(self,self.login_account,'doCapture',respText)
            result = {
                'status':'true',
                'again':'true',
                'step':'0',
                'msg':'操作失败,Code:000 '+ErrCode,
                'words':[
                            {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                            {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                        ]
            }
            return json.dumps(result)


    def doCapture1(self,jsonParams):
        self.jsonParams = json.loads(jsonParams)
        self.flowNo = self.jsonParams['flowNo']
        
        #step 0
        if self.jsonParams.get('step')=='0':
            print('0')
            if ('AccountNo' not in self.jsonParams) or ('Password' not in self.jsonParams):
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'没有输入账号',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                #print(json.dumps(result))
                return json.dumps(result)

            #保存用户账号
            self.login_account = self.jsonParams['AccountNo']
            self.login_password = self.jsonParams['Password']

            Bank.uploadException(self,self.login_account,'step 0','calling cmb init: '+self.login_account+'--'+self.login_password)
            
            
            #-------------1-----------------登录，获取ClientNo
            self.lv = str(int(time.time()*1000))
            self.ss = str(int(time.time()*1000))
            
            self.base_Cookie = 'CMB_GenServer=LoginType:A&BranchNo:&IdType:&CreditCardLoginType:PID; WEBTRENDS_ID=116.25.98.4-3473314560.30559765; WTFPC=id=2fe6e55ac14d2dcf1651480845880328:lv='+ self.lv +':ss='+self.ss+'; AuthType=A; DeviceType=A; ProVersion='
            self.Cookie = self.base_Cookie

            login_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx'
            login_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Cookie':self.Cookie,
                'Connection':"keep-alive",
                'Upgrade-Insecure-Requests':"1"
            }
            try:
                isSuccess = False
                login1 = self.session.get(login_url,headers=login_header,verify = False)
                
                soup_login1 = BeautifulSoup(login1.content.decode(),'html.parser')
                slist = soup_login1.find('div',attrs={'class':'control-input-shortcut'}).find('img')
                
                pt_login1 = re.compile(r'ClientNo=(\w+)')
                cli_no_list = re.findall(pt_login1,slist['src'])
                if len(cli_no_list) == 0:
                    print('Not catching ClientNo')
                    isSuccess = False
                else:
                    self.ClientNo = cli_no_list[0]
                    print('ClientNo:'+self.ClientNo)
                    isSuccess = True
            except:
                respText = 'login except:'+traceback.format_exc()+'  '+login1.text
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                isSuccess = False
            if isSuccess == False:
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'初始化失败,Code:001',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)

            self.jsonParams['step'] = '1'

        #step 1
        if self.jsonParams.get('step')=='1':
            print(self.jsonParams.get('step'))
            #密码加密
            isSuccess = Bank.jiamiData(self,self.ClientNo,self.login_account,self.login_password)
            if isSuccess == False:
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'操作失败,请重试 Code:002',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                print('jiamiData fail... Go to Step0 \n')
                return json.dumps(result)
            
            self.jsonParams['step'] = '2'

        errCode = ''
        #step 2
        if self.jsonParams.get('step')=='2':
            print(self.jsonParams.get('step'))

            self.lv = str(int(time.time()*1000))
            self.base_Cookie = 'CMB_GenServer=LoginType:A&BranchNo:&IdType:&CreditCardLoginType:PID; WEBTRENDS_ID=116.25.98.4-3473314560.30559765; WTFPC=id=2fe6e55ac14d2dcf1651480845880328:lv='+ self.lv +':ss='+self.ss+'; AuthType=A; DeviceType=A; ProVersion=;'
            self.Cookie = self.base_Cookie
            print('***********************************************')
            print('before GenUniLogin \n')
            
            #-------------3-----------------登录平台
            GenUniLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenUniLogin.aspx'
            GenUniLogin_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                'Content-Type':"application/x-www-form-urlencoded",
                'Connection': 'keep-alive',
                'Cookie':self.Cookie
            }
            GenUniLogin_data = 'ClientNo='+self.ClientNo+'&CreditCardVersion=2.0'+'&AccountNo='+self.AccountNo+'&Password='+self.Password+'&HardStamp='+self.HardStamp+'&Licex='+self.Licex
            #print(GenUniLogin_data)
            try:
                isSuccess = False
                GenUniLogin_resp = self.session.post(GenUniLogin_url,headers=GenUniLogin_header,data=GenUniLogin_data,verify = False)
                #print('GenUniLogin_resp:',GenUniLogin_resp.text)
                soup = BeautifulSoup(GenUniLogin_resp.content,'html.parser')
                fs1 = soup.find_all('loginflag')
                length = len(fs1)
                print('length:'+str(length))
                if length <= 0:
                    isSuccess = False
                else:                    
                    flag = fs1[0].get_text()
                    if flag == 'N':
                        print(flag)
                        isSuccess = False
                    else:
                        isSuccess = True

                if isSuccess == False:
                    fs1 = soup.find_all('loginmessage')
                    if len(fs1) > 0:
                        errCode = fs1[0].get_text()
                    respText = 'GenUniLogin except1:'+' |'+self.login_account+' |'+self.login_password+' |'+GenUniLogin_resp.text
                    Bank.uploadException(self,self.login_account,'doCapture',respText)
            except:
                respText = 'GenUniLogin except1:'+' |'+self.login_account+' |'+self.login_password+' |'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                isSuccess = False
            if isSuccess == False:
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'登录失败,请重试 Code:003  '+errCode,
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)
                
            try:
                #searching 'LoginDeviceVerify'
                self.isSendVerify = False
                fs1 = soup.find_all('logindeviceverify')
                length = len(fs1)
                if length > 0:
                    flag = fs1[0].get_text()
                    if flag == 'M2':
                        self.isSendVerify = True
                    else:
                        self.isSendVerify = False
                else:
                    self.isSendVerify = False

                print('\nLogin Success... isSendVerify='+fs1[0].get_text()+'\n')
                
                time.sleep(1)
                
                self.ClientStamp = GenUniLogin_resp.cookies.get_dict()['ClientStamp']
                #print('GenUniLogin_resp.cookies.ClientStamp:'+self.ClientStamp)
                self.lv = str(int(time.time()*1000))
                self.base_Cookie = 'CMB_GenServer=LoginType:A&BranchNo:&IdType:&CreditCardLoginType:PID; WEBTRENDS_ID=116.25.98.4-3473314560.30559765; WTFPC=id=2fe6e55ac14d2dcf1651480845880328:lv='+ self.lv +':ss='+self.ss+'; AuthType=A; DeviceType=A; ProVersion=; ClientStamp='
                self.Cookie = self.base_Cookie + self.ClientStamp
#            self.Cookie = 'CMB_GenServer=LoginType:A&BranchNo:&IdType:&CreditCardLoginType:PID; WEBTRENDS_ID=116.25.98.4-3473314560.30559765; WTFPC=id=2fe6e55ac14d2dcf1651480845880328:lv='+ str(int(time.time()*1000)) +':ss='+str(int(time.time()*1000))+'; AuthType=A; DeviceType=A; ProVersion=; ClientStamp='+self.ClientStamp
                print('GenUniLogin_resp:  '+self.Cookie)

                if self.isSendVerify:
                    #先发短信验证码请求
                    self.jsonParams['step'] = '3'
                else:
                    #print('不发送短信验证版本...')
                    result = {
                        'status':'true',
                        'again':'true',
                        'step':'5',
                        'msg':'登录成功,不需要短信验证直接跳到Step5',
                        }
                    #return json.dumps(result)
                    self.jsonParams['step'] = '4'
            except:
                respText = 'GenUniLogin except3:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'true',
                    'again':'true',
                    'step':'0',
                    'msg':'需要初始化',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)


        if self.jsonParams.get('step')=='3' :
            #登录验证成功，则获取短信验证码
            print('start to send message code...')
            #resultCode = self.sendSmsCode()
            resultCode = '01'
            resp_text = ''
            GenLoginVerifyM2_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenLoginVerifyM2.aspx'
            GenLoginVerifyM2_headers = {
                    'Host' : 'pbsz.ebank.cmbchina.com',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cookie':self.Cookie,
                    'Content-Type':"application/x-www-form-urlencoded"
            }
            GenLoginVerifyM2_data = 'ClientNo='+self.ClientNo
    
            try:
                isSuccess = False
                resp = self.session.post(GenLoginVerifyM2_url, headers = GenLoginVerifyM2_headers, data = GenLoginVerifyM2_data, verify=False, timeout = None)
                isSuccess = True
            except:
                respText = 'GenLoginVerifyM2_1 except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                isSuccess = False
                print('sendSmsCode-->[post] cmb data error, ' + GenLoginVerifyM2_url)
                #isSuccess = False
            if isSuccess == False:
                resultCode = '01'
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:GenLoginVerifyM2_1',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)
                        
            time.sleep(1)
            
            GenLoginVerifyM2_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenLoginVerifyM2.aspx'
            GenLoginVerifyM2_headers = {
                    'Host' : 'pbsz.ebank.cmbchina.com',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cookie':self.Cookie,
                    'Content-Type':"application/x-www-form-urlencoded"
                }
            GenLoginVerifyM2_data = 'PRID=SendMSGCode&ClientNo='+self.ClientNo
            try:
                resp = self.session.post(GenLoginVerifyM2_url, headers = GenLoginVerifyM2_headers, data = GenLoginVerifyM2_data, verify=False, timeout = None)
                soup = BeautifulSoup(resp.content,"html.parser")
                fs = soup.find_all('code')
                if len(fs) == 0:
                    result = {
                        'status':'false',
                        'again':'true',
                        'step':'0',
                        'msg':'发送验证码异常',
                        'words':[
                                    {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                    {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                ]
                    }
                    return json.dumps(result)
    
                #返回码为00则表示验证码匹配
                resultCode = fs[0].get_text()
                resultCode = '00'
            except:
                respText = 'GenLoginVerifyM2_2 except:'+traceback.format_exc()+'  resp:'+resp.text
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                print('sendSmsCode-->[post] cmb data error, ' + GenLoginVerifyM2_url)
                #isSuccess = False
                resultCode = '01'
                
            #返回码为0000则表示验证码匹配
            if resultCode == '00':
                print('\nsendSmsCode... OK\n')
                result = {
                    'status':'true',
                    'again':'true',
                    'step':'4',
                    'msg':'短信验证码发送成功，请输入验证码',
                    'words':[{'ID':'verifycode','index': 0,'needUserInput':'true', 'label':'验证码', 'type': 'text'}]
                }
                return json.dumps(result)
            else:
                print('\nsendSmsCode... FAILUE \n')
                result = {
                    'status':'true',
                    'again':'true',
                    'step':'0',
                    'msg':'短信发送失败,重新登录',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)
        
        if self.jsonParams.get('step')=='4' :
            print('self.isSendVerify:',self.isSendVerify)
            if self.isSendVerify:
                #发送短信验证码
                self.verifycode = self.jsonParams['verifycode']
                #-------------4-----------------提交验证码
                VerifyMsgCode_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenLoginVerifyM2.aspx'
                VerifyMsgCode_header = {
                    'Host' : 'pbsz.ebank.cmbchina.com',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Content-Type' : 'application/x-www-form-urlencoded',
                    'Referer' : '"https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenLoginVerifyM2.aspx"',
                    'Cookie':self.Cookie,
                    'Content-Length' : '100',
                    'Connection' : 'keep-alive',
                }
                VerifyMsgCode_data = 'PRID=VerifyMSGCode'+'&ClientNo='+self.ClientNo+'&SendCode='+self.verifycode
                nCount = 1
                nNum = 2
                op = False
                while (nCount > 0 and nNum > 0):
                    try:
                        VerifyMsgCode_resp = self.session.post(VerifyMsgCode_url,headers=VerifyMsgCode_header,data=VerifyMsgCode_data,verify = False)
                        soup = BeautifulSoup(VerifyMsgCode_resp.content,"html.parser")
                        fs = soup.find_all('code')
                        if len(fs) > 0:
                            resultCode = fs[0].get_text()
                            if resultCode != '00':
                                #print('短信验证失败,请重新输入')
                                result = {
                                    'status':'true',
                                    'again':'true',
                                    'step':'0',
                                    'msg':'短信验证失败,重新操作  Code 011',
                                    'words':[
                                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'卡号/身份证号/用户名', 'type': 'text'},
                                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'密码', 'type': 'password'}
                                            ]
                                }
                                return json.dumps(result)
                        nCount = 0
                        op = True
                    except:
                        respText = 'VerifyMsgCode except:'+traceback.format_exc()
                        Bank.uploadException(self,self.login_account,'doCapture',respText)
                        nCount = 1
                        nNum = nNum -1
                        op = False
                        time.sleep(0.5)   
                if (op == False):
                    result = {
                        'status':'false',
                        'again':'true',
                        'step':'0',
                        'msg':'短信验证失败,请重新操作  Code 012',
                        'words':[
                                    {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                    {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                ]
                    }
                    return json.dumps(result)

            #发送GenIndex
            GenIndex_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx'
            GenIndex_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
            GenIndex_data = 'ClientNo=' + self.ClientNo
            GenIndex_resp = self.session.post(GenIndex_url,headers=GenIndex_header,data=GenIndex_data,verify = False)

            time.sleep(0.5)
            #开始查询账户信息
            self.account_info = {}
            self.account_info['login_account'] = self.login_account 
            self.account_info['bank_code'] = 'CMB'
            self.account_info['bankName'] = '招商银行'
            self.account_info['flow_no'] = self.flowNo
            self.account_info['creditCardInfos'] = []
            self.account_info['translist'] = []
            self.haveCreditData = False
            creditResultData = Bank.getCreditDatas(self)
            
            #---------------------------------------主页面查询Token-----------------------------
            #-------------6 MainPage ApplayToken-----------------
            ApplayToken_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/ApplyToken.aspx'
            ApplayToken_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive',
            }
            ApplayToken_data = 'ClientNo=' + self.ClientNo+'&AuthName='+'<AuthName>CBANK_HOMEPAGE</AuthName>'
            nCount = 1
            nNum = 2
            op = False
            while (nCount > 0 and nNum > 0):
                try:
                    ApplayToken_resp = self.session.post(ApplayToken_url,headers=ApplayToken_header,data=ApplayToken_data,verify = False)
    
                    soup = BeautifulSoup(ApplayToken_resp.content,'html.parser')
                    authtoken = soup.find_all('authtoken')
                    if len(authtoken):
                        AuthToken = soup.find_all('authtoken')[0]
                        
                        ResultType = soup.find_all('resulttype')[0]
                        AuthName = soup.find_all('authname')[0]
                        AuthFlag = soup.find_all('authflag')[0]
                        AuthErrorCode = soup.find_all('autherrorcode')[0]            
                        AuthMessage = soup.find_all('authmessage')[0]            
                        LoginURL = soup.find_all('loginurl')[0]            
                        AuthData = soup.find_all('authdata')[0]         
                        AuthTimestamp = soup.find_all('authtimestamp')[0]           
                        AuthSignature = soup.find_all('authsignature')[0]
                        
                        #组建处理AuthToken
                        AuthToken = '<AuthToken><Head><ResultType>'+ResultType.get_text()+'</ResultType></Head><Body><AuthName>' \
                        +AuthName.get_text()+'</AuthName><AuthFlag>'+AuthFlag.get_text()+'</AuthFlag><AuthErrorCode>'+AuthErrorCode.get_text()+'</AuthErrorCode><AuthMessage>'+AuthMessage.get_text()+'</AuthMessage><LoginURL>' \
                        +LoginURL.get_text()+'</LoginURL><AuthData>'+AuthData.get_text()+'</AuthData><AuthTimestamp>'+AuthTimestamp.get_text()+'</AuthTimestamp><AuthSignature>'+AuthSignature.get_text()+'</AuthSignature></Body></AuthToken>'
                        
                        nCount = 0
                        op = True
                    else:
                        nCount = 1
                        nNum = nNum -1
                        time.sleep(0.5)   
                except:
                    respText = 'ApplayToken except:'+traceback.format_exc()
                    Bank.uploadException(self,self.login_account,'doCapture',respText)
                    nCount = 1
                    nNum = nNum -1
                    time.sleep(0.5)  
                    op = False
            if (op == False):
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:ApplayToken',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)
                
            print('MainPage ApplayToken OK... \n')
            
            
            #-------------7-----------------主页面登录
            QueryLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_HomePage/UI/HomePagePC/Login/Login.aspx'
            QueryLogin_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive',
            }
            QueryLogin_data = {
                'AuthToken': AuthToken,
                'ClientNo' : self.ClientNo
            }
            try:
                QueryLogin_resp = self.session.post(QueryLogin_url,headers=QueryLogin_header,data=QueryLogin_data,verify = False)
                #print('QueryLogin_resp='+QueryLogin_resp.text)
                soup = BeautifulSoup(QueryLogin_resp.content,'html.parser')
                fs1 = soup.find_all('loginflag')
                if len(fs1) > 0:
                    Main_LoginFlag = fs1[0].get_text()
                    print('Main_LoginFlag:'+Main_LoginFlag)
                    if Main_LoginFlag != '0':
                        fs1 = soup.find_all('loginmessage')
                        LoginMessage = fs1[0].get_text()
                        print('Main Login fail...'+LoginMessage)
                        
                    else:
                        fs2 = soup.find_all('clientno')
                        Main_ClientNo = fs2[0].get_text()
                        print('Main_ClientNo:'+Main_ClientNo)
                    print('MainPage QueryLogin OK... \n')
            except:
                respText = 'QueryLogin except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QueryLogin',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)

            time.sleep(1)

            errCode = ''
            #-------------8-----------------查询AuthToken获取
            QueryApplayToken_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/ApplyToken.aspx'
            QueryApplayToken_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive',
            }
            QueryApplayToken_data = {
                'ClientNo' : self.ClientNo,
                'AuthName':'<AuthName>CBANK_PB</AuthName>'
            }
            nCount = 1
            nNum = 3
            op = False
            while (nCount > 0 and nNum > 0):
                try:
                    QueryApplayToken_resp = self.session.post(QueryApplayToken_url,headers=QueryApplayToken_header,data=QueryApplayToken_data,verify = False)

                    soup = BeautifulSoup(QueryApplayToken_resp.content,'html.parser')
                    authtoken = soup.find_all('authtoken')
                    if len(authtoken):
                        QueryAuthToken = soup.find_all('authtoken')[0]
                        AuthToken = soup.find_all('authtoken')[0]
                        
                        ResultType = soup.find_all('resulttype')[0]
                        AuthName = soup.find_all('authname')[0]
                        AuthFlag = soup.find_all('authflag')[0]
                        AuthErrorCode = soup.find_all('autherrorcode')[0]            
                        AuthMessage = soup.find_all('authmessage')[0]            
                        LoginURL = soup.find_all('loginurl')[0]            
                        AuthData = soup.find_all('authdata')[0]         
                        AuthTimestamp = soup.find_all('authtimestamp')[0]           
                        AuthSignature = soup.find_all('authsignature')[0]
        
                        QueryAuthToken = '<AuthToken><Head><ResultType>'+ResultType.get_text()+'</ResultType></Head><Body><AuthName>' \
                        +AuthName.get_text()+'</AuthName><AuthFlag>'+AuthFlag.get_text()+'</AuthFlag><AuthErrorCode>'+AuthErrorCode.get_text()+'</AuthErrorCode><AuthMessage>'+AuthMessage.get_text()+'</AuthMessage><LoginURL>' \
                        +LoginURL.get_text()+'</LoginURL><AuthData>'+AuthData.get_text()+'</AuthData><AuthTimestamp>'+AuthTimestamp.get_text()+'</AuthTimestamp><AuthSignature>'+AuthSignature.get_text()+'</AuthSignature></Body></AuthToken>'
                        
                        nCount = 0
                        op = True
                    else:
                        nCount = 1
                        nNum = nNum -1
                        time.sleep(0.5)
                    
                    if (op == False):
                        applymessage = soup.find_all('applymessage')
                        if len(applymessage):
                            errCode = applymessage[0].get_text()
                            
                        respText = 'QueryApplayToken except:'+QueryApplayToken_resp.text
                        Bank.uploadException(self,self.login_account,'doCapture',respText)  
                except:
                    respText = 'QueryApplayToken except:'+traceback.format_exc()
                    Bank.uploadException(self,self.login_account,'doCapture',respText)
                    nCount = 1
                    nNum = nNum -1
                    time.sleep(0.5)  
                    op = False
                
            if (op == False and self.haveCreditData == False):
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QueryApplayToken '+errCode,
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)
            elif (op == False and self.haveCreditData == True):
                isSuccess = Bank.uploadData(self, self.account_info)
                #isSuccess = True
                if isSuccess:
                    result = {
                        'status':'true',
                        'again':'false',
                        'msg':'操作成功'
                    }
                    print("Upload Data Success...")
                    Bank.uploadException(self,self.login_account,'Upload Data','Upload Data Success')
                    Bank.uploadException(self,self.login_account,'Credit card datas Upload Data', "credit card datas" )
                else:
                    #result = self.init(self)  
                    result = {
                        'status':'false',
                        'again':'true',
                        'step':'0',
                        'msg':'系统繁忙,请稍后重试(CMB_UDS)',
                        'words':[
                                    {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                    {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                ]
                    }
                    print("Upload Data fail... Waiting 2S to do it again \n")
                    Bank.uploadException(self,self.login_account,'Upload Data fail','Upload Data fail')
                    time.sleep(2)
                    
                return json.dumps(result)

            print('QueryPage QueryAuthToken OK... \n')


            #-------------9-----------------查询登录
            QueryLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_PB/UI/PBPC/Login/Login.aspx'
            QueryLogin_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive'
            }
            QueryLogin_data = {
                'AuthToken': QueryAuthToken,
                'ClientNo' : self.ClientNo
            }
#            QueryLogin_data = 'ClientNo=' + self.ClientNo+'&AuthToken='+QueryAuthToken
            try:
                QueryLogin_resp = self.session.post(QueryLogin_url,headers=QueryLogin_header,data=QueryLogin_data,verify = False)

                soup = BeautifulSoup(QueryLogin_resp.content,'html.parser')
                fs1 = soup.find_all('loginflag')
                Query_LoginFlag = fs1[0].get_text()
                print('Query_LoginFlag:'+Query_LoginFlag)
                fs2 = soup.find_all('clientno')
                self.Query_ClientNo = fs2[0].get_text()
                print('Query_ClientNo:'+self.Query_ClientNo)
                print('QueryPage QueryLogin OK... \n')
            except:
                respText = 'QueryLogin except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QueryLogin',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)


            

            
            #-------------8-----------------查询开户信息
            QryAcInfo_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_PB/UI/PBPC/DebitCard_AccountManager/am_QueryAccountInfo.aspx'
            QryAcInfo_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Connection' : 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie':self.Cookie,
                'Content-Type':'application/x-www-form-urlencoded',
                'Content-Length':'65'
            }
            QryAcInfo_data = 'ClientNo=' + self.Query_ClientNo
            try:
                QryAcInfo_resp = self.session.post(QryAcInfo_url,headers=QryAcInfo_header,data=QryAcInfo_data,verify = False)
                soup_his1 = BeautifulSoup(QryAcInfo_resp.content,'html.parser')
                s = soup_his1.find('table',attrs={'class':'dgMain'})
                td = s.find_all('td')
                index = 0
                text = ''
                for tdt in td:
                    td1 = BeautifulSoup(str(tdt),'html.parser')
                    l = td1.find('td',attrs={'class':'dgHeader'})
                    if 'td' not in str(l):
                        index = index+1
                        if (index % 4)==1:
                            text = td1.text
                        elif (index % 4)==2:
                            text = td1.text
                        elif (index % 4)==3:
                            self.account_info['login_name'] = td1.text
                        elif (index % 4)==4:
                            text = td1.text
            except:
                respText = 'QryAcInfo except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QryAcInfo',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)

            time.sleep(0.5)

            #-------------9-----------------查询子账户信息
            QrySubAc_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_PB/UI/PBPC/DebitCard_AccountManager/am_QuerySubAccount.aspx'
            QrySubAc_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Connection' : 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie':self.Cookie,
                'Content-Type':'application/x-www-form-urlencoded',
                'Content-Length':'65'
            }
            QrySubAc_data = 'ClientNo=' + self.Query_ClientNo
            try:
                QrySubAc_resp = self.session.post(QrySubAc_url,headers=QrySubAc_header,data=QrySubAc_data,verify = False)
                soup_his1 = BeautifulSoup(QrySubAc_resp.content,'html.parser')
                s = soup_his1.find('table',attrs={'class':'dgMain'})
                td = s.find_all('td')
                index = 0
                text = ''
                for tdt in td:
                    td1 = BeautifulSoup(str(tdt),'html.parser')
                    l = td1.find('td',attrs={'class':'dgHeader'})
                    if 'td' not in str(l):
                        index = index+1
                        if (index % 10)==1:
                            text = td1.text
                        elif (index % 10)==2:   #SubAcNo
                            self.account_info['account_no'] = td1.text
                        elif (index % 10)==3:   #SubAcType
                            self.account_info['account_type'] = td1.text
                        elif (index % 10)==4:   #币种currency
                            self.account_info['account_currency'] = td1.text
                        elif (index % 10)==5:   #账户余额
                            account_balance = td1.text.replace(',','')
                            account_balance.strip()
                            if account_balance == '\xa0':
                                account_balance = '0.00'
                            self.account_info['account_balance'] = str(int(abs(float(account_balance)*100)))
                        elif (index % 10)==6:   #利率 account_rate
                            text = td1.text
                        elif (index % 10)==7:   #账户状态
                            self.account_info['account_status'] = td1.text
                        elif (index % 10)==8:   #币种
                            text = td1.text
                        elif (index % 10)==9:   #币种
                            text = td1.text
                        elif (index % 10)==10:   #币种
                            text = td1.text
            except:
                respText = 'QrySubAc except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QrySubAc',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)

            #-------------9-----------------查询历史交易记录
            QueryHis0_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_PB/UI/PBPC/DebitCard_AccountManager/am_QueryHistoryTrans.aspx'
            QueryHis0_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Connection' : 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie':self.Cookie,
                'Content-Type':'application/x-www-form-urlencoded',
                'Content-Length':'65'
            }
            QueryHis0_data = 'ClientNo=' + self.Query_ClientNo
            try:
                QueryHis0_resp = self.session.post(QueryHis0_url,headers=QueryHis0_header,data=QueryHis0_data,verify = False)

                soup_his0 = BeautifulSoup(QueryHis0_resp.content,'html.parser')
                s = soup_his0.find('input',attrs={'name':'__EVENTTARGET'})
                if 'type' in str(s):
                    self.__EVENTTARGET = s['value']
                s = soup_his0.find('input',attrs={'name':'__EVENTARGUMENT'})
                if 'type' in str(s):
                    self.__EVENTARGUMENT = s['value']
                    #print('__EVENTARGUMENT:',self.__EVENTARGUMENT)
                s = soup_his0.find('input',attrs={'name':'__LASTFOCUS'})
                if 'type' in str(s):
                    self.__LASTFOCUS = s['value']
                    #print('__LASTFOCUS:',self.__LASTFOCUS)
                s = soup_his0.find('input',attrs={'name':'__VIEWSTATE'})
                if 'type' in str(s):
                    self.__VIEWSTATE = s['value']
                    #print('__VIEWSTATE:',self.__VIEWSTATE)
                s = soup_his0.find('input',attrs={'name':'__VIEWSTATEGENERATOR'})
                if 'type' in str(s):
                    self.__VIEWSTATEGENERATOR = s['value']
                    #print('__VIEWSTATEGENERATOR:',self.__VIEWSTATEGENERATOR)
                s = soup_his0.find('input',attrs={'name':'__EVENTVALIDATION'})
                if 'type' in str(s):
                    self.__EVENTVALIDATION = s['value']
                    #print('__EVENTVALIDATION:',self.__EVENTVALIDATION)
                
                s = soup_his0.find('select',attrs={'name':'ddlDebitCardList'})
                if 'name' in str(s):
                    sd = s.find('option')
                    if 'value' in str(sd):
                        self.ddlDebitCardList = sd['value']
                    print('ddlDebitCardList:',self.ddlDebitCardList)
                
                s = soup_his0.find('select',attrs={'name':'ddlSubAccountList'})
                if 'name' in str(s):
                    sd = s.find('option')
                    if 'value' in str(sd):
                        self.ddlSubAccountList = sd['value']
                    else:
                        result = {
                            'status':'true',
                            'again':'true',
                            'step':'0',
                            'msg':'请求失败,请重新操作,账户没有绑定银行卡',
                            'words':[
                                        {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                        {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                    ]
                        }
                        return json.dumps(result)
                        
                    #print('ddlSubAccountList:',self.ddlSubAccountList)

                #构造13个月的时间差
                td = datetime.datetime.now()
                y = td.year
                m =td.month
                d =td.day
                year = y
                month = td.month
                day = td.day
                if d in [31,30,29,28]:
                    if m==12:
                        day = 1
                        month = '1'
                        year = str(y)
                    else:
                        day = 1
                        month = str(m+1)
                        year = str(y-1)
                else:
                    day = d+1
                    month = str(m-1)
                    year = str(y-1)
                self.EndDate = td.strftime('%Y%m%d')
                #print('month:'+str(month)+'day:'+str(day)+'td.day:'+str(td.day))
                if int(month) == 0:
                    month = 1
                if int(day) == 0:
                    day = 1
                if int(month) < 10:
                    month = '0'+str(month)
                if int(day) < 10:
                    day = '0'+str(day)                
                self.BeginDate = str(year)+str(month)+str(day)
            except:
                respText = 'QueryHis0 except:'+traceback.format_exc()
                print('QueryHis0',respText)
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QueryHis0',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)

            print('BeginDate:'+self.BeginDate+'   EndDate:'+self.EndDate)

            time.sleep(0.5)

            #-------------9-----------------按日期查询历史交易记录
            QueryHis1_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_PB/UI/PBPC/DebitCard_AccountManager/am_QueryHistoryTrans.aspx'
            QueryHis1_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Connection' : 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie':self.Cookie,
                'Content-Type':'application/x-www-form-urlencoded'
            }
            QueryHis1_form = {
                '__EVENTTARGET':self.__EVENTTARGET,
                '__EVENTARGUMENT':self.__EVENTARGUMENT,
                '__LASTFOCUS':self.__LASTFOCUS,
                '__VIEWSTATE':self.__VIEWSTATE,
                '__VIEWSTATEGENERATOR':self.__VIEWSTATEGENERATOR,
                '__EVENTVALIDATION' : self.__EVENTVALIDATION,
                'ddlDebitCardList' : self.ddlDebitCardList,
                'ddlSubAccountList' : self.ddlSubAccountList,
                'ddlTransTypeList' : '-',
                'BeginDate' : self.BeginDate,
                'EndDate' : self.EndDate,
                'BtnOK' : '查+询',
                'uc_Adv$AdvLocID' : '',
                'ClientNo' : self.Query_ClientNo,
                'PanelControl' : ''
            }
            nCount = 1
            nNum = 3
            op = False
            QueryHis1_resp = None
            translist = []
            while (nCount > 0 and nNum > 0):
                try:
                    QueryHis1_resp = self.session.post(QueryHis1_url,headers=QueryHis1_header,data=QueryHis1_form,verify = False)
                    #print(QueryHis1_resp.text)
                    soup_his1 = BeautifulSoup(QueryHis1_resp.content,'html.parser')
                    s = soup_his1.find('table',attrs={'class':'dgMain'})
                    
                    td = s.find_all('td')
                    index = 0
                    translist = []
                    trans_info = {}
                    self.account_info['login_account'] = self.login_account 
                    self.account_info['bank_code'] = 'CMB'
                    self.account_info['bankName'] = '招商银行'
                    self.account_info['account_type'] = 'DebitCard'   
                    self.account_info['flow_no'] = self.flowNo
                    
                    trans_time = ''
                    deal_time = ''
                    for tdt in td:
                        td1 = BeautifulSoup(str(tdt),'html.parser')
                        l = td1.find('td',attrs={'class':'dgHeader'})
                        if 'td' not in str(l):
                            index = index+1
                            if (index % 7)==1:
                                #trans_time = td1.text
                                trans_time = td1.text.replace('-','')
                                #trans_info['trans_time'] = trans_time
                            elif (index % 7)==2:
                                #deal_time = td1.text
                                deal_time = td1.text.replace(':','')
                                #print('deal_time:' + deal_time)
                                #trans_info['deal_time'] = deal_time
                            elif (index % 7)==3:
                                pay_money = td1.text.replace(',','')
                                length = len(pay_money)
                                #print('pay_money:' + pay_money)
                                if pay_money == '\xa0':
                                    pay_money = '0.00'
                                trans_info['pay_money'] = str(int(abs(float(pay_money)*100)))
                            elif (index % 7)==4:
                                income_money = td1.text.replace(',','')
                                #print('income_money:' + income_money)  
                                income_money.strip()
                                if income_money == '\xa0':
                                    income_money = '0.00'
                                trans_info['income_money'] = str(int(abs(float(income_money)*100)))
                            elif (index % 7)==5:
                                balance = td1.text.replace(',','')
                                balance.strip()
                                #print('balance:' + balance) 
                                if balance == '\xa0':
                                    balance = '0.00'
                                trans_info['balance'] = str(int(abs(float(balance)*100)))
                            elif (index % 7)==6:
                                trans_type = td1.text
                                #print('trans_type:' + trans_type)
                                trans_info['trans_type'] = trans_type
                            elif (index % 7)==0:
                                deal_detail = td1.text
                                #print('deal_detail:' + deal_detail)
                                trans_info['trans_remark'] = deal_detail
                                trans_info['trans_time'] = trans_time + deal_time
                                translist.append(trans_info)
                                index = 0
                                trans_info = {}
                    nCount = 0
                    op = True

                except:
                    if(QueryHis1_resp == None):
                        respText = 'QueryHis1 except:'+traceback.format_exc()
                    else:
                        respText = 'QueryHis1 except:'+traceback.format_exc()+' QueryHis1_resp:'+QueryHis1_resp.text
                    Bank.uploadException(self,self.login_account,'doCapture',respText)
                    nCount = 1
                    nNum = nNum -1
                    time.sleep(0.5)   
            if (op == False):
                if(len(self.account_info['creditCardInfos']) == 0):
                    result = {
                        'status':'false',
                        'again':'true',
                        'step':'0',
                        'msg':'请求失败,请重新操作,Code:QueryHis1',
                        'words':[
                                    {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                    {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                ]
                    }
                    return json.dumps(result)

            print('translist len='+str(len(translist)))
            self.account_info['translist'] = translist            
            #print(self.account_info)
            
            loanList = []
            loanItem = {}
            loanDetail = []
            loanDetailItem = {}
            
            
            #------------------------查询贷款信息--------------------------#
            LoanApplayToken_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/ApplyToken.aspx'
            LoanApplayToken_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive',
            }
            LoanApplayToken_data = {
                'ClientNo' : self.ClientNo,
                'AuthName':'<AuthName>CBANK_DEBITCARD_LOAN</AuthName>'
            }
            nCount = 1
            nNum = 3
            op = False
            while (nCount > 0 and nNum > 0):
                try:
                    LoanApplayToken_resp = self.session.post(LoanApplayToken_url,headers=LoanApplayToken_header,data=LoanApplayToken_data,verify = False)

                    soup = BeautifulSoup(LoanApplayToken_resp.content,'html.parser')
                    authtoken = soup.find_all('authtoken')
                    if len(authtoken):
                        LoanAuthToken = soup.find_all('authtoken')[0]
                        AuthToken = soup.find_all('authtoken')[0]
                        
                        ResultType = soup.find_all('resulttype')[0]
                        AuthName = soup.find_all('authname')[0]
                        AuthFlag = soup.find_all('authflag')[0]
                        AuthErrorCode = soup.find_all('autherrorcode')[0]            
                        AuthMessage = soup.find_all('authmessage')[0]            
                        LoginURL = soup.find_all('loginurl')[0]            
                        AuthData = soup.find_all('authdata')[0]         
                        AuthTimestamp = soup.find_all('authtimestamp')[0]           
                        AuthSignature = soup.find_all('authsignature')[0]
        
                        LoanAuthToken = '<AuthToken><Head><ResultType>'+ResultType.get_text()+'</ResultType></Head><Body><AuthName>' \
                        +AuthName.get_text()+'</AuthName><AuthFlag>'+AuthFlag.get_text()+'</AuthFlag><AuthErrorCode>'+AuthErrorCode.get_text()+'</AuthErrorCode><AuthMessage>'+AuthMessage.get_text()+'</AuthMessage><LoginURL>' \
                        +LoginURL.get_text()+'</LoginURL><AuthData>'+AuthData.get_text()+'</AuthData><AuthTimestamp>'+AuthTimestamp.get_text()+'</AuthTimestamp><AuthSignature>'+AuthSignature.get_text()+'</AuthSignature></Body></AuthToken>'
                        
                        nCount = 0
                        op = True
                    else:
                        nCount = 1
                        nNum = nNum -1
                        time.sleep(0.5)
                        
                except:
                    respText = 'LoanApplayToken except:'+traceback.format_exc()
                    Bank.uploadException(self,self.login_account,'doCapture',respText)
                    nCount = 1
                    nNum = nNum -1
                    time.sleep(0.5)  
                    op = False
                
            if (op == False):
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:LoanApplayToken',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)

            print('LoanPage LoanAuthToken OK... \n')


            #-------------9-----------------查询贷款登录
            LoanLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_DebitCard_Loan/UI/DebitCard/Login/Login.aspx'
            LoanLogin_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive'
            }
            LoanLogin_data = {
                'AuthToken': LoanAuthToken,
                'ClientNo' : self.ClientNo
            }
#            QueryLogin_data = 'ClientNo=' + self.ClientNo+'&AuthToken='+QueryAuthToken
            try:
                LoanLogin_resp = self.session.post(LoanLogin_url,headers=LoanLogin_header,data=LoanLogin_data,verify = False)
                print(LoanLogin_resp.text)
                soup = BeautifulSoup(LoanLogin_resp.content,'html.parser')
                fs1 = soup.find_all('loginflag')
                Loan_LoginFlag = fs1[0].get_text()
                print('Loan_LoginFlag:'+Loan_LoginFlag)
                fs2 = soup.find_all('clientno')
                self.Loan_ClientNo = fs2[0].get_text()
                print('Loan_ClientNo:'+self.Loan_ClientNo)
                print('LoanPage LoanLogin OK... \n')
            except:
                respText = 'LoanLogin except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:LoanLogin',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return json.dumps(result)
            
            #
            isFindQuota = False
            QuotaQryHis_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_DebitCard_Loan/UI/DebitCard/Loan/ln_QueryPersonalAssetQuota.aspx'
            QuotaQryHis_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive'
            }
            QuotaQryHis_data = {
                'ClientNo' : self.Loan_ClientNo
            }
            try:
                QuotaQryHis_resp = self.session.post(QuotaQryHis_url,headers=QuotaQryHis_header,data=QuotaQryHis_data,verify = False)
                #print(LoanQryHis_resp.text)
                soup_loanhis = BeautifulSoup(QuotaQryHis_resp.text,'html.parser')
                s = soup_loanhis.find('table',attrs={'class':'dgMain'})
                td = s.find_all('td')
                if len(td) > 0:
                    index = 0
                    
                    for tdt in td:
                        td1 = BeautifulSoup(str(tdt),'html.parser')
                        l = td1.find('td',attrs={'class':'dgHeader'})
                        if 'td' not in str(l):
                            index = index+1
#                             if (index % 10)==1:
#                                 val = td1.text
#                                 #print('贷款查询:'+val)
#                             elif (index % 10)==2:
#                                 val = td1.text
#                                 #print('额度编号:'+val)
#                             elif (index % 10)==3:
#                                 val = td1.text
#                                 #print('业务品种:'+val)
#                             elif (index % 10)==4:
#                                 val = td1.text
#                                 #print('额度总额:'+val)
                            if (index % 10)==5:
                                val = td1.text
                                val = val.replace(',','')
                                loanItem['loanAct'] = str(int(abs(float(val)*100)))
                                #print('可用额度:'+val)
                            elif (index % 10)==6:
                                val = td1.text
#                                 print('期限（日）:'+val)
                            elif (index % 10)==7:
                                val = td1.text
                                val = val.replace('-','')
                                val = val.replace(' ','')
                                val = val + '000000'
                                loanItem['openDate'] = val
                            isFindQuota = True
                table = soup_loanhis.find('table',attrs={'id':'Table5'})
                spans = table.find_all('span',attrs={'id':'RecCount'})
                if len(spans) > 0:
                    val = spans[0].get_text()
                    #print('额度笔数:'+val)
                spans = table.find_all('span',attrs={'id':'QuotaSum'})
                if len(spans) > 0:
                    val = spans[0].get_text()
                    val = val.replace(',','')
                    val = str(int(abs(float(val)*100)))
                    #print('额度总额合计（元）:'+val)
                spans = table.find_all('span',attrs={'id':'SurQuotaSum'})
                if len(spans) > 0:
                    val = spans[0].get_text()
                    val = val.replace(',','')
                    val = str(int(abs(float(val)*100)))
                    #print('可用额度合计（元）:'+val)
                    
                QuotaIDs = re.compile('QuotaID=(.*?)\'', re.S | re.M | re.I).findall(QuotaQryHis_resp.text)
                if len(QuotaIDs) > 0:
                    QuotaID = QuotaIDs[0]
                    
                Flags = re.compile('Flag=(.*?)\'', re.S | re.M | re.I).findall(QuotaQryHis_resp.text)
                if len(Flags) > 0:
                    Flag = Flags[0]
                nCount = 0
                op = True
                print('QuotaPage LoanLogin OK... \n')
            except:
                respText = 'QuotaLogin except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'doCapture',respText)
                if isFindQuota:
                    result = {
                        'status':'false',
                        'again':'true',
                        'step':'0',
                        'msg':'请求失败,请重新操作,Code:QuotaHis',
                        'words':[
                                    {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                    {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                ]
                    }
                    return json.dumps(result)

            #
            if isFindQuota:
                isFindQuota = False
                LoanQry_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_DebitCard_Loan/UI/DebitCard/Loan/ln_QueryPersonalAssetLoan.aspx'
                LoanQry_header = {
                    'Host' : 'pbsz.ebank.cmbchina.com',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Content-Type' : 'application/x-www-form-urlencoded',
                    'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                    'Cookie':self.Cookie,
                    'Connection' : 'keep-alive'
                }
                LoanQry_data = 'ClientNo='+self.Loan_ClientNo+'&QuotaID='+QuotaID+'&Flag='+Flag
                try:
                    LoanQry_resp = self.session.post(LoanQry_url,headers=LoanQry_header,data=LoanQry_data,verify = False)
                    #print(LoanQryHis_resp.text)
                    soup_LoanQry = BeautifulSoup(LoanQry_resp.text,'html.parser')
                    table = soup_LoanQry.find('table',attrs={'class':'dgMain'})
                    td = table.find_all('td')
                    if len(td) > 0:
                        index = 0
                        for tdt in td:
                            td1 = BeautifulSoup(str(tdt),'html.parser')
                            l = td1.find('td',attrs={'class':'dgHeader'})
                            if 'td' not in str(l):
                                index = index+1
                                if (index % 9)==3:
                                    loanItem['loanType'] = 'H'
                                    loanItem['loanTypeName'] = td1.text
                                    #print('业务品种:'+td1.text)
                                elif (index % 9)==4:
                                    val = td1.text
                                    val = val.replace(',','')
                                    loanItem['loanAmt'] = str(int(abs(float(val)*100)))
                                    #print('贷款总额:'+td1.text)
                                elif (index % 9)==5:
                                    val = td1.text
                                    val = val.replace(',','')
                                    loanItem['loanBalance'] = str(int(abs(float(val)*100)))
                                    #print('贷款余额:'+td1.text)
                                elif (index % 9)==6:
                                    loanItem['remaPeriod'] = td1.text
                                    #print('剩余期数:'+td1.text)
#                                 elif (index % 9)==7:
#                                     print('还款方式:'+td1.text)
#                                 elif (index % 9)==1:
#                                     print('还款查询:'+td1.text)
#                                 elif (index % 9)==2:
#                                     print('贷款编号:'+td1.text)
                                elif (index % 9)==8:
                                    loanItem['loanSts'] = td1.text
                                    #print('贷款状态:'+td1.text)
                                elif (index % 9)==0:
                                    loanItem['loanAct'] = td1.text
                                    loanItem['cutPayAct'] = td1.text
                                    #print('扣款账号:'+td1.text)
                                    #self.account_info['loanList'].append(loanItem)
                                    
                                isFindQuota = True
                    
                    table = soup_LoanQry.find('table',attrs={'id':'Table5'})
                    spans = table.find_all('span',attrs={'id':'RecCount'})
                    if len(spans) > 0:
                        val = spans[0].get_text()
                        #print('贷款笔数:'+val)
                    spans = table.find_all('span',attrs={'id':'LoanMoneySum'})
                    if len(spans) > 0:
                        val = spans[0].get_text()
                        val = val.replace(',','')
                        val = str(int(abs(float(val)*100)))
                        #print('贷款总额合计:'+val)
                    spans = table.find_all('span',attrs={'id':'BalanceSum'})
                    if len(spans) > 0:
                        val = spans[0].get_text()
                        val = val.replace(',','')
                        val = str(int(abs(float(val)*100)))
                        #print('贷款余额合计:'+val)
                       
                    BusinessIDs = re.compile('BusinessID=(.*?)\'', re.S | re.M | re.I).findall(LoanQry_resp.text)
                    if len(BusinessIDs) > 0:
                        BusinessID = BusinessIDs[0]
                        
                    nCount = 0
                    op = True
                    print('LoanQry OK... \n')
                except:
                    respText = 'LoanQry except:'+traceback.format_exc()
                    Bank.uploadException(self,self.login_account,'doCapture',respText)
                    if isFindQuota:
                        result = {
                            'status':'false',
                            'again':'true',
                            'step':'0',
                            'msg':'请求失败,请重新操作,Code:LoanQry',
                            'words':[
                                        {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                        {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                    ]
                        }
                        return json.dumps(result)
                
                #
                if isFindQuota:
                    LoanPreBill_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_DebitCard_Loan/UI/DebitCard/Loan/ln_QueryPersonalAssetLoanPreBill.aspx'
                    LoanPreBill_header = {
                        'Host' : 'pbsz.ebank.cmbchina.com',
                        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding' : 'gzip, deflate, br',
                        'Content-Type' : 'application/x-www-form-urlencoded',
                        'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                        'Cookie':self.Cookie,
                        'Connection' : 'keep-alive'
                    }
                    LoanPreBill_data = 'ClientNo='+self.Loan_ClientNo+'&BusinessID='+BusinessID
                    try:
                        LoanPreBill_resp = self.session.post(LoanPreBill_url,headers=LoanPreBill_header,data=LoanPreBill_data,verify = False)
                        #print(LoanPreBill_resp.text)
                        index = 0
                        soup_LoanPreBill = BeautifulSoup(LoanPreBill_resp.text,'html.parser')
                        table = soup_LoanPreBill.find('table',attrs={'id':'dgRecSet'})
                        td = table.find_all('td')
                        if len(td) > 0:
                            index = 0
                            owePrinciple = 0
                            oweInterest = 0
                            principle = 0
                            interest = 0
                            for tdt in td:
                                td1 = BeautifulSoup(str(tdt),'html.parser')
                                l = td1.find('td',attrs={'class':'dgHeader'})
                                if 'td' not in str(l):
                                    index = index+1
#                                     if (index % 8)==1:
#                                         print('期次:'+td1.text)
                                    if (index % 8)==2:
                                        val = td1.text
                                        val = val.replace('-','')
                                        val = val.replace(' ','')
                                        loanDetailItem['tranDate'] = val
                                        #print('应扣日期:'+td1.text)
#                                     elif (index % 8)==3:
#                                         print('应还本金:'+td1.text)
                                    elif (index % 8)==4:
                                        val = td1.text
                                        val = val.replace(',','')
                                        principle = int(abs(float(val)*100))
                                        loanDetailItem['principle'] = str(principle)
                                        #print('实还本金:'+td1.text)
                                    elif (index % 8)==5:
                                        owePrinciple = td1.text
                                        owePrinciple = owePrinciple.replace(',','')
                                        owePrinciple = int(abs(float(owePrinciple)*100))
                                        #print('欠本:'+td1.text)
                                    #elif (index % 8)==6:
                                        #print('应还利息:'+td1.text)
                                    elif (index % 8)==7:
                                        val = td1.text
                                        val = val.replace(',','')
                                        interest = int(abs(float(val)*100))
                                        loanDetailItem['interest'] = str(interest)
                                        #print('实还利息:'+td1.text)
                                    elif (index % 8)==0:
                                        oweInterest = td1.text
                                        oweInterest = oweInterest.replace(',','')
                                        oweInterest = int(abs(float(oweInterest)*100))
                                        #print('欠息:'+td1.text)
                                        
                                        loanDetailItem['tranType'] = '还款'
                                        loanDetailItem['tranAmt'] = str(principle + interest)
                                        penalty = owePrinciple + oweInterest
                                        loanDetailItem['penalty'] = str(penalty)
                                        loanDetail.append(loanDetailItem)
                                        loanDetailItem = {}

                        loanItem['loanDetail'] = loanDetail
                        loanList.append(loanItem)
                        self.account_info['loanList'] = loanList
                        
                        table = soup_LoanPreBill.find('table',attrs={'id':'Table5'})
                        spans = table.find_all('span',attrs={'id':'RecCount'})
                        if len(spans) > 0:
                            val = spans[0].get_text()
                            #print('记录个数:'+val)
                        spans = table.find_all('span',attrs={'id':'ActPrincipalSum'})
                        if len(spans) > 0:
                            val = spans[0].get_text()
                            val = val.replace(',','')
                            val = str(int(abs(float(val)*100)))
                            #print('实还本金合计:'+val)
                        spans = table.find_all('span',attrs={'id':'ActInterestSum'})
                        if len(spans) > 0:
                            val = spans[0].get_text()
                            val = val.replace(',','')
                            val = str(int(abs(float(val)*100)))
                            #print('实还利息合计:'+val)
                           
        
                        nCount = 0
                        op = True
                        print('LoanPreBill OK... \n')
                    except:
                        respText = 'LoanPreBill except:'+traceback.format_exc()
                        Bank.uploadException(self,self.login_account,'doCapture',respText)
                        if isFindQuota:
                            result = {
                                'status':'false',
                                'again':'true',
                                'step':'0',
                                'msg':'请求失败,请重新操作,Code:LoanPreBill',
                                'words':[
                                            {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                            {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                        ]
                            }
                            return json.dumps(result)

            #print('Bank.uploadData:',json.dumps(self.account_info))
            self.jsonParams['step'] = '5'
            isSuccess = Bank.uploadData(self, self.account_info)
            #isSuccess = True
            if isSuccess:
                result = {
                    'status':'true',
                    'again':'false',
                    'msg':'操作成功'
                }
                print("Upload Data Success...")
                Bank.uploadException(self,self.login_account,'Upload Data','Upload Data Success')
                Bank.uploadException(self,self.login_account,'Len Upload Data', str(len(self.account_info['translist'])) )
            else:
                #result = self.init(self)  
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'系统繁忙,请稍后重试(CMB_UDS)',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                print("Upload Data fail... Waiting 2S to do it again \n")
                Bank.uploadException(self,self.login_account,'Upload Data fail','Upload Data fail')
                time.sleep(2)
            #print(result)
            return json.dumps(result)
        
        
    
    def applyToken_ChangeClientNo(self , AuthName , LoginUrl = ''):
        try:
            ApplyToken = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/ApplyToken.aspx'
            applyTokenHeader = {
                    'Accept': '*/*',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                    'Accept-Language': 'zh-cn',
                    'Accept-Encoding': 'gzip, deflate',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                    'Host': 'pbsz.ebank.cmbchina.com',
                    'Content-Length': '131',
                    'Connection': 'Keep-Alive',
                    'Cookie':self.Cookie
                }
            applyToken_data = 'ClientNo='+ self.ClientNo + '&AuthName=<AuthName>'+ AuthName +'</AuthName>'
            
            applyToken_resp = self.session.post(ApplyToken, headers = applyTokenHeader, data = applyToken_data, verify = False)
            print('applyTokenHeader')
#             print(applyToken_resp.text)
            soup = BeautifulSoup(applyToken_resp.text,'html.parser')
            authtoken = soup.find_all('authtoken')
            LoginURL = ''
            if len(authtoken):
                AuthToken = soup.find_all('authtoken')[0]
                
                ResultType = soup.find_all('resulttype')[0]
                AuthName = soup.find_all('authname')[0]
                AuthFlag = soup.find_all('authflag')[0]
                AuthErrorCode = soup.find_all('autherrorcode')[0]            
                AuthMessage = soup.find_all('authmessage')[0]            
                LoginURL = soup.find_all('loginurl')[0]    
                #print("tokern LoginURL: "+ str(LoginURL.get_text()))        
                AuthData = soup.find_all('authdata')[0]         
                AuthTimestamp = soup.find_all('authtimestamp')[0]           
                AuthSignature = soup.find_all('authsignature')[0]
                
                #组建处理AuthToken
                AuthToken = '<AuthToken><Head><ResultType>'+ResultType.get_text()+'</ResultType></Head><Body><AuthName>' \
                +AuthName.get_text()+'</AuthName><AuthFlag>'+AuthFlag.get_text()+'</AuthFlag><AuthErrorCode>'+AuthErrorCode.get_text()+'</AuthErrorCode><AuthMessage>'+AuthMessage.get_text()+'</AuthMessage><LoginURL>' \
                +LoginURL.get_text()+'</LoginURL><AuthData>'+AuthData.get_text()+'</AuthData><AuthTimestamp>'+AuthTimestamp.get_text()+'</AuthTimestamp><AuthSignature>'+AuthSignature.get_text()+'</AuthSignature></Body></AuthToken>'
                
            else:
                time.sleep(0.5)  
            
            print('AuthToken')
#             print(AuthToken)
            
            '''if( LoginURL == ''):
                QueryLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_HomePage/UI/HomePagePC/Login/Login.aspx'
            elif( LoginURL == 'query'):
                QueryLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Loan/UI/CreditCard/Login/Login.aspx'
            else:
                QueryLogin_url = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Account/UI/CreditCard/Login/LoginGB.aspx'''
            if(LoginURL == ''):
                return None
            
            QueryLogin_url =  'https://pbsz.ebank.cmbchina.com' + LoginURL.get_text() 
            QueryLogin_header = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                'Cookie':self.Cookie,
                'Connection' : 'keep-alive',
            }
            QueryLogin_data = {
                'AuthToken': AuthToken,
                'ClientNo' : self.ClientNo
            }
            try:
                print("QueryLogin_url "+QueryLogin_url)
                QueryLogin_resp = self.session.post(QueryLogin_url,headers=QueryLogin_header,data=QueryLogin_data,verify = False)
#                 print('QueryLogin_resp='+QueryLogin_resp.text)
                soup = BeautifulSoup(QueryLogin_resp.content,'html.parser')
                fs1 = soup.find_all('loginflag')
                if len(fs1) > 0:
                    Main_LoginFlag = fs1[0].get_text()
                    print('Main_LoginFlag:'+Main_LoginFlag)
                    if Main_LoginFlag != '0':
                        fs1 = soup.find_all('loginmessage')
                        LoginMessage = fs1[0].get_text()
                        print('Main Login fail...'+LoginMessage)
                        Bank.uploadException(self,self.login_account,'Credit Apply Token',str(AuthName) + str(LoginMessage))
                        return None
                    else:
                        fs2 = soup.find_all('clientno')
                        Main_ClientNo = fs2[0].get_text()
                        #self.ClientNo = Main_ClientNo
                        print('Main_ClientNo:'+Main_ClientNo)
                        return Main_ClientNo
                    print('MainPage QueryLogin OK... \n')
            except:
                respText = 'Credit QueryLogin except:'+traceback.format_exc()
                Bank.uploadException(self,self.login_account,'Credit applyToken_ChangeClientNo',respText)
                result = {
                    'status':'false',
                    'again':'true',
                    'step':'0',
                    'msg':'请求失败,请重新操作,Code:QueryLogin',
                    'words':[
                                {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                            ]
                }
                return 0
            
        except Exception:
#             print(traceback.format_exc())
            respText = 'Credit QueryLogin except:'+traceback.format_exc()
            Bank.uploadException(self,self.login_account,'applyToken_ChangeClientNo',respText)
            
        
    def getCreditDatas(self):
        returnData = {
                    'status' : 'true' ,
                    'success1': True,
                    'msg' : ''
                }
        try:
            creditCardInfos = []
            
            print('getCreditcards')
            print(self.ClientNo)
            CreditHomePage_clientNo = Bank.applyToken_ChangeClientNo(self , 'CBANK_HOMEPAGE')
            if(CreditHomePage_clientNo == 0):
                CreditHomePage_clientNo = self.ClientNo
            print(CreditHomePage_clientNo)
            time.sleep(0.5)
            
            creditCardObj = {}
            
            creditCardObj["actName"] = ""
            creditCardObj["currencyName"] = ""
            creditCardObj["creditLimit"] = ""
            creditCardObj["availableLimit"] = ""
            creditCardObj["cashLimit"] = ""
            creditCardObj["openDate"] = ""
            creditCardObj["billDay"] = ""
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
            
            creditHomePage = 'https://pbsz.ebank.cmbchina.com/CmbBank_HomePage/UI/HomePagePC/HomePageGen/CreditHomePage.aspx'
            creditHomeHeader = {
                    'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/msword, */*',
                    'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                    'Accept-Language': 'zh-CN',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept-Encoding': 'gzip, deflate',
                    'Host': 'pbsz.ebank.cmbchina.com',
                    'Content-Length': '83',
                    'Connection': 'Keep-Alive',
                    'Cookie': self.Cookie
                }
            creditHomeData = 'ClientNo='+ CreditHomePage_clientNo +'&DefaultMenuType=C'
            creditHome_resp = self.session.post(creditHomePage, headers = creditHomeHeader, data = creditHomeData, verify = False)
            print('creditHome')
#             print(creditHome_resp.text)
            
            QueryRegister = 'https://pbsz.ebank.cmbchina.com/CmbBank_HomePage/UI/HomePagePC/AllInOne/QueryRegisterStatusXML.aspx'
            queryRegHeader = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/xml, text/xml, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_HomePage/UI/HomePagePC/HomePageGen/CreditHomePage.aspx',
                    'Accept-Language': 'zh-cn',
                    'Accept-Encoding': 'gzip, deflate',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                    'Host': 'pbsz.ebank.cmbchina.com',
                    'Content-Length': '80',
                    'Connection': 'Keep-Alive',
                    'Cache-Control': 'no-cache',
                    'Cookie': self.Cookie
                }
            queryReg_data = 'PRID=AIOStatus&ClientNo='+ CreditHomePage_clientNo
            queryReg_resp = self.session.post(QueryRegister, headers = queryRegHeader, data = queryReg_data, verify = False)
            print('queryReg_resp')
#             print(queryReg_resp.text)
            
            am_QueryAccountClientNo = Bank.applyToken_ChangeClientNo(self, 'CBANK_CREDITCARD_ACCOUNT' , 'LOGIN_GB')
            print(am_QueryAccountClientNo)
            if(am_QueryAccountClientNo == 0 or am_QueryAccountClientNo == None):
                am_QueryAccountClientNo = self.ClientNo

            time.sleep(1)
                                #https://pbsz.ebank.cmbchina.com/CmbBank_CreditCardV2/UI/CreditCardPC/CreditCardV2_AccountManager/am_QueryAccount.aspx
            am_QueryAccount = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Account/UI/CreditCard/Account/am_QueryAccount.aspx'
            am_QueryAccount_header = {
                    'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/msword, */*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN',
                    'Connection': 'Keep-Alive',
                    'Content-Length': '65',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': self.Cookie,
                    'Host': 'pbsz.ebank.cmbchina.com',
                    'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)'
                }
            am_QueryAccount_data = 'ClientNo=' + am_QueryAccountClientNo
            
            am_QueryAccount_resp = self.session.post(am_QueryAccount, headers = am_QueryAccount_header, data = am_QueryAccount_data, verify = False)
#             print(am_QueryAccount_resp.text)
            soup = BeautifulSoup(am_QueryAccount_resp.text,'html.parser')
            try:
                MYZD = soup.find('span',{"id": "MYZD"}).text
                MYZD = MYZD.replace('日','')
                creditCardObj["billDay"] = MYZD
            except:
                respText = str(am_QueryAccount_resp.text) + "_" + traceback.format_exc()
                #Bank.uploadException(self,self.login_account,'billDay exception',respText)
            
            am_QueryReckoningNotRMBClientNo = Bank.applyToken_ChangeClientNo(self, 'CBANK_CREDITCARD_LOAN' , 'query')
            print(am_QueryReckoningNotRMBClientNo)
            if(am_QueryReckoningNotRMBClientNo != None):
                Bank.uploadException(self,self.login_account,'getCreditCard Data', 'start_to_get_credit_card_data')
                if(am_QueryReckoningNotRMBClientNo == 0):
                    am_QueryReckoningNotRMBClientNo = self.ClientNo
                
                
                unsettledBill = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Loan/UI/CreditCard/Loan/Pro8/am_QueryReckoningNotRMB.aspx'
                unSetteledHeader = {
                    'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/msword, */*',
                    'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Loan/UI/CreditCard/Loan/am_QueryReckoningSurveyNew.aspx',
                    'Accept-Language': 'zh-CN',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept-Encoding': 'gzip, deflate',
                    'Host': 'pbsz.ebank.cmbchina.com',
                    'Content-Length': '73',
                    'Connection': 'Keep-Alive',
                    'Cookie': self.Cookie
                    }
                unsettledBillData = 'ClientNo=' + am_QueryReckoningNotRMBClientNo + '&index=2'
                unsettledBill_resp = self.session.post(unsettledBill, headers = unSetteledHeader, data = unsettledBillData,verify = False)
    #             print(unsettledBill_resp.text)
                unsettledBill_soup = BeautifulSoup(unsettledBill_resp.text,'html.parser')
                
                
                historyBillData = 'ClientNo=' + am_QueryReckoningNotRMBClientNo
                historyBill = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Loan/UI/CreditCard/Loan/am_QueryReckoningSurveyNew.aspx'
                historyBill_resp = self.session.post(historyBill, headers = am_QueryAccount_header, data = historyBillData,verify = False)
    #             print(historyBill_resp.text)
                historyBill_soup = BeautifulSoup(historyBill_resp.text,'html.parser')
                
                
                userInfor = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Account/UI/CreditCard/Account/cs_QueryCustomerInfo.aspx'
                userInfor_resp = self.session.post(userInfor, headers = am_QueryAccount_header, data = am_QueryAccount_data,verify = False)
    #             print(userInfor_resp.text)
                userInfor_soup = BeautifulSoup(userInfor_resp.text,'html.parser')
                
                CheckBill = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Account/UI/CreditCard/Account/am_CheckBillQuery.aspx'
                checkBillHeader = {
                        'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/msword, */*',
                        'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                        'Accept-Language': 'zh-CN',
                        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept-Encoding': 'gzip, deflate',
                        'Host': 'pbsz.ebank.cmbchina.com',
                        'Content-Length': '65',
                        'Connection': 'Keep-Alive',
                        'Cache-Control': 'no-cache',
                        'Cookie': self.Cookie
                    }
                CheckBill_data = 'ClientNo=' + am_QueryAccountClientNo
                CheckBill_resp = self.session.post(CheckBill, headers = checkBillHeader, data = CheckBill_data,verify = False)
    #             print(CheckBill_resp.text)
                historyBillDetail = []
                for i in range(0, 12):
                    time.sleep(0.5)
                    prevMonth = -(i)
                    
                    #print((datetime.date.today() + datetime.timedelta((prevMonth)*365/12)))
                    prevM = (datetime.date.today() + datetime.timedelta((prevMonth)*365/12)).strftime("%m")
                    prevY = (datetime.date.today() + datetime.timedelta((prevMonth)*365/12)).strftime("%Y")
                    endD = calendar.monthrange(int(prevY),int(prevM))[1]
                    monthStr = prevY + "" +  prevM + "" + str(endD)
                    print('--------- '+ str(monthStr) +' ---------')
                    
                    CheckBillDetail = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Account/UI/CreditCard/Account/am_CheckBillQuery.aspx'
                    checkBillHeader = {
                            'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/msword, */*',
                            'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Account/UI/CreditCard/Account/am_CheckBillQuery.aspx',
                            'Accept-Language': 'zh-CN',
                            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Accept-Encoding': 'gzip, deflate',
                            'Host': 'pbsz.ebank.cmbchina.com',
                            'Content-Length': '65',
                            'Connection': 'Keep-Alive',
                            'Cache-Control': 'no-cache',
                            'Cookie': self.Cookie
                        }
                    CheckBillDetail_data = 'ClientNo=' + am_QueryAccountClientNo + '&Currency=RMB&QueryYearMonth='+ str(monthStr) +'&index=0'
                    CheckBill_detail_resp = self.session.post(CheckBillDetail, headers = checkBillHeader, data = CheckBillDetail_data,verify = False)
    #                 print(CheckBill_detail_resp.text)
                    CheckBill_detail_str = str(CheckBill_detail_resp.text)
                    CheckBill_detail_soup = BeautifulSoup(CheckBill_detail_resp.text,'html.parser')
                    
                    dgMainTable = CheckBill_detail_soup.find('table',{"id": "dgBill"})
    #                 print(dgMainTable)
    
                    try:
                        if(dgMainTable != None):
                            trs = dgMainTable.findAll('tr')
                            i = 0 
                            
                            for tr in trs:
                                if( i != 0 ):
                                    trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                                    td = trTD.findAll('td')
        #                             if(i == 1):
        #                                 Bank.uploadException(self,self.login_account,'historyBillDetail td', str(td))
                                    tranDate = td[1].text
                                    bookedDate = td[2].text
                                    tranSummary = td[3].text
                                    cardNum = td[4].text
                                    tranAmt = td[5].text
                                    
                                    tranAmt = tranAmt.replace('￥', '')
                                    tranAmt = tranAmt.replace(' ', '')
                                    tranAmt = tranAmt.replace(',', '')
                                    tranAmt = tranAmt.replace('.', '')
                                    
                                    if( '-' in  td[5].text):
                                        payMoney = '0'
                                        incomeMoney = tranAmt
                                        incomeMoney = incomeMoney.replace('-', '')
                                    else:
                                        payMoney = tranAmt
                                        incomeMoney = '0'
                                    
                                    bookedDate = bookedDate.replace('-', '')
                                    tranDate = tranDate.replace('-', '')
                                    
                                    historyBillsDetailObj = {}
                                    historyBillsDetailObj['tranDate'] = tranDate
                                    historyBillsDetailObj['bookedDate'] = bookedDate
                                    historyBillsDetailObj['tranSummary'] = tranSummary
                                    historyBillsDetailObj['cardNum'] = cardNum
                                    historyBillsDetailObj['incomeMoney'] = incomeMoney
                                    historyBillsDetailObj['payMoney'] = payMoney
                                    historyBillsDetailObj['tranPlace'] = ""
                                    historyBillDetail.append(historyBillsDetailObj)
                                    
                                i =  i + 1
                        else:
                            Bank.uploadException(self,self.login_account,'historyBillDetail else:',CheckBill_detail_str)
                    except:
                        respText = traceback.format_exc()
                        Bank.uploadException(self,self.login_account,'historyBillDetail except:',respText)
                    searchstr = 'dataArray= "'
                    endStr = '";'
                    start = CheckBill_detail_str.find(searchstr)
                    end = CheckBill_detail_str.find( endStr , start)
                    dataArray = CheckBill_detail_str[start + len( searchstr ) : end]
    #                 print(dataArray)
                    print('-----******* ---------')
                
                
                creditCardObj['historyBillDetail'] = historyBillDetail
                credit_limit_RMBXYED = soup.find('span',{"id": "RMBXYED"}).text
                available_credit_RMBXYED = soup.find('span',{"id": "RMBKYED"}).text
                cashLimit_RMBYJXJ = soup.find('span',{"id": "RMBYJXJ"}).text
                Outstanding_principal_RMBWCZFQ = soup.find('span',{"id": "RMBWCZFQ"}).text
                dueDate_DQHQ = soup.find('span',{"id": "DQHQ"}).text
                
                credit_limit_RMBXYED = credit_limit_RMBXYED.replace('￥', '')
                credit_limit_RMBXYED = credit_limit_RMBXYED.replace(' ', '')
                credit_limit_RMBXYED = credit_limit_RMBXYED.replace(',', '')
                credit_limit_RMBXYED = credit_limit_RMBXYED.replace('.', '')
                
                available_credit_RMBXYED = available_credit_RMBXYED.replace('￥', '')
                available_credit_RMBXYED = available_credit_RMBXYED.replace(' ', '')
                available_credit_RMBXYED = available_credit_RMBXYED.replace(',', '')
                available_credit_RMBXYED = available_credit_RMBXYED.replace('.', '')
                
                cashLimit_RMBYJXJ = cashLimit_RMBYJXJ.replace('￥', '')
                cashLimit_RMBYJXJ = cashLimit_RMBYJXJ.replace(' ', '')
                cashLimit_RMBYJXJ = cashLimit_RMBYJXJ.replace(',', '')
                cashLimit_RMBYJXJ = cashLimit_RMBYJXJ.replace('.', '')
                
                dueDate_DQHQ = dueDate_DQHQ.replace('-', '')
                
                creditCardObj['creditLimit'] = credit_limit_RMBXYED
                creditCardObj['availableLimit'] = available_credit_RMBXYED
                creditCardObj['cashLimit'] = cashLimit_RMBYJXJ
                creditCardObj['dueDate'] = dueDate_DQHQ
                
                
                lMobileNo = userInfor_soup.find('span',{"id": "lMobileNo"}).text
                lEmailIndi = userInfor_soup.find('span',{"id": "lEmailIndi"}).text
                lOfficePhone = userInfor_soup.find('span',{"id": "lOfficePhone"}).text
                lHomePhone = userInfor_soup.find('span',{"id": "lHomePhone"}).text
                billAddr = userInfor_soup.find('span',{"id": "lCurAddr"}).text
                homeAddr =  userInfor_soup.find('span',{"id": "lHomeAddr"}).text
                companyAddr =  userInfor_soup.find('span',{"id": "lWorkAddr"}).text
                houseAddr =  userInfor_soup.find('span',{"id": "lTAddr"}).text
                billType =  userInfor_soup.find('span',{"id": "lStmtDeliMtd"}).text
                companyName =  userInfor_soup.find('span',{"id": "LbCoprName"}).text
                
                
                creditCardObj['mobile'] = lMobileNo
                creditCardObj['email'] = lEmailIndi
                creditCardObj['homeTel'] = lHomePhone
                creditCardObj['houseAddr'] = houseAddr
                creditCardObj['homeAddr'] = homeAddr
                creditCardObj['companyTel'] = lOfficePhone
                creditCardObj['companyName'] = companyName
                creditCardObj['companyAddr'] = companyAddr
                creditCardObj['billAddr'] = billAddr
                creditCardObj['billType'] = billType
                
                
                dgReckoningInfo1 = historyBill_soup.find('table',{"id": "dgReckoningInfo1"})
                trs = dgReckoningInfo1.findAll('tr')
                i = 0 
                historyBills = []
                for tr in trs:
                    if( i != 0 ):
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        billDate = td[0].text
                        totalCost = td[1].text
                        minPaymentAmt = td[2].text
                        
                        totalCost = totalCost.replace('￥', '')
                        totalCost = totalCost.replace(' ', '')
                        totalCost = totalCost.replace(',', '')
                        #totalCost = totalCost.replace('.', '')
                        totalCost = str(int(float(totalCost) * 100)) 
                        
                        minPaymentAmt = minPaymentAmt.replace('￥', '')
                        minPaymentAmt = minPaymentAmt.replace(' ', '')
                        minPaymentAmt = minPaymentAmt.replace(',', '')
                        #minPaymentAmt = minPaymentAmt.replace('.', '')
                        minPaymentAmt = str(int(float(minPaymentAmt) * 100)) 
                        
                        billDate = billDate.replace('-', '')
                        
                        historyBillsObj = {}
                        historyBillsObj['billDate'] = billDate
                        historyBillsObj['totalCost'] = totalCost
                        historyBillsObj['minPaymentAmt'] = minPaymentAmt
                        historyBills.append(historyBillsObj)
                        
                    i =  i + 1
                
                creditCardObj['historyBills'] = historyBills
                
                
                dgReckoningNotDetail = unsettledBill_soup.find('table',{"id": "dgReckoningNotDetail"})
                trs = dgReckoningNotDetail.findAll('tr')
                i = 0 
                unsettledBills = []
                print("Unsettled")
                for tr in trs:
    #                 print(tr)
                    if( i != 0 ):
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        if(i == 1):
                            Bank.uploadException(self,self.login_account,'unsettledBills td', str(td))
                        
                        bookedDate = td[0].text
                        tranSummary = td[2].text
                        tranAmt = td[5].text
                        cardNum = td[4].text
                        tranDate = td[1].find('span').text
                        unsettledBillsObj = {}
                        
                        tranAmt = tranAmt.replace('￥', '')
                        tranAmt = tranAmt.replace(' ', '')
                        tranAmt = tranAmt.replace(',', '')
                        tranAmt = tranAmt.replace('.', '')
                        
                        if( '-' in  td[5].text):
                            payMoney = '0'
                            incomeMoney = tranAmt
                            incomeMoney = incomeMoney.replace('-', '')
                        else:
                            payMoney = tranAmt
                            incomeMoney = '0'
                        
                        bookedDate = bookedDate.replace('-', '')
                        tranDate = tranDate.replace('-', '')
                        tranDate = tranDate.replace(' ', '')
                        tranDate = tranDate.replace('\r', '')
                        tranDate = tranDate.replace('\n', '')
                        
                        unsettledBillsObj['bookedDate'] = bookedDate
                        unsettledBillsObj['tranSummary'] = tranSummary
                        unsettledBillsObj['payMoney'] = payMoney
                        unsettledBillsObj['incomeMoney'] = incomeMoney
                        unsettledBillsObj['tranDate'] = tranDate
                        unsettledBillsObj['cardNum'] = cardNum
                        unsettledBillsObj['tranPlace'] = ""
                        unsettledBills.append(unsettledBillsObj)
                        
                    i =  i + 1
                    
                creditCardObj['unsettledBillDetail'] = unsettledBills    
                print("bill Detail")
                
                
                CBANK_CREDITCARD_CUSTOMERClientNo = Bank.applyToken_ChangeClientNo(self, 'CBANK_CREDITCARD_CUSTOMER' , '')
                print(CBANK_CREDITCARD_CUSTOMERClientNo)
                if(CBANK_CREDITCARD_CUSTOMERClientNo == 0):
                    CBANK_CREDITCARD_CUSTOMERClientNo = self.ClientNo
                    
                cardInfoUrl = 'https://pbsz.ebank.cmbchina.com/CmbBank_CreditCard_Customer/UI/CreditCard/Customer/cm_QueryCustomInfo.aspx'
                cardInfoHeader = {
                        'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/msword, */*',
                        'Referer': 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenIndex.aspx',
                        'Accept-Language': 'zh-CN',
                        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.2)',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept-Encoding': 'gzip, deflate',
                        'Host': 'pbsz.ebank.cmbchina.com',
                        'Content-Length': '65',
                        'Connection': 'Keep-Alive',
                        'Cookie': self.Cookie
                    }
                cardInfo_data = 'ClientNo=' + CBANK_CREDITCARD_CUSTOMERClientNo
                cardInfo_resp = self.session.post(cardInfoUrl, headers = cardInfoHeader, data = cardInfo_data, verify = False)
    #             print(cardInfo_resp.text)
                
                
                cardInfo_soup = BeautifulSoup(cardInfo_resp.text,'html.parser')
                
                dgMainTable = cardInfo_soup.find('table',{"id": "ucCmQueryCustomInfo0_dgReckoningSet"})
    #                 print(dgMainTable)
                
                trs = dgMainTable.findAll('tr')
                i = 0 
                cardsInfo = []
                for tr in trs:
                    if( i != 0 ):
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        cardsInfoObj = {}
                        cardNo = td[0].text
                        cardType = td[1].text
                        cardAliasName = td[2].text
                        ownerName = td[3].text
                        openFlag = td[4].text
                        cardsInfoObj['cardNo'] = cardNo
                        cardsInfoObj['cardType'] = cardType
                        cardsInfoObj['cardAliasName'] = cardAliasName
                        cardsInfoObj['ownerName'] = ownerName
                        cardsInfoObj['openFlag'] = openFlag
                        
                        cardsInfo.append(cardsInfoObj)
                        
                    i = i + 1
                
                creditCardObj['cardsInfo'] = cardsInfo    
                creditCardInfos.append(creditCardObj)
                self.account_info['creditCardInfos'] = creditCardInfos
                self.haveCreditData = True
                Bank.uploadException(self,self.login_account,'creditCardInfos', str(self.account_info['creditCardInfos']))
    #             print(creditCardObj)
            
            return returnData
        
        except Exception:
            self.haveCreditData = False
            respTxt = traceback.format_exc()
            #print(respTxt)
            Bank.uploadException(self,self.login_account,'getCreditDatas',respTxt)
            returnData = {
                        'status':'false',
                        'again':'true',
                        'step':'0',
                        'msg':'请求失败,请重新操作,Code:Creditdata',
                        'success1': False,
                        'words':[
                                    {'ID':'AccountNo','index': 0,'needUserInput':'true', 'label':'账号', 'type': 'text'},
                                    {'ID':'Password','index': 1,'needUserInput':'true', 'label':'网银登录密码', 'type': 'password'}
                                ]
                    }
            return returnData

    def uploadData(self, data):
        #上传数据到服务器
        #print(data)
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
            print('uploadData-->[post] cmb data to ' + self.crawlerServiceUrl)
            resp = requests.post(self.crawlerServiceUrl, headers = headers, data = {'content':json.dumps(postData, ensure_ascii=False)})
            respText = resp.text;
            #print(resp.text)
            respObj = json.loads(str(resp.text).strip(), encoding = 'utf-8')
            if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
                return True
            else:
                Bank.uploadException(self, username=data['login_account'], step='uploadData', errmsg=respText)
                return False
        except Exception:
            print('uploadData-->[post] cmb data error, ' + self.crawlerServiceUrl)
            respText = traceback.format_exc()
            Bank.uploadException(self, username=data['login_account'], step='5', errmsg=respText)
            return False

    def uploadException(self, username = '', step = '', errmsg = ''):
        #上传异常信息
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'cmb','login_account':username}
        try:
            requests.post(self.uploadExceptionUrl, headers = headers, data = {'content':json.dumps(data, ensure_ascii=False)})
        except:
            print('uploadException-->[post] exception error')

    def sendSmsCode(self):
        
        try:
            url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenLoginVerifyM2.aspx'
            headers = {
                    'Host' : 'pbsz.ebank.cmbchina.com',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cookie':self.Cookie,
                    'Content-Type':"application/x-www-form-urlencoded"
            }
            post_data = 'ClientNo='+self.ClientNo

            resp = self.session.post(url, headers = headers, data = post_data, verify=False, timeout = None)
    
            time.sleep(1)
            
            url = 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/GenLoginVerifyM2.aspx'
            headers = {
                    'Host' : 'pbsz.ebank.cmbchina.com',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cookie':self.Cookie,
                    'Content-Type':"application/x-www-form-urlencoded"
                }
            post_data = 'PRID=SendMSGCode&ClientNo='+self.ClientNo
            resp = self.session.post(url, headers = headers, data = post_data, verify=False, timeout = None)
            soup = BeautifulSoup(resp.content,"html.parser")
            fs = soup.find_all('code')

            #返回码为00则表示验证码匹配
            resultCode = fs[0].get_text()
            #print(resultCode)
            return resultCode      
        except:
            print('sendSmsCode-->[post] cmb data error, ' + url)
            #isSuccess = False
            return '01'
        

    def logout(self):
        url = 'https://pbsz.ebank.cmbchina.com/CmbBank_HomePage/UI/HomePagePC/Login/Logout.aspx'
        headers = {
                'Host' : 'pbsz.ebank.cmbchina.com',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Referer' : 'https://pbsz.ebank.cmbchina.com/CmbBank_GenShell/UI/GenShellPC/Login/Login.aspx',
                'Upgrade-Insecure-Requests': '1',
                'Cookie':self.Cookie,
                'Content-Type':"application/x-www-form-urlencoded",
                'Connection': 'keep-alive'
            }
        post_data = 'ClientNo='+self.ClientNo
        resp = self.session.post(url, headers = headers, data = post_data, verify=False)   


    def jiamiData(self,ClientNo,login_account,login_password):
        #密码加密
        jiamiUrl = self.jiamiUrl
        jiamiUrl_headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        
        jiamiUrl_resp = ''
        nCount = 1
        nNum = 3
        op = False
        while (nCount > 0 and nNum > 0):
            try:
                jiamiUrl_resp = requests.get(self.jiamiUrl+'?content={"bankCode":"CMB","params":"%s","account":"%s","password":"%s"}'%(ClientNo,login_account,login_password),timeout = None)

                jiamiObj = jiamiUrl_resp.json()
                self.AccountNo = jiamiObj['AccountNo']
                self.Password = jiamiObj['Password']
                self.HardStamp = jiamiObj['HardStamp']
                self.Licex = jiamiObj['Licex']
                 
                nCount = 0
                op = True
            except:
                respText = 'jiamiData except:'+login_account+' | '+login_password+'  '+traceback.format_exc()+jiamiUrl_resp.text
                Bank.uploadException(self,self.login_account,'jiamiData',respText)
    
                nCount = 1
                nNum = nNum - 1
                op = False
                
            time.sleep(0.5)
        return op

