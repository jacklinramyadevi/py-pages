# -*- coding: utf-8 -*-
'''
@author: Jacklin
@Province: Hebei
'''
import json
import requests
from bs4 import BeautifulSoup, Comment
import base64
import datetime
import time
import traceback
from builtins import str
from urllib import parse
import re

class CTCC() :

    '''中国电信爬虫-河北省
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
        #self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
#         self.jiamiUrl = 'http://192.168.1.82:8081/creditcrawler/bank/getEncryptParams'
        self.jiamiUrl = 'http://api.telecom.yuancredit.com/JsEncrypt'
        #self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        
        #防止重复初始化覆盖新值
        if not hasattr(self, 'crawlerServiceUrl'):
            self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        if not hasattr(self, 'uploadExceptionUrl'):
            self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        
        if params :
            self.initCfg(self, params)  
        self.param = {
            'username':'',
            'password':''
        }
        try:
            self.session = requests.session()
            self.login_account = ''
            returnData = {
                'status':'true',
                'again':'true',
                'step':'0',
                'msg':'',
                'words':[

                    {'ID':'username','index': 0,'needUserInput':'true', 'label':'手机号码', 'type': 'text'},
                    {'ID':'password','index': 1,'needUserInput':'true', 'label':'服务密码', 'type': 'password'}
                ]
            }
        except Exception :
            respText = traceback.format_exc()
            CTCC.uploadException(self , username = '' , step = 'init' , errmsg = respText)
            returnData = {
                'status' : 'false',
                'again' : 'true',
                'msg' : '初始化失败,请重试,code:1'
            }
        return returnData

    
    def doCapture(self, jsonParams):
        try:
            return CTCC.doCapture1(self,jsonParams)
        except:
            respText = 'Code_000 except:'+traceback.format_exc()
            #print(respText)
            CTCC.uploadException(self, self.login_account, 'doCapture', respText)
            result = {
                'status':'true',
                'again':'true',
                'step':'0',
                'msg':'需要初始化',
                'words':[
                            {'ID':'mobile','index': 0,'needUserInput':'true', 'label':'手机号码', 'type': 'text'},
                            {'ID':'password','index': 1,'needUserInput':'true', 'label':'服务密码', 'type': 'password'}
                        ]
            }
            return json.dumps(result)
    
    
    def doCapture1(self, jsonParams):
        
        try:
            data = {}
            #print(jsonParams)
            #json.dumps(jsonParam)
            #
            jsonParams = json.loads(jsonParams, encoding='utf-8')
            self.jsonParams = jsonParams
            
            if 'step' in jsonParams.keys():
                self.step = jsonParams["step"]
            else:
                self.step = str(jsonParams["result"]["step"])
                obj = {"result":jsonParams["result"]}
                '''jsonParams["username"] = jsonParams["result"]["username"]
                jsonParams["password"] = jsonParams["result"]["password"]'''
            
            setrandomFlag = "0"
            if 'setrandomFlag' in jsonParams.keys():
                setrandomFlag = jsonParams["setrandomFlag"]
            elif 'result' in jsonParams.keys():
                if 'setrandomFlag' in jsonParams["result"].keys():
                    setrandomFlag = str(jsonParams["result"]["setrandomFlag"])
            #self.flowNo = str(self.jsonParams['flowNo'])
            if(self.step == "0"):
                #if()
                if setrandomFlag == "1":
                    self.randomFlag = "1"
                else:
                    self.randomFlag = "0"
                self.jsonParams = jsonParams
                
                if 'flowNo' in jsonParams.keys():
                    self.flowNo = jsonParams['flowNo']
                else:
                    self.flowNo = str(jsonParams["result"]["flowNo"])
                obj = {}
                obj["result"] = {}
                obj = {
                        "result" : {
                            'status':'true',
                            'again':'true',
                            'step':'0',
                            'username':'',
                            'password':'',
                            'gostep':''
                        }
                      }
                if 'username' in jsonParams.keys() and 'password' in jsonParams.keys():
                    obj["result"]["username"] = jsonParams["username"]
                    obj["result"]["password"] = jsonParams["password"]
                    
                self.result_info = {}
                self.result_info['ispName'] = '电信'
                self.result_info['ispCode'] = 'CTCC'
                self.result_info['ispProvince'] = '河北'
                self.result_info['phoneNum'] = obj["result"]["username"]#self.login_account
                
                self.result_info['flow_no'] = self.flowNo
                self.result_info['createTime'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                
                self.mobile = obj["result"]["username"]
                self.UserId  = obj["result"]["username"]
                self.login_account = obj["result"]["username"]
                self.login_password = obj["result"]["password"]
                self.result_info["billDetail"] = []
                self.result_info["paymentRecord"] = []
                CTCC.uploadException(self, self.mobile, 'docapture1_password', 'init_' + str(self.login_password))
                data = CTCC.checkLogin(self, obj)
                return data
            elif(self.step == "2"):
                obj = {
                        "result" : {
                            'status':'true',
                            'again':'true',
                            'step':self.step,
                            'username':self.login_account,
                            'password':self.login_password,
                            'gostep':''
                        }
                      }
                if 'piccode' in jsonParams.keys():
                    piccode = str(jsonParams["piccode"])
                elif 'piccode' in jsonParams["result"].keys():
                    piccode = str(jsonParams["result"]["piccode"])
                self.piccode = piccode 
                data = CTCC.checkLogin(self, obj)     
                return data  
            
            elif(self.step == "1"):
                obj = {
                        "result" : {
                            'status':'true',
                            'again':'true',
                            'step':self.step,
                            'username':self.login_account,
                            'password':self.login_password,
                            'gostep':'1'
                        }
                      }
                if 'smsPwd' in jsonParams.keys():
                    smsPwd = str(jsonParams["smsPwd"])
                elif 'smsPwd' in jsonParams["result"].keys():
                    smsPwd = str(jsonParams["result"]["smsPwd"])
                
#                 if 'idNum' in jsonParams.keys():
#                     idNum = str(jsonParams["idNum"])
#                 elif 'idNum' in jsonParams["result"].keys():
#                     idNum = str(jsonParams["result"]["idNum"])    
                
                self.mobilecode = smsPwd.strip()
#                 self.CustIdNum = idNum.strip()
                data = CTCC.checkLogin(self, obj)
                return data
            
            return data
        except Exception :
            CTCC.uploadException( self, username = self.login_account, step = 'doCapture', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
#             print(traceback.format_exc())
            return returnData

    #上传数据到服务器
    def uploadData(self, data):
        #print(data)
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        try:
            postData = {
                'heade':{'code':'uploadIspData','token':'','timestamp':''},
                'body':{
                    'attach':'',
                    'content':data
                }
            }
#             print('uploadData-->[post] ctcc_hn data to ' + self.crawlerServiceUrl)
            resp = requests.post(self.crawlerServiceUrl, headers = headers, data = {'content':json.dumps(postData, ensure_ascii=False)})
            respText = resp.text;
            #print(resp.text)
            respObj = json.loads(str(resp.text).strip(), encoding = 'utf-8')
#             print(respObj.keys())
#             print(str(respObj['success']))
            if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
                return True
            else:
                CTCC.uploadException(self, username= self.login_account, step='uploadData', errmsg="upload return False"+respText)
                return False
#            if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
#                return True
#            else:
#                CTCC.uploadException(self, username=data['login_account'], step='2', errmsg=respText)
#                return False
        except Exception:
#             print('uploadData-->[post] ctcc_hn data error, ' + self.crawlerServiceUrl)
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=self.login_account, step='uploadData', errmsg=respText)
            return False
   
        
        #鍒濆鍖杝ession
        
    def uploadException(self, username = '', step = '', errmsg = ''):
        #上传异常信息
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'ctcc_heb','login_account':username}
        try:
            if '192.168.1.82' not in self.uploadExceptionUrl:
                requests.post(self.uploadExceptionUrl, headers = headers, data = {'content':json.dumps(data, ensure_ascii=False)})
        except:
            print('uploadException-->[post] exception error')

       
    def passwordEncryption(self, username, password):
        
        jiamiUrl_headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
        }
        
        jiamiUrl_params = {
            'ctrlType':'CTCC',
            'loginInfo': username,
            'password': password,
            'loginInfo': self.loginInfo
        }
        resp = self.session.post(self.jiamiUrl, headers = jiamiUrl_headers, data = {'content':json.dumps(jiamiUrl_params,ensure_ascii=False)}, allow_redirects = True)
        jiamiObj = json.loads(resp.text, encoding = 'utf-8')
        #print('jiamiObj=',jiamiObj,'\n')
        
        try:
            self.param['password'] = jiamiObj['password']
            self.logInfo = jiamiObj['loginInfo']
           
        except Exception:
            respText =  traceback.format_exc()
            CTCC.uploadException(self, username = username, step='passwordencryption', errmsg=respText)
            data = {
                    'status':'true',
                    'step':'0',
                    'msg':'加密服务错误，请退出重试',
                    'words':[
                                {'ID':'username','index': '0',  'label':'用户名', 'type': 'text'},
                                {'ID':'password','index': '1', 'label':'服务密码', 'type': 'password'}
                            ]
                }
        return self.param
            
    

    
    def checkLogin(self, obj):
        try:
            if(obj['result']['step'] == "0"):
                
                userInfo = {}
                phoneInfo = {}
                self.result_info['operator'] = '山东电信'
                self.result_info['phone_no'] = self.login_account
                self.result_info['userInfo'] = userInfo
                self.result_info['phoneInfo'] = phoneInfo
    #             self.result_info['historyBillInf'] = []
                
                resultObj = {
                        "step": "0",
                        "gostep":"",
                        "username": str(obj["result"]["username"]),
                        "password": str(obj["result"]["password"])
                    }
                
            
                if CTCC.getLoginCookies(self, obj) == False:
                    resultObj['step'] = '2'
                    resultObj['gostep'] = 'verifyCode'
                    
                    returnData = {
                            'status' : 'true',
                            'step' : '2',
                            'again' : 'true',
                            'msg': "",
                            'username': self.login_account,
                            'words': []
                        }
                    if(self.imgbyteBase64Str != None):
                        returnData['words'] = [
                                {'ID' : 'piccode' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '请输入四位黑色验证码' , 'type' : 'piccode' , 'source' : self.imgbyteBase64Str }
                            ] 
                    return returnData
            elif (self.step == "2"):
                self.randomFlag = "0"
                self.step = '0'
                obj['result']['gostep'] = 'logined'
                encry_obj = CTCC.passwordEncryption(self, str(self.login_account), str(obj["result"]["password"]))
                obj['result']['password'] = encry_obj["password"]
                self.encry_password = encry_obj["password"]
                loginData = CTCC.doLogin(self, obj, '0', self.piccode)
                obj['result']['gostep'] = 'logined'
            elif (self.step == "1"):
                loginData = {}
                resData = CTCC.checkSMSCode(self)
                if( resData["success1"] == 'true' and resData["status"] == 'true' ):
                    data = CTCC.getPhoneList(self)
                    if( data["success1"] == 'true' ):
                        data = CTCC.getPaymentRecord(self)
                        
                        if data["success1"] == 'true':
                            #data = CTCC.getUSERINFO(self)
                            if data["success1"] == 'true':
                                return CTCC.doUpload(self)
                            else:
                                return data
                        else:
                            return data
                    else:
                        return data
                elif(resData["success1"] == 'true' and resData["status"] == 'false' ):
                    
                    data = CTCC.getSMSCode(self)
                    if data["success1"] == 'true':
                        data = {
                            'status' : 'true',
                            'step' : '1',
                            'gostep': '',
                            'again' : 'true',
                            'msg': '',
                            'username': self.login_account,
                            'words' : [
#                                     {'ID' : 'idNum' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '证件号码' , 'type' : 'idNum'},
                                    {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                                    
                                ]
                        }
                        return data
                    else:
                        return CTCC.doUpload(self)
                else:
                    CTCC.uploadException( self, username = self.login_account, step = 'checkVerifyCodeSendSMSfail', errmsg = "sms code failed" )
                    resultObj = CTCC.init(self)
                    resultObj = json.loads(json.dumps(resultObj), encoding = 'utf-8')
                    resultObj['msg'] = resData["msg"]
                    return resultObj
                
            
                
            if obj['result']['gostep'] == '' and self.step == "0":
                if obj['result']['password'] == '':
                    smsobj = CTCC.doRandomPasswordLogin(self, obj)
                    if(smsobj['result'] == "True"):
                        #obj['result']['password'] = raw_input("please enter code: ")
                        ''''''
                        data = {
                            'status' : 'true',
                            'step' : '1',
                            'gostep': '',
                            'again' : 'true',
                            'msg': '请输入短信验证码',
                            'username': self.login_account,
                            'words' : [
                                    {'ID' : 'randomPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                                ]
                        }
                        resultObj['step'] = '1'
                        resultObj['gostep'] = smsobj['msg']
                        return data
                        
                    else:
                            resultObj = CTCC.init(self)
                            resultObj = json.loads(json.dumps(resultObj), encoding = 'utf-8')
                            resultObj['msg'] = smsobj['msg']
                            return resultObj
                else:  
                    encry_obj = CTCC.passwordEncryption(self, str(self.login_account), str(obj["result"]["password"]))
                    obj['result']['password'] = encry_obj["password"]
                    self.encry_password = encry_obj["password"]
                    loginData = CTCC.doLogin(self, obj, '0', '')
                
            
            if(self.step == "0" and loginData["result"] == "True" ):
                print("logined")
                data = CTCC.goFrontPage(self)#
                #print(data["success1"])
                
                if data["success1"] == 'true':
                    if( data['msg'] == 'goLogin'):
                        data = CTCC.getLoginAgain(self)
                    if data["success1"] == 'true' or data['msg'] == 'getsms':
                        data = CTCC.getSMSCode(self)
                        if data["success1"] == 'true':
                            data = {
                                'status' : 'true',
                                'step' : '1',
                                'gostep': '',
                                'again' : 'true',
                                'msg': '',
                                'username': self.login_account,
                                'words' : [
    #                                     {'ID' : 'idNum' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '证件号码' , 'type' : 'idNum'},
                                        {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                                        
                                    ]
                            }
                            return data
                        else:
                            return data
                    else:
                        return data
                else:
                    return data
                
                
            elif(self.step == "0" and loginData["result"] == "False"):
                returnData = CTCC.init( self )
                returnData = json.loads(json.dumps(returnData), encoding = 'utf-8')
                returnData["msg"] = loginData["msg"]
                return returnData
        except Exception:
            respText =  traceback.format_exc()
            #print(respText)
            CTCC.uploadException(self, username = self.UserId, step='checklogin', errmsg=respText)
        
            
            
    def getLoginCookies(self, obj):
        try:
        #Login for Get ECSLoginReq Cookie
            headerStr = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Content-Type':'application/x-www-form-urlencoded',
                'Host':'login.189.cn',
                'Origin':'http://login.189.cn',
                'Referer':'http://login.189.cn/login',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent' : 'python-requests/2.12.3',
                'Proxy-Connection':'keep-alive'
                #'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            }
            
            url = 'http://login.189.cn/login' 
            getECSLoginresp = self.session.get(url, headers = headerStr, verify = False, allow_redirects = True) 
            ##time.sleep(10)
            #for get ProvinceID
            ajaxUrl = 'http://login.189.cn/login/ajax'
            ajax_post_data = {
                    'm': 'checkphone',
                    'phone': str(self.login_account)
                }
            ajaxHeaderStr = {
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'30',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Host':'login.189.cn',
                'Origin':'http://login.189.cn',
                'Referer':'http://login.189.cn/login',
                'User-Agent' : 'python-requests/2.12.3',
                #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest',
                'Proxy-Connection':'keep-alive'
                }
            getProvinceresp = self.session.post(ajaxUrl, data = ajax_post_data, headers = ajaxHeaderStr, verify = False, allow_redirects = True) 
            self.ProvinceID = json.loads(getProvinceresp.text)["provinceId"]
            self.AreaCode = json.loads(getProvinceresp.text)["areaCode"]
            
            self.loginInfo = self.mobile +'$$201$地市 （中文/拼音） $'+ self.ProvinceID +'$$$0'
            
            #13315923020$$201$地市（中文/拼音）$05$$$0"
            ##time.sleep(10)
            ajaxUrl2 = 'http://login.189.cn/login/ajax'
            ajax_post_data2 = {
                'Account': str(self.login_account),
                'AreaCode': '',
                'CityNo': '',
                'ProvinceID': self.ProvinceID,
                'UType': '201',
                'm': 'captcha'
                 }
            ajaxHeaderStr2 = {
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'30',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Host':'login.189.cn',
                'Origin':'http://login.189.cn',
                'Referer':'http://login.189.cn/login',
                'User-Agent' : 'python-requests/2.12.3',
                #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest',
                'Proxy-Connection':'keep-alive'
                }
            
            getAJAXresp2 = self.session.post(ajaxUrl2, data = ajax_post_data2, headers = ajaxHeaderStr2, verify = False, allow_redirects = True) 
            
            #print(getAJAXresp2.text)
            jsonRes = json.loads(getAJAXresp2.text, encoding = 'utf-8')
            self.imgbyteBase64Str = None
            #print(getAJAXresp2.text)
            jsonRes = json.loads(getAJAXresp2.text, encoding = 'utf-8')
            if(str(jsonRes["captchaFlag"]).lower() == "true"):
                self.imgbyteBase64Str = CTCC.getVerifyCode(self)
                return False
                
                
            return True
        except Exception:
            #print(traceback.format_exc() )
            CTCC.uploadException( self, username = self.login_account, step = 'getLoginCookies', errmsg = traceback.format_exc() )
            return False
        
    def getVerifyCode(self):
        try:
            verifyCodeUrl = 'http://login.189.cn/captcha?8ad658a301ca4b068c85ef842155b9df&source=login&width=100&height=37&0.1887850539333522'
            verifyCodeHeader = {
                    'Accept':'image/webp,image/*,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'login.189.cn',
                    'Referer':'http://login.189.cn/login',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            getVerifyCoderesp = self.session.get(verifyCodeUrl, headers = verifyCodeHeader, verify = True, allow_redirects = True, timeout = None)
            imgbyteBase64Str = base64.b64encode(getVerifyCoderesp.content).decode(encoding = 'utf-8')
            return imgbyteBase64Str
            '''#store it in local
            imgData = base64.b64decode(imgbyteBase64Str)
            fileName = 'C:/work/temp/resp.png'
            with open(fileName, 'wb') as f:
                f.write(imgData)'''
            
        except Exception:
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'doLogin', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
        
    def doLogin(self, obj, randomFlag, verifycode):
        try:
            dataResult = {
                    "result": "False",
                    "msg":""
                }
            
            ##time.sleep(10)
            #U2FsdGVkX1%2B8CHhx2vKYzNLuTUDVPzluCZkMCbGtfnP%2F23IyiS0GB%2FRcQtI1O7z9i3j1ey%2F0WB3cDWFW9OApTql%2B0wG8x9tOXEi%2B6DVS3Wo%3D
            url = 'http://login.189.cn/login' 
            login_post_data = {
                'Account': str(self.login_account),
                'AreaCode': '',
                'Captcha': '',
                'CityNo': '',
                'Password': str(obj["result"]["password"]),
                'ProvinceID': self.ProvinceID,
                'RandomFlag': self.randomFlag,
                'UType': '201'
            }
#             cookieVal = 'ECSLoginReq='+ self.session.cookies["ECSLoginReq"] 
            if(verifycode != ''):
                login_post_data = {
                    'Account': str(self.login_account),
                    'AreaCode': '',
                    'Captcha': '',
                    'CityNo': '',
                    'Password': str(obj["result"]["password"]),
                    'ProvinceID': self.ProvinceID,
                    'RandomFlag': randomFlag,
                    'UType': '201',
                    'Captcha':verifycode
                }
#                 cookieVal += ';ECS_Captcha_login='+ self.session.cookies["ECS_Captcha_login"] 
                
            self.session.cookies["ECS_ReqInfo_login1"] = self.logInfo    
            headerStr = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Content-Length':'121',
                'Content-Type':'application/x-www-form-urlencoded',
                'Host':'login.189.cn',
                'Origin':'http://login.189.cn',
                'Referer':'http://login.189.cn/login',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent' : 'python-requests/2.12.3',
                'Proxy-Connection':'keep-alive'
#                 'Cookie': cookieVal 
                #'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            }
            ##self.session.cookies["ECS_ReqInfo_login1"] = "U2FsdGVkX196M7FM0p64n8M+z1I12RQm+Bca/XNBE0ElXoV6BF2yUkGvqWFQSeCNFdcTLxKln7nOqrBYWi32Lgh3o9IPg4ReDihEJ1iITFk="
            
            proxies1 = {"http"  : '42.99.16.164:80'}
           
            
            getLoginresp = self.session.post(url, data = login_post_data, headers = headerStr, verify = True, allow_redirects = True, timeout = None)
            #self.session.resolve_redirects(getLoginresp,self.session)
            #print(getLoginresp.text)
            # print("LOGGINNN PAGE"+ str(getLoginresp))
            #print(self.session.cookies)
            print(getLoginresp.url)
            ##time.sleep(10)
            if(getLoginresp.url.find("ecs.do") > 0):
                #time.sleep(10)
                '''getUamTOresp = self.session.get(getLoginresp.url, headers = headerStr, verify = False, allow_redirects = True)
                print(getUamTOresp.text)
                print(getUamTOresp.url)
                print(self.session.cookies)'''
                #time.sleep(10)
                Ticket = getLoginresp.url.split('&')[-2]
                TxID = getLoginresp.url.split('&')[-1]
                
#                 getEcsurl = 'http://www.189.cn/login/ecs.do?method=loginJXUamGet&PlatNO=90000&ResultCode=0&'+ Ticket +'&'+ TxID
                getEcsurl = 'http://www.189.cn/login/ecs.do?PlatNO=90000&ResultCode=0&'+ Ticket +'&'+ TxID
                headerStr1 = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Cache-Control':'max-age=0',
                    'Connection':'keep-alive',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'www.189.cn',
                    'Origin':'http://login.189.cn',
                    'Referer':'http://login.189.cn/login',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent' : 'python-requests/2.12.3',
                    'Proxy-Connection':'keep-alive',
                    'Cookie': 'EcsLoginToken='+ self.session.cookies["EcsLoginToken"] 
                    #'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
                }
                getEcsresp = self.session.get(getEcsurl, headers = headerStr1, verify = True, allow_redirects = True, timeout = None)
                print(getEcsresp.url)
                
                getRes = getEcsresp.text
                try:
                    respSoup = BeautifulSoup(getRes,'html.parser')
                    
                    down_05_ul = respSoup.find('div',{"class": "down_05_ul"})#div
                    #bb0  div
                    down_05_ulTxt = BeautifulSoup(str(down_05_ul),'html.parser')
                    
                    bb0 = down_05_ulTxt.findAll('div',{"class": "bb0"})
                    
                    bb0 = BeautifulSoup(str(bb0),'html.parser')
                    aTags = bb0.findAll('a')
                    self.frontUrl = aTags[1].get('href')
                except Exception:
                    self.frontUrl = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407'
                print(self.frontUrl)
                
                dataResult = {
                    "result": "True",
                    "msg":"success"
                }
                return dataResult
            elif(getLoginresp.url.find("login.189.cn") > 0):
                #print(getLoginresp.text)
                respSoup = BeautifulSoup(getLoginresp.text,'html.parser')
                nameTags = respSoup.findAll('form',{"data-errmsg":True})
                #print(nameTags)
                errorMsg = "登录错误"
                data_resultcode =''
                for n in nameTags:
                    errorMsg = (n['data-errmsg'])
                    data_resultcode = str(n['data-resultcode'])
                #print(errorMsg+ "data-resultcode : " +str(data_resultcode))
                if errorMsg == "瀵嗙爜宸茶閿佸畾":
#                     print("Password locked try random password")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                elif data_resultcode == "9103":
#                     print("Password error")
                    dataResult = {
                        "result": "False",
                        "msg":errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                elif data_resultcode == "9999":
#                     print("need Verification code")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                elif data_resultcode == "9113":
#                     print("Password locked")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : "9113"
                    }
                else:
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                CTCC.uploadException( self, username = self.login_account, step = 'doLogin', errmsg = dataResult["msg"] )
                
                return dataResult
                 
            
            #
        except Exception :
            print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'doLogin', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData["result"] = "False"
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
            
    def doRandomPasswordLogin(self, obj):
        try:
            
            dataResult = {
                    "result": "False",
                    "msg": ""
                }
            passwordSMSUrl = 'http://login.189.cn/login/ajax'
            passwordSMSHeader = {
                        'Accept':'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'33',
                        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
#                         'Cookie':'ECSLoginReq='+ self.session.cookies["ECSLoginReq"] ,
                        'Host':'login.189.cn',
                        'Origin':'http://login.189.cn',
                        'Referer':'http://login.189.cn/login',
                        'User-Agent':'python-requests/2.12.3',
                        'X-Requested-With':'XMLHttpRequest'
                }
            passwordSMS_postData = {
                    'm':'sendrandompwd',
                    'phone':str(self.login_account)
                }
            getPasswordSMSresp = self.session.post(passwordSMSUrl, data = passwordSMS_postData, headers = passwordSMSHeader, verify = True, allow_redirects = True, timeout = None)
            #self.session.resolve_redirects(getLoginresp,self.session)
            #print(getLoginresp.text)
            #print("SMS PAssword PAGE"+ str(getPasswordSMSresp.text))
            #print(self.session.cookies)
            resp = json.loads(getPasswordSMSresp.text)
            #print(resp)
#             print(resp['ResultCode'])
            if str(resp['ResultCode']) == '0':
                dataResult = {
                    "result": "True",
                    "msg": "success"
                }
            else:
#                 print(resp['Desc'])
                dataResult = {
                    "result": "False",
                    "msg": resp['Desc']
                }
            return dataResult
        except Exception :
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'doRandomPasswordLogin', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
        
    
        
    def goFrontPage(self):
        try:
            time.sleep(1)
            self.smsCount = 0;
            self.phoneDetail  = []
           
    
    
            checkMySession = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
            checkMySessionHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '17',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : '.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT=' + self.session.cookies['JSESSIONID-JT'] + ';;userId=' + self.session.cookies['userId'] + ';cityCode=he;'
                }
            check_data = {
                    'fastcode':'00420429'
                }
            check_data = 'fastcode=00420429'
            sessionResp = self.session.post(checkMySession, headers = checkMySessionHeader, data = check_data , verify = False, allow_redirects = False) 
#             print(sessionResp.text)
            #print(self.frontUrl)
            billFrontPageHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cache-Control':'max-age=0',
                        'Connection':'keep-alive',
                        'Host':'www.189.cn',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'Cookie': 'aactgsh111220='+ self.session.cookies['aactgsh111220'] +';userId=' + self.session.cookies['userId'] + ';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                }
            billPageUrlresp = self.session.get(self.frontUrl, headers = billFrontPageHeader, verify = False, allow_redirects = True) 
            #print(billPageUrlresp.text)
#             print(billPageUrlresp.url)
            #print(self.session.cookies)
            
            ssolink = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he'
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie': 'isLogin=logined;loginStatus=logined;aactgsh111220='+ self.session.cookies['aactgsh111220'] +';userId=' + self.session.cookies['userId'] + ';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                }
            SSoResp = self.session.get(ssolink, headers = ssoHeader, verify = False, allow_redirects = False) 
            #print(SSoResp.text)
#             print(SSoResp.url)
            
            ecslink = SSoResp.headers['Location']
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie': 'isLogin=logined;loginStatus=logined;aactgsh111220='+ self.session.cookies['aactgsh111220'] +';userId=' + self.session.cookies['userId'] + ';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                }
            ecsResp = self.session.get(ecslink, headers = ssoHeader, verify = False, allow_redirects = False) 
            #print(SSoResp.text)
#             print(ecsResp.url)
            
            ecsssoUrl = ecsResp.headers['Location']
            ECSSSOTransitHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Host':'login.189.cn',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                        'Cookie': 'ECS_ReqInfo_login1='+self.session.cookies['ECS_ReqInfo_login1'] +';EcsCaptchaKey='+self.session.cookies['EcsCaptchaKey']+';EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            ECSSSOUrlresp = self.session.get(ecsssoUrl, headers = ECSSSOTransitHeader, verify = False, allow_redirects = False)
#             print(ECSSSOUrlresp.text) 
            Url1 = ECSSSOUrlresp.url
#             print(Url1)
#             print(self.session.cookies)
            
            loginSSo = ECSSSOUrlresp.headers['Location']
#             print(loginSSo)
            loginSSOHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'aactgsh111220=' + self.session.cookies['aactgsh111220'] + '; userId='+ self.session.cookies['userId'] +'; isLogin=logined; .ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] +'; loginStatus=logined; cityCode=he; SHOPID_COOKIEID=10006;',
                    'Host':'he.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
                }
            loginSSoresp = self.session.get(loginSSo, headers = loginSSOHeader, verify = False, allow_redirects = False)
#             print(ECSSSOUrlresp.text) 
            Url1 = loginSSoresp.headers['Location']
#             print(Url1)
#             print(self.session.cookies)
            
            
            
            
            
            feeQueryHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'he.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Cookie' : '.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';BIGipServerHB-WTpool='+ self.session.cookies['BIGipServerHB-WTpool'] + ';JSESSIONID=' + self.session.cookies['JSESSIONID'] + ';SHOPID_COOKIEID=' + self.session.cookies['SHOPID_COOKIEID']+ ';aactgsh111220='+ self.session.cookies['aactgsh111220'] +';userId=' + self.session.cookies['userId']
                }
            Url1resps = self.session.get(Url1, headers = feeQueryHeader, verify = False, allow_redirects = True) 
#             print(Url1resps.url)
#             print(Url1resps.text)http://he.189.cn/service/bill/action/ifr_bill_detailslist_new_iframe.jsp http://he.189.cn/service/bill/feeQuery_iframe.jsp?%20SERV_NO=SHQD1&fastcode=00380407&cityCode=he
            billResp = Url1resps.text
            
            searchstr = "doQuery('"
            start = billResp.find(searchstr)
            end = billResp.find(");" , start)
            doQueryStr = billResp[start + len(searchstr) : end]
#             print(doQueryStr)
            doQueryArr = doQueryStr.split(',')
            self.AreaCodeStr = str(doQueryArr[1])[1:len(doQueryArr[1]) - 1]
            self.ProdNoStr = str(doQueryArr[2])[1:len(doQueryArr[2]) - 1]
            self.UserName = str(doQueryArr[3])[1:len(doQueryArr[3]) - 1]
            self.ServiceKind = str(doQueryArr[4])[1:len(doQueryArr[4]) - 1]
            self.UserIdStr = str(doQueryArr[5])[1:len(doQueryArr[5]) - 1]
            
            nameEncode = parse.quote(self.UserName)
            
            
            
            
            new_iframe = 'http://he.189.cn/service/bill/action/ifr_bill_detailslist_new_iframe.jsp'
            newIframeHeader = {
                    'Host': 'he.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '116',
                    'Accept': '*/*',
                    'Origin': 'http://he.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : '.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';BIGipServerHB-WTpool='+ self.session.cookies['BIGipServerHB-WTpool'] + ';JSESSIONID=' + self.session.cookies['JSESSIONID'] + ';SHOPID_COOKIEID=' + self.session.cookies['SHOPID_COOKIEID']+ ';aactgsh111220='+ self.session.cookies['aactgsh111220'] +';userId=' + self.session.cookies['userId']
                }
            newFrameData = 'NUM='+ self.mobile +'&AREA_CODE='+ self.AreaCodeStr +'&PROD_NO='+ self.ProdNoStr +'&USER_NAME='+ nameEncode +'&ServiceKind='+ self.ServiceKind +'&USER_ID='+ self.UserIdStr
#             print(newFrameData)
            newFrameresps = self.session.post(new_iframe, headers = newIframeHeader, data = newFrameData, verify = False, allow_redirects = True) 
#             print(newFrameresps.url)
#             print(newFrameresps.text)
            responseTxt = newFrameresps.text
            
            resp = BeautifulSoup(str(newFrameresps.text),'html.parser')
            
            self.PRODTYPE =  resp.find('input', {'name' : 'PRODTYPE'}).get('value')
            print(self.PRODTYPE)
            
            QUERY_TYPE = resp.find('select', {'id' : 'QUERY_TYPE'})
            ACCT_DATE = resp.find('select', {'id' : 'ACCT_DATE'})
            self._FUNC_ID_ = resp.find('input',{'id' : '_FUNC_ID_'}).get('value')
#             print(self._FUNC_ID_)
#             print(QUERY_TYPE)
#             print(ACCT_DATE)
            
            self.QUERYTYPE = []
            respHtml = BeautifulSoup(str(QUERY_TYPE),'html.parser')
            for option in respHtml.findAll('option'):
                self.QUERYTYPE.append({'value': option['value'] , 'queryTxt' : option.text})
                
#             print(self.QUERYTYPE)
            self.monthVal = []
            monthRespHtml = BeautifulSoup(str(ACCT_DATE),'html.parser')
            for option in monthRespHtml.findAll('option'):
                year = re.compile(r'(.*?)年')
                yearA = re.findall(year,option['year'])
                
                month = re.compile(r'(.*?)月')
                monthA = re.findall(month,option['month'])
                self.monthVal.append({'FEE_DATE': option['value'] , 'BEGIN_DATE' : yearA[0]+ '-' + monthA[0] + '-01 00:00:00', 'END_DATE': yearA[0]+ '-' + monthA[0] + '-'+ option['maxday'] +' 23:59:59'})
            
#             print(self.monthVal)
            
            self.retCode = resp.find('input', {'name' : 'retCode'}).get('value')
#             print(self.retCode)
            msg = ''
            if(self.retCode == '0'):
                msg = '您当前不是实名制用户，请到附近的实体营业厅进行实名制补登记。'
            elif(self.retCode != '0000'):
                msg = '获取实名制信息失败，请重试。'
                
            if(msg != ''):
                CTCC.uploadException( self, username = self.login_account, step = 'getSMSCode', errmsg = msg )
                returnData = CTCC.init( self )
                returnData['status'] = 'false'
                returnData['success1'] = 'false'
                returnData['msg'] =  msg
                return returnData    
            
            searchstr = 'postValidCode.jsp'
            start = responseTxt.find(searchstr)
            end = responseTxt.find('beforeSend' , start)
            postValidCodeFn = responseTxt[start + len(searchstr) + 1 : end]
#             print(postValidCodeFn)
            
            searchstr = 'LOGIN_TYPE: '
            start = postValidCodeFn.find(searchstr)
            end = postValidCodeFn.find('",' , start)
            self.LOGIN_TYPE = postValidCodeFn[start + len(searchstr) + 1 : end]
#             print(self.LOGIN_TYPE)
            
            searchstr = 'OPER_TYPE: '
            start = postValidCodeFn.find(searchstr)
            end = postValidCodeFn.find('",' , start)
            self.OPER_TYPE = postValidCodeFn[start + len(searchstr) + 1 : end]
#             print(self.OPER_TYPE)
            
            searchstr = 'RAND_TYPE: '
            start = postValidCodeFn.find(searchstr)
            end = postValidCodeFn.find('"}' , start)
            self.RAND_TYPE = postValidCodeFn[start + len(searchstr) + 1 : end]
#             print(self.RAND_TYPE)
            
            searchstr = 'FLAG_QUERYSTR: '
            start = responseTxt.find(searchstr)
            end = responseTxt.find('}' , start)
            self.FLAG_QUERYSTR = responseTxt[start + len(searchstr) : end]
            
            flowRecommUrl = 'http://www.189.cn/dqmh/flowrecommend.do'
            flowRecommHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie': 'JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'] +'; aactgsh111220='+ self.session.cookies['aactgsh111220'] +'; userId='+self.session.cookies['userId'] +'; isLogin=logined; .ybtj.189.cn='+self.session.cookies['.ybtj.189.cn'] +'; loginStatus=logined; cityCode=he; SHOPID_COOKIEID=10006'
                }
            '''flowResps = self.session.post(flowRecommUrl, headers = flowRecommHeader,  verify = False, allow_redirects = True) '''
#             print(flowResps.url)
#             print(flowResps.text)
            
            checkMySession = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
            checkMySessionHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '17',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookies': 'userId='+ self.session.cookies['userId'] +';.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';SHOPID_COOKIEID='+ self.session.cookies['SHOPID_COOKIEID'] + ';cityCode=he;isLogin=logined;loginStatus=logined;aactgsh111220='+ self.session.cookies['aactgsh111220'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT']
                }
            check_data = {
                    'fastcode':'00380407'
                }
            sessionResp = self.session.post(checkMySession, headers = checkMySessionHeader, data = check_data , verify = False, allow_redirects = True) 
#             print(sessionResp.text)
            respObj = json.loads(str(sessionResp.text).strip(), encoding = 'utf-8')
            if(respObj['status'] == "2"):
                returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : 'getsms'
                }
            else:
                returnData = {
                        'status' : 'true' ,
                        'success1': 'true',
                        'msg' : 'goLogin'
                    }
            return returnData
            
            '''
            #SEND SMS
            smsUrl = 'http://he.189.cn/public/postValidCode.jsp'
            smsHeader = {
                    'Host': 'he.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '71',
                    'Accept': 'application/xml, text/xml, */*',
                    'Origin': 'http://he.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : '.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';BIGipServerHB-WTpool='+ self.session.cookies['BIGipServerHB-WTpool'] + ';JSESSIONID=' + self.session.cookies['JSESSIONID'] + ';SHOPID_COOKIEID=' + self.session.cookies['SHOPID_COOKIEID']+ ';userId=' + self.session.cookies['userId']
                }
            smsPostData = 'NUM='+ self.mobile +'&AREA_CODE='+ self.AreaCodeStr +'&LOGIN_TYPE='+ self.LOGIN_TYPE +'&OPER_TYPE='+ self.OPER_TYPE +'&RAND_TYPE='+ self.RAND_TYPE
            smsResps = self.session.post(smsUrl, headers = smsHeader, data = smsPostData, verify = False, allow_redirects = True) 
#             print(smsResps.url)
#             print(smsResps.text)
            smsResps = smsResps.text
            
            searchstr = '<actionFlag>'
            start = smsResps.find(searchstr)
            end = smsResps.find('</actionFlag>' , start)
            actionFlag = smsResps[start + len(searchstr) : end]
#             print(actionFlag)
            
            
            searchstr = '<actionMsg>'
            start = smsResps.find(searchstr)
            end = smsResps.find('</actionMsg>' , start)
            actionMsg = smsResps[start + len(searchstr) : end]
            
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            if(str(actionFlag) != '0'):
                returnData = CTCC.init( self )
                returnData['msg'] = actionMsg
                returnData['success1'] = 'false'
                '''
            
            '''checkMySession = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
            checkMySessionHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '17',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : 'JSESSIONID='+ self.session.cookies['JSESSIONID'] +';USER_INFO='+ self.session.cookies['USER_INFO'] +';.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT=' + self.session.cookies['JSESSIONID-JT'] + ';SHOPID_COOKIEID=' + self.session.cookies['SHOPID_COOKIEID']+ ';userId=' + self.session.cookies['userId'] + ';cityCode=he;'
                }
            check_data = {
                    'fastcode':'00420429'
                }
            check_data = 'fastcode=00420429'
            sessionResp = self.session.post(checkMySession, headers = checkMySessionHeader, data = check_data , verify = False, allow_redirects = False) 
            print(sessionResp.text)'''
            
            '''ssolink = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : '.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT=' + self.session.cookies['JSESSIONID-JT'] + ';SHOPID_COOKIEID=' + self.session.cookies['SHOPID_COOKIEID']+ ';userId=' + self.session.cookies['userId']
                }
            SSoResp = self.session.get(ssolink, headers = ssoHeader, verify = False, allow_redirects = True) 
            #print(SSoResp.text)
            print(SSoResp.url)'''
            '''time.sleep(1)
            checkMySession = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
            checkMySessionHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '17',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : 'loginStatus=non-logined;JSESSIONID='+ self.session.cookies['JSESSIONID'] +';USER_INFO='+ self.session.cookies['USER_INFO'] +';.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT=' + self.session.cookies['JSESSIONID-JT'] + ';SHOPID_COOKIEID=' + self.session.cookies['SHOPID_COOKIEID']+ ';userId=' + self.session.cookies['userId'] + ';cityCode=he;'
                }
            check_data = {
                    'fastcode':'00420429'
                }
            check_data = 'fastcode=00420429'
            sessionResp = self.session.post(checkMySession, headers = checkMySessionHeader, data = check_data , verify = False, allow_redirects = False) 
            print(sessionResp.text)'''
            '''
            index = 'http://www.189.cn/login/index.do'
            indexREg = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'loginStatus=non-logined; JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'] +'; aactgsh111220=13315923020; userId='+ self.session.cookies['userId'] +'; isLogin=logined; .ybtj.189.cn=' + self.session.cookies['.ybtj.189.cn'],
                    'Host':'www.189.cn',
                    'Referer':'http://www.189.cn/html/login/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            sessionResp1 = self.session.get(index, headers = indexREg, verify = False, allow_redirects = False) 
            print(sessionResp1.text)'''
            
            '''ssolink = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie': 'aactgsh111220='+ self.session.cookies['aactgsh111220'] +';userId=' + self.session.cookies['userId'] + ';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                }
            SSoResp = self.session.get(ssolink, headers = ssoHeader, verify = False, allow_redirects = True) 
            #print(SSoResp.text)
            print(SSoResp.url)
            
            ECSSSOTransitHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Host':'login.189.cn',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                        'Cookie': 'EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            ECSSSOUrlresp = self.session.get(SSoResp.url, headers = ECSSSOTransitHeader, verify = False, allow_redirects = True)
#             print(ECSSSOUrlresp.text) 
            Url1 = ECSSSOUrlresp.url
            print(Url1)
            print(self.session.cookies)'''
            
                
            '''ssolink = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8'
                }
            SSoResp = self.session.get(ssolink, headers = ssoHeader, verify = False, allow_redirects = True) 
            #print(SSoResp.text)
            print(SSoResp.url)
           
            
            ECSSSOTransitHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Host':'login.189.cn',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                        'Cookie': 'EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            ECSSSOUrlresp = self.session.get(SSoResp.url, headers = ECSSSOTransitHeader, verify = False, allow_redirects = True)
#             print(ECSSSOUrlresp.text) 
            Url1 = ECSSSOUrlresp.url
            print(Url1)
            if(Url1 == 'http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'):
                myselfInfoHtml = BeautifulSoup(str(ECSSSOUrlresp.text).strip(),'html.parser')
                custTable = myselfInfoHtml.find("table")
            else:
               
                
                time.sleep(0.5)
                Url1Header = {
                            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding':'gzip, deflate, sdch',
                            'Accept-Language':'zh-CN,zh;q=0.8',
                            'Connection':'keep-alive',
                            'Host':'he.189.cn',
                            'Upgrade-Insecure-Requests':'1',
                            'User-Agent' : 'python-requests/2.12.3',
                            'Referer':'http://www.189.cn/hb/',
                            'Cookie': 'cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID='+ self.session.cookies['JSESSIONID'],
                            #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                    }
                Url1resps = self.session.get(Url1, headers = Url1Header, verify = False, allow_redirects = False) 
                print(Url1resps.url)
                #print(Url1resps.text)
                
                
                userInforUrl = 'http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
                userInfoHeader = {
                        'Host': 'he.189.cn',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8'
                    }
                userinfoResp = self.session.get(userInforUrl, headers = userInfoHeader, verify = False, allow_redirects = False) 
    #             print(userinfoResp.text)
                print(userinfoResp.url)
                
                myselfInfoHtml = BeautifulSoup(str(userinfoResp.text).strip(),'html.parser')
    #             print(myselfInfoHtml)
                custTable = myselfInfoHtml.find("table")
                
            trVal = custTable.findAll('tr')
            
#             print(trVal)
            userInfo = {}
            phoneInfo= {}
            i = 0
            for tr in trVal:
                trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                td = trTD.find('td')
#                 print(td)
                
                if(i == 0):
                    userInfo['name'] = str(td.text).strip()
                if(i == 3):
                    phoneInfo['status'] = str(td.text).strip()
                if(i == 5):
                    userInfo['certType'] =  str(td.text).strip()
                if(i == 6):
                    userInfo['certNum'] =  str(td.text).strip()
                    userInfo['certNo'] =  str(td.text).strip()
                if(i == 7):
                    userInfo['address'] =  str(td.text).strip()
                    userInfo['addr'] =  str(td.text).strip()
                
                i += 1
            userInfo['inNetDate'] =  ""
            self.result_info['userInfo'] = userInfo
            self.result_info['phoneInfo'] = phoneInfo
            
            self.result_info["userInfo"]["balance"] = "0"
            self.result_info["userInfo"]["oweFee"] = "0"
            self.result_info["userInfo"]["status"] = "0"
#             print(self.result_info)'''
            
            
            '''ssolink = 'http://www.189.cn/login/sso/ecs.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he'
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8'
                }
            SSoResp = self.session.get(ssolink, headers = ssoHeader, verify = False, allow_redirects = True) 
            #print(SSoResp.text)
            print(SSoResp.url)
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : 'gofrontpage'
                }
            return returnData'''
            
        except Exception :
            #print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'goFrontPage', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'false'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
        
    def getLoginAgain(self):
        try:
            print(self.session.cookies)
            obj = {
                "result":{
                    'password' : self.encry_password
                    }
                }
            loginData = CTCC.doLogin(self, obj, '0', '')
            #print(self.session.cookies)
            resulData = CTCC.getUSERINFO(self)
            #if( loginData["result"] == "True" ):
            print("logined")
            returnData = {}
            returnData = {
                'status' : 'true' ,
                'success1': 'true',
                'msg' : 'getsms'
            }
        
            return returnData
            '''else:
                CTCC.uploadException( self, username = self.login_account, step = 'goFrontPage', errmsg = str(loginData) )
                returnData = CTCC.init( self )
                returnData['status'] = 'false'
                returnData['success1'] = 'false'
                returnData['msg'] = '统异常,请稍后重试,code:1005'
                return returnData'''
        except Exception:
            #print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'goFrontPage', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'false'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
    
    def getSMSCode(self):
        try:
            #print(self.session.cookies)
            checkMySession = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
            checkMySessionHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '17',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookies': 'userId='+ self.session.cookies['userId'] +';.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';SHOPID_COOKIEID='+ self.session.cookies['SHOPID_COOKIEID'] + ';cityCode=he;isLogin=logined;loginStatus=logined;aactgsh111220='+ self.session.cookies['aactgsh111220'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT']
                }
            check_data = {
                    'fastcode':'00380407'
                }
            sessionResp = self.session.post(checkMySession, headers = checkMySessionHeader, data = check_data , verify = False, allow_redirects = True) 
#             print(sessionResp.text)
            
            
            
            #SEND SMS
            smsUrl = 'http://he.189.cn/public/postValidCode.jsp'
            smsUrl = 'http://he.189.cn/service/transaction/postValidCode.jsp'
            smsHeader = {
                    'Host': 'he.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '71',
                    'Accept': 'application/xml, text/xml, */*',
                    'Origin': 'http://he.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8'
                }
            smsPostData = 'NUM='+ self.mobile +'&AREA_CODE='+ self.AreaCodeStr +'&LOGIN_TYPE='+ self.LOGIN_TYPE +'&OPER_TYPE='+ self.OPER_TYPE +'&RAND_TYPE='+ self.RAND_TYPE
            today = datetime.datetime.today()
            
            format = "%a %b %d %Y %H:%M:%S"


            s = today.strftime(format)
            smsPostData = 'reDo='+ str(s) +'&OPER_TYPE='+ self.OPER_TYPE +'&RAND_TYPE='+ self.RAND_TYPE +'&PRODTYPE='+self.PRODTYPE+'&MOBILE_NAME='+  self.mobile + '&MOBILE_NAME_PWD=&NUM='+ self.mobile +'&AREA_CODE='+ self.AreaCodeStr +'&LOGIN_TYPE='+ self.LOGIN_TYPE
            CTCC.uploadException( self, username = self.login_account, step = 'smsPostData', errmsg = smsUrl + ' _ '+ str(smsPostData) )
            '''reDo:Thu Nov 23 2017 09:09:10 GMT+0800 (中国标准时间)
            OPER_TYPE:CR1
            RAND_TYPE:006
            PRODTYPE:2020966
            MOBILE_NAME:17788216030
            MOBILE_NAME_PWD:
            NUM:17788216030
            AREA_CODE:188
            LOGIN_TYPE:21'''
            smsResps = self.session.post(smsUrl, headers = smsHeader, data = smsPostData, verify = False, allow_redirects = True)
           
            CTCC.uploadException( self, username = self.login_account, step = 'smsResps', errmsg = smsUrl + ' _ '+ str(smsResps.text) )
#             print(smsResps.url)
#             print(smsResps.text)
            smsResps = smsResps.text
            
            searchstr = '<actionFlag>'
            start = smsResps.find(searchstr)
            end = smsResps.find('</actionFlag>' , start)
            actionFlag = smsResps[start + len(searchstr) : end]
#             print(actionFlag)
            
            
            searchstr = '<actionMsg>'
            start = smsResps.find(searchstr)
            end = smsResps.find('</actionMsg>' , start)
            actionMsg = smsResps[start + len(searchstr) : end]
            
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            if(str(actionFlag) != '0'):
                returnData = CTCC.init( self )
                CTCC.uploadException( self, username = self.login_account, step = 'sms sent failed', errmsg =  str(smsResps) )
                returnData['msg'] = actionMsg
                returnData['success1'] = 'false'
                
            return returnData
            
        except Exception:
            #print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'getSMSCode', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'false'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData     
        
    def checkSMSCode(self):
        try:
            if(self.smsCount < 2):
                CTCC.uploadException( self, username = self.login_account, step =  'sms code again', errmsg = str(self.smsCount) + "sent sms code" )
                
                #Check SMS
                checkSmsUrl = 'http://he.189.cn/public/pwValid.jsp'
                checkSmsUrl = 'http://he.189.cn/service/bill/action/ifr_bill_detailslist_em_new.jsp'
                smsHeader = {
                        'Host': 'he.189.cn',
                        'Connection': 'keep-alive',
                        'Content-Length': '71',
                        'Accept': 'application/xml, text/xml, */*',
                        'Origin': 'http://he.189.cn',
                        'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': 'http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8'
                    }
                nameEncode = parse.quote(self.UserName)
                try:
                    self.CustIdNum = self.result_info['userInfo']['certNum']
                    strvar = re.findall("\d+", self.CustIdNum)
                    if(len(strvar) != 0):
                        self.CustIdNum = str(strvar[0])
                    else:
                        self.CustIdNum = '131002'
                except Exception:
                    self.CustIdNum = '131002'
                
                smsPostData = '_FUNC_ID_='+ self._FUNC_ID_ +'&CustName='+ nameEncode +'&IdentityCode='+ self.CustIdNum +'&ACC_NBR='+ self.mobile +'&AREA_CODE='+ self.AreaCodeStr +'&LOGIN_TYPE='+ self.LOGIN_TYPE +'&MOBILE_FLAG=&MOBILE_LOGON_NAME=&MOBILE_CODE='+ self.mobilecode +'&FLAG_QUERYSTR='+ self.FLAG_QUERYSTR
                smsPostData = 'ACC_NBR='+ self.mobile  +'&CITY_CODE='+ self.AreaCodeStr +'&BEGIN_DATE='+ self.monthVal[self.smsCount]['BEGIN_DATE'] +'&END_DATE='+ self.monthVal[self.smsCount]['END_DATE'] +'&FEE_DATE='+  self.monthVal[self.smsCount]['FEE_DATE']  +'&SERVICE_KIND='+ self.ServiceKind +'&retCode='+self.retCode+'&QUERY_FLAG=1&QUERY_TYPE_NAME=%E7%A7%BB%E5%8A%A8%E8%AF%AD%E9%9F%B3%E8%AF%A6%E5%8D%95&QUERY_TYPE=1&radioQryType=on&QRY_FLAG=1&ACCT_DATE='+self.monthVal[self.smsCount]['FEE_DATE']+'&ACCT_DATE_1='+self.monthVal[self.smsCount]['FEE_DATE']+'&sjmput=' + self.mobilecode
                CTCC.uploadException(self, self.login_account, 'check smsPostData', str(smsPostData))
                smsResps = self.session.post(checkSmsUrl, headers = smsHeader, data = smsPostData, verify = False, allow_redirects = True)
                self.smsCount = self.smsCount + 1;
                
                CTCC.uploadException(self, self.login_account, 'smsResponse', str(smsResps.text))
    #             print(smsPostData) 
    #             print(smsResps.url)
    #             print(smsResps.text)
                smsResps = smsResps.text
                
                '''searchstr = '<actionFlag>'
                start = smsResps.find(searchstr)
                end = smsResps.find('</actionFlag>' , start)
                actionFlag = smsResps[start + len(searchstr) : end]
    #             print(actionFlag)
                
                
                searchstr = '<actionMsg>'
                start = smsResps.find(searchstr)
                end = smsResps.find('</actionMsg>' , start)
                actionMsg = smsResps[start + len(searchstr) : end]
                '''
                actionFlag = ''
                searchstr = 'info_alert">'
                start = smsResps.find(searchstr)
                end = smsResps.find('</p>' , start)
                actionFlag = smsResps[start + len(searchstr) : end]
    #             print(actionFlag)
                
                returnData = {
                        'status' : 'false' ,
                        'success1': 'true',
                        'msg' : ''
                    }
                if((start) != -1):
                    if('随机码不正确,请重新输入' in str(actionFlag.strip())):
                        
                        returnData = CTCC.init( self )
                        returnData['msg'] = actionFlag.strip()
                        returnData['success1'] = 'false'
                    else:
                        returnData = {
                            'status' : 'true' ,
                            'success1': 'true',
                            'msg' : ''
                        }
                        
                else:
                    totallen = len(smsResps)
                    strText = smsResps
                    intTotal = int(totallen/6)
                    firstpart =  strText[0 : intTotal]
                    secondpart =  strText[intTotal : (intTotal * 2)]
                    thirdpart =  strText[(intTotal * 2) : (intTotal * 3)]
                    fourthpart =  strText[(intTotal * 3) : (intTotal * 4)]
                    fifthpart =  strText[(intTotal * 4) : (intTotal * 5)]
                    sixthpart =  strText[(intTotal * 5) : (totallen)]
                    '''CTCC.uploadException( self, username = self.login_account, step = '1 checkSMSCode', errmsg = firstpart )
                    CTCC.uploadException( self, username = self.login_account, step = '2 checkSMSCode', errmsg = secondpart)
                    CTCC.uploadException( self, username = self.login_account, step = '3 checkSMSCode', errmsg = thirdpart )
                    CTCC.uploadException( self, username = self.login_account, step = '4 checkSMSCode', errmsg = fourthpart )
                    CTCC.uploadException( self, username = self.login_account, step = '5 checkSMSCode', errmsg = fifthpart)
                    CTCC.uploadException( self, username = self.login_account, step = '6  checkSMSCode', errmsg = sixthpart )'''
                    
                    resp = BeautifulSoup(str(smsResps),'html.parser')
                    tbody = resp.find('tbody')
    #                 print(tbody)
                    if(tbody != None):
                        trVal = tbody.findAll('tr')
                        for tr in trVal:
                            phoneDetailObj = {}
                            trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                            td = trTD.findAll('td')
                            try:
                                if(len(td) != 0):
                                    try:
                                        commDate =  str(td[3].text).strip()
                                        
                                        endDatestr = time.strptime(commDate,"%Y-%m-%d %H:%M:%S")
                                        commDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                                    except Exception:
                                        commDate = '00000000000000'
                                        CTCC.uploadException( self, username = self.login_account, step = 'getPhoneList', errmsg = str(td) )
                                    costVal = 0
                                    try:
                                        costVal = str(td[11].text).strip()
                                    except:
                                        try:
                                            costVal = str(td[7].text).strip()
                                        except:
                                            costVal = 0
                                    if(costVal != '' and costVal != None):
                                        cost = str(int(float(costVal) * 100)) 
                                    
                                    phoneDetailObj['commPhoneNo'] = str(td[1].text).strip()
                                    phoneDetailObj['callType'] = str(td[2].text).strip()
                                    phoneDetailObj['commDate'] = commDate[0:8]
                                    phoneDetailObj['commTime'] = commDate[8:len(commDate)]
                                    phoneDetailObj['commTotalTime'] = str(td[4].text).strip()
                                    phoneDetailObj['cost'] = cost
                                    
                                    phoneDetailObj['otherPhoneNum'] = str(td[1].text).strip()
                                    phoneDetailObj['callTypeName'] = str(td[2].text).strip()
                                    phoneDetailObj['startDate'] = commDate[0:8]
                                    phoneDetailObj['startTime'] = commDate[8:len(commDate)]
                                    phoneDetailObj['totalTime'] = str(td[4].text).strip()
                                    phoneDetailObj['totalFee'] = cost
                                    
                                    self.phoneDetail.append(phoneDetailObj)
                                else:
                                    CTCC.uploadException( self, username = self.login_account, step = 'phonelist else', errmsg = str(trTD) )
                            except Exception:
                                print('')
                    
            else:
                returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            
            return returnData
        except Exception:
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'checkSMSCode', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'false'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData       
            
    
    def getPhoneList(self):
        try:
            
            smsDetail  = []
            netDetail  = []
            prevMonth = self.monthVal[0]['FEE_DATE']
            #CTCC.uploadException( self, username = self.login_account, step = 'getPhoneList', errmsg = str(self.monthVal))
            for item in self.monthVal:
                
                phoneUrl = 'http://he.189.cn/service/bill/action/ifr_bill_detailslist_em_new_iframe.jsp'
                #phoneUrl = 'http://he.189.cn/service/bill/action/ifr_bill_detailslist_em_new.jsp'
                phoneHeader = {
                        'Host': 'he.189.cn',
                        'Connection': 'keep-alive',
                        'Content-Length': '71',
                        'Accept': 'application/xml, text/xml, */*',
                        'Origin': 'http://he.189.cn',
                        'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': 'http://he.189.cn/service/bill/feeQuery_iframe.jsp?SERV_NO=SHQD1&fastcode=00380407&cityCode=he',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8'
                    }
                phoneData = {}
                try:
                    phoneData = {
                            'ACC_NBR': self.mobile,
                            'CITY_CODE': self.AreaCodeStr,
                            'BEGIN_DATE': item['BEGIN_DATE'],
                            'END_DATE':  item['END_DATE'],
                            'FEE_DATE': item['FEE_DATE'],
                            'SERVICE_KIND': self.ServiceKind,
                            'retCode': self.retCode,
                            'QUERY_TYPE_NAME':'移动语音详单',#移动语音详单
                            'QUERY_TYPE':'1',
                            'radioQryType':'on',
                            'QRY_FLAG':'1',
                            'ACCT_DATE': item['FEE_DATE'],
                            'ACCT_DATE_1': prevMonth,
                            'sjmput' : self.mobilecode
                        }
                    phoneData = 'ACC_NBR='+ self.mobile  +'&CITY_CODE='+ self.AreaCodeStr +'&BEGIN_DATE='+ item['BEGIN_DATE'] +'&END_DATE='+ item['END_DATE'] +'&FEE_DATE='+  item['FEE_DATE']  +'&SERVICE_KIND='+ self.ServiceKind +'&retCode='+self.retCode+'&QUERY_FLAG=1&QUERY_TYPE_NAME=%E7%A7%BB%E5%8A%A8%E8%AF%AD%E9%9F%B3%E8%AF%A6%E5%8D%95&QUERY_TYPE=1&radioQryType=on&QRY_FLAG=1&ACCT_DATE='+item['FEE_DATE']+'&ACCT_DATE_1='+item['FEE_DATE']+'&sjmput='
                    #CTCC.uploadException( self, username = self.login_account, step = ' phoneData inside phonelist ', errmsg = str(phoneData))
                except:
                    CTCC.uploadException( self, username = self.login_account, step = 'exception phoneData inside phonelist ', errmsg = str(traceback.format_exc() ))
                phoneListResps = self.session.post(phoneUrl, headers = phoneHeader, data = phoneData, verify = False, allow_redirects = True)
                #print(phoneListResps.text)
                totallen = len(phoneListResps.text)
                strText = str(phoneListResps.text)
                
                totallen = len(strText)
                intTotal = int(totallen/10)
                firstpart =  strText[0 : intTotal]
                secondpart =  strText[intTotal : (intTotal * 2)]
                thirdpart =  strText[(intTotal * 2) : (intTotal * 3)]
                fourthpart =  strText[(intTotal * 3) : (intTotal * 4)]
                fifthpart =  strText[(intTotal * 4) : (intTotal * 5)]
                sixthpart =  strText[(intTotal * 5) : (intTotal * 6)]
                seventhpart =  strText[(intTotal * 6) : (intTotal * 7)]
                eighthpart =  strText[(intTotal * 7) : (intTotal * 8)]
                ninthpart =  strText[(intTotal * 8) : (intTotal * 9)]
                tenthpart =  strText[(intTotal * 9) : totallen]
                
                #CTCC.uploadException( self, username = self.login_account, step = 'inside phonelist ', errmsg = 'inside phonelist ' + str(totallen) )
                
                #CTCC.uploadException( self, username = self.login_account, step = '11 firstpart phonelist '  , errmsg = str(phoneListResps.text) )
             
#                 print(phoneData) 
#                 print(phoneListResps.url)
                
                resp = BeautifulSoup(str(phoneListResps.text),'html.parser')
                tbody = resp.find('tbody')
#                 print(tbody)
                if(tbody != None):
                    trVal = tbody.findAll('tr')
                    for tr in trVal:
                        phoneDetailObj = {}
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        try:
                            if(len(td) != 0):
                                try:
                                    commDate =  str(td[3].text).strip()
                                    
                                    endDatestr = time.strptime(commDate,"%Y-%m-%d %H:%M:%S")
                                    commDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                                except Exception:
                                    commDate = '00000000000000'
                                    CTCC.uploadException( self, username = self.login_account, step = 'getPhoneList', errmsg = str(td) )
                                costVal = 0
                                try:
                                    costVal = str(td[11].text).strip()
                                except:
                                    try:
                                        costVal = str(td[7].text).strip()
                                    except:
                                        costVal = 0
                                if(costVal != '' and costVal != None):
                                    cost = str(int(float(costVal) * 100)) 
                                
                                phoneDetailObj['commPhoneNo'] = str(td[1].text).strip()
                                phoneDetailObj['callType'] = str(td[2].text).strip()
                                phoneDetailObj['commDate'] = commDate[0:8]
                                phoneDetailObj['commTime'] = commDate[8:len(commDate)]
                                phoneDetailObj['commTotalTime'] = str(td[4].text).strip()
                                phoneDetailObj['cost'] = cost
                                
                                phoneDetailObj['otherPhoneNum'] = str(td[1].text).strip()
                                phoneDetailObj['callTypeName'] = str(td[2].text).strip()
                                phoneDetailObj['startDate'] = commDate[0:8]
                                phoneDetailObj['startTime'] = commDate[8:len(commDate)]
                                phoneDetailObj['totalTime'] = str(td[4].text).strip()
                                phoneDetailObj['totalFee'] = cost
                                
                                self.phoneDetail.append(phoneDetailObj)
                            else:
                                CTCC.uploadException( self, username = self.login_account, step = 'phonelist else', errmsg = str(trTD) )
                        except Exception:
                            print('')
                            #CTCC.uploadException( self, username = self.login_account, step = 'phonelist exception', errmsg = str(trTD) + str(traceback.format_exc()) )
                
                
                
                smsListData = {
                        'ACC_NBR': self.mobile,
                        'CITY_CODE': self.AreaCodeStr,
                        'BEGIN_DATE': item['BEGIN_DATE'],
                        'END_DATE':  item['END_DATE'],
                        'FEE_DATE': item['FEE_DATE'],
                        'SERVICE_KIND': self.ServiceKind,
                        'retCode': self.retCode,
                        'QUERY_TYPE_NAME':'移动短信详单',
                        'QUERY_TYPE':'2',
                        'radioQryType':'on',
                        'QRY_FLAG':'1',
                        'ACCT_DATE': item['FEE_DATE'],
                        'ACCT_DATE_1': prevMonth
                    }
                smsListData = 'ACC_NBR='+ self.mobile  +'&CITY_CODE='+ self.AreaCodeStr +'&BEGIN_DATE='+ item['BEGIN_DATE'] +'&END_DATE='+ item['END_DATE'] +'&FEE_DATE='+  item['FEE_DATE']  +'&SERVICE_KIND='+ self.ServiceKind +'&retCode='+self.retCode+'&QUERY_FLAG=1&QUERY_TYPE_NAME=%E7%A7%BB%E5%8A%A8%E7%9F%AD%E4%BF%A1%E8%AF%A6%E5%8D%95&QUERY_TYPE=2&radioQryType=on&QRY_FLAG=1&ACCT_DATE='+item['FEE_DATE']+'&ACCT_DATE_1='+item['FEE_DATE']+'&sjmput=' + self.mobilecode
                smsListResps = self.session.post(phoneUrl, headers = phoneHeader, data = smsListData, verify = False, allow_redirects = True)
#                 print(smsListData) 
#                 print(smsListResps.text)
                resp = BeautifulSoup(str(smsListResps.text),'html.parser')
                tbody = resp.find('tbody')
                if(tbody != None):
                    trVal = tbody.findAll('tr')
                    
                    for tr in trVal:
                        smsDetailObj = {}
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        if(len(td) != 0):
                            msgDate  =  str(td[3].text).strip()
                            
                            endDatestr = time.strptime(msgDate,"%Y-%m-%d %H:%M:%S")
                            msgDate  = time.strftime("%Y%m%d%H%M%S",endDatestr)
                            
                            costVal = str(td[9].text).strip()
                            if(costVal != '' and costVal != None):
                                cost = str(int(float(costVal) * 100)) 
                            
                            smsDetailObj['sendType'] = str(td[2].text).strip()
                            smsDetailObj['msgDate'] = msgDate[0:8]
                            smsDetailObj['msgPhone'] = str(td[1].text).strip()
                            smsDetailObj['cost'] = cost
                            
                            smsDetailObj['smsType'] = str(td[2].text).strip()
                            smsDetailObj['otherPhoneNum'] = str(td[1].text).strip()
                            smsDetailObj['smsDate'] = msgDate[0:8]
                            smsDetailObj['smsTime'] = msgDate[8:len(msgDate)]
                            smsDetailObj['totalFee'] = cost
                            
                            smsDetail.append(smsDetailObj)
                        else:
                            CTCC.uploadException( self, username = self.login_account, step = 'smslist', errmsg = str(trTD) )
                        
                netListData = {
                        'ACC_NBR': self.mobile,
                        'CITY_CODE': self.AreaCodeStr,
                        'BEGIN_DATE': item['BEGIN_DATE'],
                        'END_DATE':  item['END_DATE'],
                        'FEE_DATE': item['FEE_DATE'],
                        'SERVICE_KIND': self.ServiceKind,
                        'retCode': self.retCode,
                        'QUERY_TYPE_NAME':'移动上网详单',
                        'QUERY_TYPE':'3',
                        'radioQryType':'on',
                        'QRY_FLAG':'1',
                        'ACCT_DATE': item['FEE_DATE'],
                        'ACCT_DATE_1': prevMonth
                    }
                netListData = 'ACC_NBR='+ self.mobile  +'&CITY_CODE='+ self.AreaCodeStr +'&BEGIN_DATE='+ item['BEGIN_DATE'] +'&END_DATE='+ item['END_DATE'] +'&FEE_DATE='+  item['FEE_DATE']  +'&SERVICE_KIND='+ self.ServiceKind +'&retCode='+self.retCode+'&QUERY_FLAG=1&QUERY_TYPE_NAME=%E7%A7%BB%E5%8A%A8%E4%B8%8A%E7%BD%91%E8%AF%A6%E5%8D%95&QUERY_TYPE=3&radioQryType=on&QRY_FLAG=1&ACCT_DATE='+item['FEE_DATE']+'&ACCT_DATE_1='+item['FEE_DATE']+'&sjmput=' + self.mobilecode
                netListResps = self.session.post(phoneUrl, headers = phoneHeader, data = netListData, verify = False, allow_redirects = True)
#                 print(netListData) 
#                 print(netListResps.text)
                resp = BeautifulSoup(str(netListResps.text),'html.parser')
                tbody = resp.find('tbody')
                if(tbody != None):
                    trVal = tbody.findAll('tr')
#                     print(trVal)
                    for tr in trVal:
                        netDetailObj = {}
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        if(len(td) != 0):
                            netDate  =  str(td[1].text).strip()
                            
                            endDatestr = time.strptime(netDate,"%Y-%m-%d %H:%M:%S")
                            netDate  = time.strftime("%Y%m%d%H%M%S",endDatestr)
                            
                            netTotalTime = str(td[2].text).strip()
                            
                            hourVal = '0'
                            minuteVal = '0'
                            secondsVal = '0'
                            
                            hour = re.compile(r'(.*?)时')
                            hourA = re.findall(hour,netTotalTime)
                            if(len(hourA) > 0):
                                hourVal = hourA[0]
                                
                                netTotalTime = netTotalTime.split('时')
                                netTotalTime = netTotalTime[1]
                            
                            minute = re.compile(r'(.*?)分')
                            minuteA = re.findall(minute,netTotalTime)
                            if(len(minuteA) > 0):
                                minuteVal = minuteA[0]
                                netTotalTime = netTotalTime.split('分')
                                netTotalTime = netTotalTime[1]
                                
                            
                            seconds = re.compile(r'(.*?)秒')
                            secondsA = re.findall(seconds,netTotalTime)
                            if(len(secondsA) > 0):
                                secondsVal = secondsA[0]
                            
                            totalTime = (int(hourVal) * 3600 ) + ( int(minuteVal) * 60 ) + int(secondsVal)
                            
                            
                            costVal = str(td[7].text).strip()
                            if(costVal != '' and costVal != None):
                                cost = str(int(float(costVal) * 100)) 
                                
                            totalTraffic = str(td[3].text).strip()
                            GB = re.findall(re.compile(r'(\d*)GB'),totalTraffic)
                            MB = re.findall(re.compile(r'(\d*)MB'),totalTraffic)
                            KB = re.findall(re.compile(r'(\d*)KB'),totalTraffic)
                            
                            if( len(GB) == 0 and len(MB) == 0 and len(KB) == 0):
                                netTraffic = totalTraffic
                            else:
                                if len(GB):
                                    GB = float(GB[0])
                                else:
                                    GB = 0
                                if len(MB):
                                    MB = float(MB[0])
                                else:
                                    MB = 0
                                if len(KB):
                                    KB = float(KB[0])
                                else:
                                    KB = 0
                                
                                netTraffic = int(1024**2*GB+60*MB+KB) 
                            
                            netDetailObj['netType'] = str(td[4].text).strip()
                            netDetailObj['netDate'] = netDate
                            netDetailObj['netTotalTime'] = totalTime
                            netDetailObj['netMoney'] = cost
                            netDetailObj['flow'] = netTraffic
                            
                            netDetailObj['startTime'] = netDate
                            netDetailObj['totalTime'] = totalTime
                            netDetailObj['totalFee'] = cost
                            netDetailObj['totalTraffic'] = netTraffic
                            
                            netDetail.append(netDetailObj)
                        else:
                            CTCC.uploadException( self, username = self.login_account, step = 'netlist', errmsg = str(trTD) )
                    
            
            
                
                
                
                prevMonth = item['FEE_DATE']
                
                
            
            self.result_info['callDetail'] = self.phoneDetail
            self.result_info['smsDetail'] = smsDetail
            self.result_info['netDetail'] = netDetail
            
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            return returnData
        except Exception:
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'getPhoneList', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'false'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData   
        
    def getPaymentRecord(self):
        try:
            paymentDetail = []
            startDate = ( ( datetime.date.today()  + datetime.timedelta(1) ) + datetime.timedelta((-12)*365/12)).strftime("%Y-%m-%d")
            endDate = datetime.date.today().strftime("%Y-%m-%d") 
            
            paymentUrl = 'http://he.189.cn/service/pay/userPayfeeHisList_iframe.jsp'
            paymentHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'49',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'he.189.cn',
                    'Origin':'http://he.189.cn',
                    'Referer':'http://he.189.cn/service/pay/userPayFeeHisQuery_iframe.jsp?SERV_NO=FSE-9-3&fastcode=00400421&cityCode=he',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            paymentData = {
                    'START_ASK_DATE': startDate,
                    'END_ASK_DATE': endDate
                }
            paymentResps = self.session.post(paymentUrl, headers = paymentHeader, data = paymentData, verify = False, allow_redirects = True)
#             print(paymentData) 
#             print(paymentResps.text)
            
            resp = BeautifulSoup(str(paymentResps.text),'html.parser')
            tbody = resp.find('tbody')
            if(tbody != None):
                trVal = tbody.findAll('tr')
                
                for tr in trVal:
                    paymentListObj = {}
                    trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                    td = trTD.findAll('td')
                    
                    payDate  =  str(td[4].text).strip()
                    if(payDate != '' and payDate != None ):
                        endDatestr = time.strptime(payDate,"%Y-%m-%d %H:%M:%S")
                        payDate  = time.strftime("%Y%m%d%H%M%S",endDatestr)
                        
                       
                        
                        costVal = str(td[3].text).strip()
                        if(costVal != '' and costVal != None):
                            cost = str(int(float(costVal) * 100)) 
                        
                        paymentListObj['payChannel'] = str(td[1].text).strip()
                        paymentListObj['payFee'] = cost
                        paymentListObj['payDate'] = payDate
                        
                        paymentDetail.append(paymentListObj)
                        
            self.result_info['paymentRecord'] = paymentDetail
            
            balanceUrl = 'http://he.189.cn/service/account/query_account_balance.jsp'
            balanceHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'44',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'he.189.cn',
                    'Origin':'http://he.189.cn',
                    'Referer':'http://he.189.cn/service/account/index_iframe.jsp?fastcode=0043&cityCode=he',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            balanceData = {
                    'NUM': self.mobile,
                    'AREA_CODE': self.AreaCodeStr,
                    'SERVICE_KIND': self.ServiceKind
                }
            balResps = self.session.post(balanceUrl, headers = balanceHeader, data = balanceData, verify = False, allow_redirects = True)
#             print(balResps.text)
            
            resp = BeautifulSoup(str(balResps.text),'html.parser')

            for element in resp(text=lambda text: isinstance(text, Comment)):
                element.extract()
            
            balance = resp.prettify()
            
            if(balance != '' and balance != None):
                try:
                    balance = str(int(float(balance) * 100))
                except:
                    balance = '0' 
            
            self.result_info['phoneInfo']['balance'] = str(balance).strip()
            
            realtimeUrl = 'http://he.189.cn/service/account/query_rt.jsp'
            realMoneyHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'44',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'he.189.cn',
                    'Origin':'http://he.189.cn',
                    'Referer':'http://he.189.cn/service/account/index_iframe.jsp?fastcode=0043&cityCode=he',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            realmoneyData = {
                    'NUM': self.mobile,
                    'AREA_CODE': self.AreaCodeStr,
                    'SERVICE_KIND': self.ServiceKind
                }
            realMoneyResps = self.session.post(realtimeUrl, headers = realMoneyHeader, data = realmoneyData, verify = False, allow_redirects = True)
#             print(realMoneyResps.text)
#             realMoney = str(realMoneyResps.text).strip()
            
            resp = BeautifulSoup(str(realMoneyResps.text),'html.parser')

            for element in resp(text=lambda text: isinstance(text, Comment)):
                element.extract()
            
            realMoney = resp.prettify()
            if(realMoney != '' and realMoney != None):
                try:
                    realMoney = str(int(float(realMoney) * 100))
                except:
                    realMoney = '0' 
            
            self.result_info['phoneInfo']['realMoney'] = str(realMoney).strip()
            
            self.result_info["userInfo"]["balance"] = str(balance).strip()
            self.result_info["userInfo"]["oweFee"] = str(realMoney).strip()
            
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            return returnData
        except Exception:
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'getPaymentRecord', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'false'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData  
        
    def getUSERINFO(self):
        
        try:
            time.sleep(5)
            checkMySession = 'http://www.189.cn/dqmh/my189/checkMy189Session.do'
            checkMySessionHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Content-Length': '17',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'http://www.189.cn',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00380407',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie' : '.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT=' + self.session.cookies['JSESSIONID-JT'] + ';;userId=' + self.session.cookies['userId'] + ';cityCode=he;'
                }
            check_data = {
                    'fastcode':'00420429'
                }
            check_data = 'fastcode=00420429'
            time.sleep(0.5)
            sessionResp = self.session.post(checkMySession, headers = checkMySessionHeader, data = check_data , verify = False, allow_redirects = False) 
            sess = str(sessionResp.text)
            time.sleep(10)
            
            userInforUrl = 'http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
            userInfoHeader = {
                    'Host': 'he.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie': 'EcsCaptchaKey='+ self.session.cookies['EcsCaptchaKey'] +';aactgsh111220='+ self.session.cookies['aactgsh111220'] +';BIGipServerHB-WTpool='+ self.session.cookies['BIGipServerHB-WTpool'] +';JSESSIONID='+ self.session.cookies['JSESSIONID'] +';USER_INFO='+ self.session.cookies['USER_INFO'] +';EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                }
            userinfoResp = self.session.get(userInforUrl, headers = userInfoHeader, verify = False, allow_redirects = False) 
#             print(userinfoResp.text)
            print(userinfoResp.url)
            
            
            myselfInfoHtml = BeautifulSoup(str(userinfoResp.text).strip(),'html.parser')
#             print(myselfInfoHtml)
            custTable = myselfInfoHtml.find("table")
            CTCC.uploadException( self, username = self.login_account, step = 'userinfoResp custTable', errmsg = str(custTable) )
            
            '''ssolink = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10006&toStUrl=http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
            time.sleep(0.5)
            ssoHeader = {
                    'Host': 'www.189.cn',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cookie': 'EcsCaptchaKey='+ self.session.cookies['EcsCaptchaKey'] +';aactgsh111220='+ self.session.cookies['aactgsh111220'] +';BIGipServerHB-WTpool='+ self.session.cookies['BIGipServerHB-WTpool'] +';JSESSIONID='+ self.session.cookies['JSESSIONID'] +';USER_INFO='+ self.session.cookies['USER_INFO'] +';EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                }
            time.sleep(0.5)
            SSoResp = self.session.get(ssolink, headers = ssoHeader, verify = False, allow_redirects = True) 
            #print(SSoResp.text)
            print(SSoResp.url)
           
            time.sleep(9)
            ECSSSOTransitHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Host':'login.189.cn',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                        'Cookie': 'EcsCaptchaKey='+ self.session.cookies['EcsCaptchaKey'] +';aactgsh111220='+ self.session.cookies['aactgsh111220'] +';BIGipServerHB-WTpool='+ self.session.cookies['BIGipServerHB-WTpool'] +';JSESSIONID='+ self.session.cookies['JSESSIONID'] +';USER_INFO='+ self.session.cookies['USER_INFO'] +';EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            time.sleep(0.5)
            ECSSSOUrlresp = self.session.get(SSoResp.url, headers = ECSSSOTransitHeader, verify = False, allow_redirects = True)
#             print(ECSSSOUrlresp.text) 
            Url1 = ECSSSOUrlresp.url
            print(Url1)
            if(Url1 == 'http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'):
                myselfInfoHtml = BeautifulSoup(str(ECSSSOUrlresp.text).strip(),'html.parser')
                custTable = myselfInfoHtml.find("table")
                #CTCC.uploadException( self, username = self.login_account, step = 'ECSSSOUrlresp', errmsg = str(ECSSSOUrlresp.text) )
            else:
               
                
                time.sleep(0.5)
                Url1Header = {
                            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding':'gzip, deflate, sdch',
                            'Accept-Language':'zh-CN,zh;q=0.8',
                            'Connection':'keep-alive',
                            'Host':'he.189.cn',
                            'Upgrade-Insecure-Requests':'1',
                            'User-Agent' : 'python-requests/2.12.3',
                            'Referer':'http://www.189.cn/hb/',
                            'Cookie': 'cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID='+ self.session.cookies['JSESSIONID'],
                            #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                    }
                Url1resps = self.session.get(Url1, headers = Url1Header, verify = False, allow_redirects = False) 
                print(Url1resps.url)
                #print(Url1resps.text)
                
                time.sleep(2)
                userInforUrl = 'http://he.189.cn/service/manage/index_iframe.jsp?FLAG=1&fastcode=00420429&cityCode=he'
                userInfoHeader = {
                        'Host': 'he.189.cn',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Referer': 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00420429',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Cookie': 'EcsCaptchaKey='+ self.session.cookies['EcsCaptchaKey'] +';EcsLoginToken='+ self.session.cookies['EcsLoginToken'] +';cityCode=sd;isLogin=logined;loginStatus=logined;.ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] + ';JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'],
                    }
                userinfoResp = self.session.get(userInforUrl, headers = userInfoHeader, verify = False, allow_redirects = False) 
    #             print(userinfoResp.text)
                print(userinfoResp.url)
                #CTCC.uploadException( self, username = self.login_account, step = 'userinfoResp', errmsg = str(userinfoResp.text) )
                
                myselfInfoHtml = BeautifulSoup(str(userinfoResp.text).strip(),'html.parser')
    #             print(myselfInfoHtml)
                custTable = myselfInfoHtml.find("table")
                '''
            trVal = custTable.findAll('tr')
            
#             print(trVal)
            userInfo = {}
            phoneInfo= {}
            i = 0
            #CTCC.uploadException( self, username = self.login_account, step = 'self.custTable', errmsg = str(custTable) )
            for tr in trVal:
                trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                td = trTD.find('td')
#                 print(td)
                
                if(i == 0):
                    self.result_info['userInfo']['name'] = str(td.text).strip()
                if(i == 3):
                    self.result_info['phoneInfo']['status'] = str(td.text).strip()
                if(i == 5):
                    self.result_info['userInfo']['certType'] =  str(td.text).strip()
                if(i == 6):
                    self.result_info['userInfo']['certNum'] =  str(td.text).strip()
                    self.result_info['userInfo']['certNo'] =  str(td.text).strip()
                if(i == 7):
                    self.result_info['userInfo']['address'] =  str(td.text).strip()
                    self.result_info['userInfo']['addr'] =  str(td.text).strip()
                
                i += 1
            self.result_info['userInfo']['inNetDate'] =  ""
            #self.result_info['userInfo'] = userInfo
            #self.result_info['phoneInfo'] = phoneInfo
            CTCC.uploadException( self, username = self.login_account, step = 'self.result_infouserInfo', errmsg = str(self.result_info['userInfo']) )
            
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            return returnData
        except Exception:
            print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'getUSERINFO', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['status'] = 'false'
            returnData['success1'] = 'true'
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData 
    
    def doUpload(self):
        try:
            if self.result_info :
               
                print('-----------CTCC doUpload List------------')
                #合并userInfo到phoneInfo
                if self.result_info['userInfo']:
                    self.result_info['phoneInfo'] = dict(self.result_info['phoneInfo'], **self.result_info['userInfo'])
                
                self.isSuccess = CTCC.uploadData( self, self.result_info)
#                 print(self.result_info)
                print('-----------CTCC Successful List------------')
                if self.isSuccess :
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : 'success'
                    }
                    CTCC.uploadException(self, self.login_account, 'Upload Data', 'Upload Data Success')
                    CTCC.uploadException(self, self.login_account, 'Uploaded call', str(len(self.result_info['callDetail'])))
                    CTCC.uploadException(self, self.login_account, 'Uploaded sms', str(len(self.result_info['smsDetail'])))
                    CTCC.uploadException(self, self.login_account, 'Uploaded netDetail', str(len(self.result_info['netDetail'])))
#                     CTCC.uploadException(self, self.login_account, 'Uploaded data', str(self.result_info))
                    return returnData
                else:
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : 'false'
                    }
                    return returnData 
            else:
                CTCC.uploadException( self, username = self.login_account, step = 'doUpload', errmsg = 'result_info empty' )
                returnData = CTCC.init( self )
                returnData['msg'] = '统异常,请稍后重试,code:1005'
                return returnData   
        except Exception:
            CTCC.uploadException( self, username = self.login_account, step = 'doUpload', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData 
        
def header_map(headerstr):
    headers = {}
    hd = map(lambda x:x.split(':'),headerstr.split('\n'))
    hdlist = list(hd)
    hdlist
    for item in  hdlist:
        valuestr = ''
        for i in list(range(1,len(item))):
            valuestr = valuestr+item[i]
        headers[item[0]]= valuestr.strip(' ')
    return headers

def cookie_map(cookiestr):
    cookie = {}
    cookiedict = map(lambda x:x.split('='),cookiestr.split(';'))
    cookiedict = list(cookiedict)
    for item in  cookiedict:
        cookie[item[0].strip(' ')]= item[1]
    return cookie

def postdata_map(postdatastr):
    post_data = {}
    pd = map(lambda x:x.split('='),postdatastr.split('&'))
    pdlist = list(pd)
    if postdatastr[-1]=='&':
        pdlist.pop()
    for item in  pdlist:
        post_data[item[0]]= item[1]
    return post_data
    
