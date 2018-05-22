# -*- coding: utf-8 -*-
'''
@author: Jacklin
@Province: Hennan
'''
import json
import requests
from bs4 import BeautifulSoup
import base64
import re 
import datetime
import time
import traceback
from builtins import str


class CTCC() :
    '''中国电信爬虫-河南省
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

    ''''def doCapture(self, jsonParams):
        print('ctcc_hen-->doCapture...')
        try:
            jsonParams = json.loads(jsonParams, encoding='utf-8')
            self.jsonParams = jsonParams
            obj = {}
            obj["result"] = {}
            if 'step' in jsonParams.keys():
                step = jsonParams["step"]
            
            if('step' in jsonParams.keys()):
                if(jsonParams['step'] == '0'):
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
                    if 'loginname' in jsonParams.keys() and 'nloginpwd' in jsonParams.keys():
                        obj["result"]["username"] = jsonParams["loginname"]
                        obj["result"]["password"] = jsonParams["nloginpwd"]
                        
                elif(jsonParams['step'] == '1'):
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
                    if 'username' in jsonParams.keys() and 'nloginpwd' in jsonParams.keys():
                        obj["result"]["username"] = jsonParams["username"]
                        obj["result"]["password"] = jsonParams["randomPwd"]
            else:
                obj["result"] = jsonParams["result"]
                obj["result"]["username"] = jsonParams["result"]["username"]
                obj["result"]["password"] = jsonParams["result"]["randomPwd"]
            
            return self.checkLogin(self, obj)
        except Exception:
            print(traceback.format_exc())
            return jsonParams'''
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

            #print(jsonParams)
            #json.dumps(jsonParam)
            #
            jsonParams = json.loads(jsonParams, encoding='utf-8')
            self.jsonParams = jsonParams
#             print(self.jsonParams)
            
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
                self.havePiccode = False
                #if()
                if 'flowNo' in jsonParams.keys():
                    self.flowNo = jsonParams['flowNo']
                else:
                    self.flowNo = str(jsonParams["result"]["flowNo"])
                if setrandomFlag == "1":
                    self.randomFlag = "1"
                else:
                    self.randomFlag = "0"
                self.jsonParams = jsonParams
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
                self.result_info['ispProvince'] = '河南'
#                 self.result_info['operator'] = '河南电信'
                self.result_info['flow_no'] = self.flowNo
                self.result_info['createTime'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                
                self.mobile = obj["result"]["username"]
                self.UserId  = obj["result"]["username"]
                self.login_account = obj["result"]["username"]
                self.login_password = obj["result"]["password"]
                self.result_info["billDetail"] = []
                self.result_info["paymentRecord"] = []
                CTCC.uploadException(self, self.mobile, 'docapture1', 'init_' + str(self.login_password))
                    
                '''elif(self.step == '1'):
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
                    self.randomFlag = "1"
                    if 'username' in jsonParams.keys() and 'password' in jsonParams.keys():
                        obj["result"]["username"] = jsonParams["username"]
                        obj["result"]["password"] = jsonParams["randomPwd"]
                    elif 'result' in jsonParams.keys():
                        obj["result"]["username"] = jsonParams['result']["username"]
                        obj["result"]["password"] = jsonParams['result']["randomPwd"]'''
            
            elif(self.step == "3"):
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
                self.loginpiccode = piccode
                
            
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
                if 'smsPwd' in jsonParams.keys():
                    smsPwd = str(jsonParams["smsPwd"])
                elif 'smsPwd' in jsonParams["result"].keys():
                    smsPwd = str(jsonParams["result"]["smsPwd"])
                self.mobilecode = smsPwd
            
            return CTCC.checkLogin(self, obj)
        except Exception :
            print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'docapture', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
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
#             print('uploadData-->[post] ctcc_hen data to ' + self.crawlerServiceUrl)
            resp = requests.post(self.crawlerServiceUrl, headers = headers, data = {'content':json.dumps(postData, ensure_ascii=False)})
            respText = resp.text;
            #print(resp.text)
            respObj = json.loads(str(resp.text).strip(), encoding = 'utf-8')
            if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
                return True
            else:
                CTCC.uploadException(self, username=self.mobile, step='uploadData', errmsg=respText)
                return False
        except Exception:
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=self.mobile, step='uploadData', errmsg=respText)
            return False
   
        
    def uploadException(self, username = '', step = '', errmsg = ''):
        #上传异常信息
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'ctcc_hen','login_account':username}
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
            'password': password
        }
        resp = self.session.post(self.jiamiUrl, headers = jiamiUrl_headers, data = {'content':json.dumps(jiamiUrl_params,ensure_ascii=False)}, allow_redirects = True)
        #print('jiami post sucess'+str(resp.text))
        jiamiObj = json.loads(resp.text, encoding = 'utf-8')
        #print('jiamiObj=',jiamiObj,'\n')
        
        try:
            self.param['password'] = jiamiObj['password']
            
        except Exception:
            respText =  traceback.format_exc()
            print(respText)
            CTCC.uploadException(self, username=username, step='password encryption', errmsg=respText)
            data = {
                    'status':'true',
                    'step':'0',
                    'msg':'统异常,请稍后重试,code:1005',
                    'words':[
                                {'ID':'username','index': '0',  'label':'用户名', 'type': 'text'},
                                {'ID':'password','index': '1', 'label':'服务密码', 'type': 'password'}
                            ]
                }
            return data
        return self.param
            
    

    
    def checkLogin(self, obj):
        if (self.step == "3"):
            self.havePiccode = True
            obj['result']['step'] = "0"
            self.step == "0"
            
        if(obj['result']['step'] == "0"):
            if(self.havePiccode == False):
                userInfo = {}
                phoneInfo = {
                    "status":'OK',
                    "realMoney":'' ,
                    "serviceLevel": '',
                    "inNetDate": '',
                    "pointValue":'',
                    "totalCreditValue": '',
                    "balance": '',
                    "basicMonthFee":'',
                    "packageInfos":'' 
                  }
                self.result_info['phoneNum'] = self.login_account
                self.result_info['userInfo'] = userInfo
                self.result_info['phoneInfo'] = {}
    #             self.result_info['phoneInfo'] = phoneInfo
                resultObj ={
                        "step": "0",
                        "gostep":"",
                        "username": str(obj["result"]["username"]),
                        "password": str(obj["result"]["password"])
                    }
            
        
            if self.havePiccode == False and CTCC.getLoginCookies(self, obj) == False:
                resultObj['step'] = '3'
                resultObj['gostep'] = 'verifyCode'
                
                returnData = {
                        'status' : 'true',
                        'step' : '3',
                        'again' : 'true',
                        'msg': "",
                        'username': self.login_account,
                        'words': []
                    }
                if(self.imgbyteBase64Str != None):
                    returnData['words'] = [
                            {'ID' : 'piccode' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '请输入四位黑色验证码' , 'type' : 'piccode' , 'source' : self.imgbyteBase64Str }
                        ] 
                return returnData
            else:
                encry_obj = CTCC.passwordEncryption(self, str(self.login_account), str(obj["result"]["password"]))
                obj['result']['password'] = encry_obj["password"]
                if self.havePiccode == False:
                    loginData = CTCC.doLogin(self, obj, '0', '')
                else:
                    loginData = CTCC.doLogin(self, obj, '0', self.loginpiccode)
                
                if(loginData["result"] == "True"):
                    if( CTCC.goFrontPage(self) ):
                        if(self.productId != ''):
                            if( CTCC.getPhoneInfo(self,  obj) ):
                                data = CTCC.getUserInfo(self)
                                if( data["success1"] == 'true' ):
                                    #self.getBillingQuery(self, obj)
                                    data = CTCC.getUserBillDatas(self,  obj)
                                    return data
                                else:
#                                     returnData = CTCC.init( self )
                                    return data
                            else:
                                returnData = CTCC.init( self )
                                return returnData
                        #print(self.result_info)
                        else:
                            data = CTCC.init( self )
                            data["msg"] = '系统错误！ 请退出输入'
                        #print(data)
                        return data
                    else:
                        returnData = CTCC.init(self)
                        returnData['msg'] = ' 系统错误！ 请退出输入'
                        return returnData
                       
                else:
                    if('msg' in loginData):
                        loginData["msg"] = loginData["msg"] 
                    else:
                        loginData["msg"] = ''
                    CTCC.uploadException( self, username = self.login_account, step = 'doLogin logindata empty', errmsg = loginData["msg"] )
                    resultObj = CTCC.init( self )
                    resultObj["msg"] = loginData["msg"]
                    return resultObj
        
        elif (self.step == "2"):
            #self.mobilecode = obj['result']['smsPwd']
            
            return CTCC.getPhoneCallList(self)
        
       
            
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
            if(str(jsonRes["captchaFlag"]).lower() == "true"):
                self.imgbyteBase64Str = CTCC.getVerifyCode(self)
                return False
                
            return True
        except Exception :
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'getLoginCookies', errmsg = traceback.format_exc() )
            return False
        
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
                    'Proxy-Connection':'keep-alive'
#                     'Cookie': 'ECSLoginReq='+ self.session.cookies["ECSLoginReq"] + ';ECSLoginToken='+ self.session.cookies["ECSLoginToken"] 
                    #'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
                }
                getEcsresp = self.session.get(getEcsurl, headers = headerStr1, verify = True, allow_redirects = True, timeout = None)
               
                #time.sleep(10)
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
                        "msg":errorMsg,
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
#             print(traceback.format_exc())
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
#             print(self.session.cookies)
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
            CTCC.uploadException( self, username = self.login_account, step = 'doLogin', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['result'] = "False"
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
        
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
        
    def goFrontPage(self):
        try:
            time.sleep(2)
            billPageUrl = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000356'
            billFrontPageHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cookie': 'JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; aactgsh111220= '+ self.session.cookies["aactgsh111220"] +';SHOPID_COOKIEID=10017;isLogin = '+ self.session.cookies["isLogin"] + ';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; loginStatus=logined;',
                        'Host':'www.189.cn',
                        'Proxy-Connection':'keep-alive',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'python-requests/2.12.3'
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            billPageUrlresp = self.session.get(billPageUrl, headers = billFrontPageHeader, verify = False) 
#             print("billPageUrlresp CHECK")
            
            myWalletInfoHtml = BeautifulSoup(str(billPageUrlresp.text).strip(),'html.parser')

            TableTags1 = myWalletInfoHtml.findAll('th')
#             print(len(TableTags1))
            flag = False
            i = 0
            self.usrr_wallet = ''
            for row in TableTags1:
                identification = row.find(text = "积   分：")
                if (identification != None):
                    idval = str(TableTags1[i])
                    self.usrr_wallet = idval[ (idval.find("<span>")) + 6 : idval.rfind("</span>") ]
                    #print(self.usrr_wallet)
                
                   
                i += 1
            
            pointValue  = {"pointValue" : self.usrr_wallet}
            #self.result_info['phoneInfo'].append(pointValue)
            #self.result_info['phoneInfo']["pointValue"] = self.usrr_wallet
            
            getProductIDUrl = 'http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo='+ self.session.cookies["SHOPID_COOKIEID"] +'&toStUrl=http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha'
            productIDHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cache-Control':'max-age=0',
                        'Connection':'keep-alive',
                        'Cookie': 'JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +';aactgsh111220= '+ self.session.cookies["aactgsh111220"] +';SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=ha; loginStatus=logined;',
                        'Host':'www.189.cn',
                        'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000356',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'python-requests/2.12.3'
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            productIDresp = self.session.get(getProductIDUrl, headers = productIDHeader, verify = False) 
            #print(productIDresp.text)
            
            productResponseHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
#                         'Cookie': 'ECSLoginReq='+ self.session.cookies["ECSLoginReq"] +';ECSLoginToken='+ self.session.cookies["ECSLoginToken"] +';isLogin='+ self.session.cookies["isLogin"] +';aactgsh111220= '+ self.session.cookies["aactgsh111220"] +';SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=ha; loginStatus=logined;',
                        'Host':'login.189.cn',
                        'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000356',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'python-requests/2.12.3'
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            productIDresp1 = self.session.get(productIDresp.url, headers = productResponseHeader, verify = False) 
            print(productIDresp.url)
            #print(productIDresp1.text)
            productIDHTML = BeautifulSoup(productIDresp1.text,'html.parser')
            script = productIDHTML.find_all("script")
            #print(script)
            try:
                if( len(script) >= 15):
                    doQuery = str(script[15])
                    doQuery.strip()
                    self.productId = doQuery[(doQuery.find(",'")) + 2:doQuery.rfind("',")]
                else:
                    self.productId = ''
            except:
                self.productId = ''
                
                
            longDistanceUrl = 'http://ha.189.cn/service/iframe/bill/iframe_inxx.jsp'
            longDistanceHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'53',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha',
                    'User-Agent':'python-requests/2.12.3',
                    'X-Requested-With':'XMLHttpRequest',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';'
                }
            
            longDistance_post_data = {
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'ACCTNBR97':''
                }
            longDistanceResp = self.session.post(longDistanceUrl, data = longDistance_post_data, headers = longDistanceHeader, verify = False) 
            #print(longDistanceResp.text)
            strVal = str(longDistanceResp.text)
            searchstr = 'var operate_type = "'
            endStr = '";'
            start = strVal.find(searchstr)
            end = strVal.find( endStr , start)
            operate_type = strVal[start + len( searchstr ) : end]
            #print(operate_type)
            
            productIDHTML = BeautifulSoup(longDistanceResp.text,'html.parser')
            transaction_id = productIDHTML.find('input',{"id":"transaction_id"}).get('value')
            #print(transaction_id)
            
            livingbodyUrl = 'http://ha.189.cn/service/iframe/public/livingBodyCheck.jsp'
            headers = {
                    'Accept':'application/xml, text/xml, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.9',
                    'Connection':'keep-alive',
                    'Content-Length':'98',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            post_data = {
                'TRANSACTION_ID':str(transaction_id),
                'OPERATE_TYPE':str(operate_type),
                'ACC_NBR':str(self.login_account)
                }
            longDistanceResp = self.session.post(livingbodyUrl, data = post_data, headers = headers, verify = False) 
            
            url = 'http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp'
            frameHeader = {
                    'Accept':'text/html, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.9',
                    'Connection':'keep-alive',
                    'Content-Length':'175',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            postData = {
                    'ACC_NBR':str(self.login_account),
                    'PROD_TYPE':self.productId,
                    'BEGIN_DATE':'',
                    'END_DATE':'',
                    'SERV_NO':'',
                    'ValueType':'1',
                    'REFRESH_FLAG':'1',
                    'FIND_TYPE':'4',
                    'radioQryType':'on',
                    'QRY_FLAG':'1',
                    'ACCT_DATE':'201712',
                    'ACCT_DATE_1':'201801'
                }
            longDistanceResp = self.session.post(url, data = postData, headers = frameHeader, verify = False) 
            CTCC.uploadException( self, username = self.login_account, step = 'iframe_inxxall', errmsg = str(longDistanceResp.text) )
            #print(longDistanceResp.text)
            #pattern = re.compile("(\w+): '(.*?)'")
            #script1 = re.findall(pattern, doQury)
#             fields = dict(re.findall(pattern, doQuery))
           
#             print(self.productId)
#             pattern = re.compile("(\w+): '(.*?)'")
#             script = re.findall(pattern, string)
#             print(script)#, "doQuery"))
#             print(len(script))
#             for value in script:
#                 val = value.find("doQuery")
#                 print(val)
            
            return True
            
        except Exception :
#                 print(traceback.format_exc())
                CTCC.uploadException( self, username = self.login_account, step = 'doLogin', errmsg = traceback.format_exc() )
                returnData = CTCC.init( self )
                returnData['msg'] = '统异常,请稍后重试,code:1005'
                return False
            
        
        
    
    def getPhoneInfo(self, obj):
        try:
            time.sleep(1)
            billPageUrl = 'http://ha.189.cn/service/iframe/bill/iframe_sshf.jsp'
            billFrontPageHeader = {
                        'Accept':'*/*',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'53',
                        'Content-Type':'application/x-www-form-urlencoded',
                        'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +'; ',
                        'Host':'ha.189.cn',
                        'Origin':'http://ha.189.cn',
                        'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-8&fastcode=20000359&cityCode=ha',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest'
                }
            realMoney_postData = {
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'ACCTNBR97':''
                }
            billPageUrlresp = self.session.post(billPageUrl, data = realMoney_postData, headers = billFrontPageHeader, verify = False) 
            #print(billPageUrlresp.text)
            realMoneyInfoHtml = BeautifulSoup(str(billPageUrlresp.text).strip(),'html.parser')
    
            TableTags1 = realMoneyInfoHtml.findAll('td')
            #print(len(TableTags1))
            flag = False
            i = 0
            self.realMoney = "0"
            for row in TableTags1:
                identification = row.find(text = "语音通话费")
                if (identification != None):
                    idval = str(TableTags1[i+1])
                    self.realMoney = idval[ (idval.find("<td>")) + 4 : idval.rfind("</td>") ]
                    #print(self.realMoney)
                
                   
                i += 1
            self.realMoney = str(self.realMoney).replace('元', '')
            self.realMoney = str(int(float(self.realMoney) * 100)) 
            pointValue  = {"realMoney" : self.realMoney}
            #self.result_info['phoneInfo'].append(pointValue)
    #         self.result_info['phoneInfo']["realMoney"] = self.realMoney
            
            billPageUrl1 = 'http://ha.189.cn/service/iframe/bill/iframe_intc.jsp'
            billFrontPageHeader1 = {
                        'Accept':'*/*',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'53',
                        'Content-Type':'application/x-www-form-urlencoded',
                        'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +'; ',
                        'Host':'ha.189.cn',
                        'Origin':'http://ha.189.cn',
                        'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-8&fastcode=20000359&cityCode=ha',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest'
                }
            realMoney_postData1 = {
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'ACCTNBR97':''
                }
            billPageUrlresp1 = self.session.post(billPageUrl1, data = realMoney_postData1, headers = billFrontPageHeader1, verify = False) 
            #print(billPageUrlresp.text)
            packageInfoHtml = BeautifulSoup(str(billPageUrlresp1.text).strip(),'html.parser')
    
            TableTags1 = packageInfoHtml.findAll('tr')
            flag = False
            i = 0
            self.packageInfo = []
            packageArr = []
            packageObj = {}
            if(len(TableTags1) >= 4):
                packVal = str(TableTags1[3])
                packageValHtml = BeautifulSoup(str(packVal).strip(),'html.parser')
                #print(packageValHtml)
                packVals = packageValHtml.findAll("td")
                packageArr = []
                #for item in packVals:
                
                
                
                packageObj = {
                    "packageName": "",
                    "totalamountPackage": "",
                    "effectiveDate": "",
                    "ExpirationDate": ""
                    }
                if( len(packVals) > 0):
                    idval = str(packVals[0])
                    packageObj["packageName"] = idval[ (idval.find("<td>")) + 4 : idval.rfind("</td>") ]
                    idval = str(packVals[1])
                    totalamountPackage = str(idval[ (idval.find("<td>")) + 4 : idval.rfind("</td>") ]).strip()
            #         print("before: "+str(totalamountPackage))
            #         for character in totalamountPackage:  
            #             if character in string.ascii_letters:  
            #                 totalamountPackage = totalamountPackage.replace(character, "")  
            #         print("after: "+str(totalamountPackage))
                    packageObj["totalamountPackage"] = str(totalamountPackage)
                    idval = str(packVals[3])
                    effectiveDate = str(idval[ (idval.find("<td>")) + 4 : idval.rfind("</td>") ]).strip()
            #         for character in effectiveDate:  
            #             if character in string.ascii_letters:  
            #                 effectiveDate = effectiveDate.replace(character, "")  
                    packageObj["effectiveDate"] = effectiveDate
                    idval = str(packVals[4])
                    ExpirationDate = str(idval[ (idval.find("<td>")) + 4 : idval.rfind("</td>") ]).strip()
            #         for character in ExpirationDate:  
            #             if character in string.ascii_letters:  
            #                 ExpirationDate = ExpirationDate.replace(character, "")  
                    packageObj["ExpirationDate"] =  ExpirationDate
                
                #print(packageArr)
                
            packageArr.append(packageObj)
    #         self.result_info['phoneInfo']["packageInfos"] = packageArr
            
            CTCC.getBalanceQuery(self, obj)
            return True
        except Exception :
#                 print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'getPhoneInfo', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return False
        
        
    def sendMobileSMS(self, obj):
        try:
            time.sleep(2)
            ''''''
            
            queryPageUrl = 'http://ha.189.cn/service/bill/getRand.jsp'
            queryPageHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cookie': 'JSESSIONID='+ self.session.cookies["JSESSIONID"] +';JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; loginStatus=logined;',
                        'Host':'www.189.cn',
                        'Proxy-Connection':'keep-alive',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent' : 'python-requests/2.12.3'
                        #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            sms_data = {
                'PRODTYPE':self.productId,
                'RAND_TYPE':'002',
                'BureauCode':self.AreaCode,
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'PROD_PWD':'',
                'REFRESH_FLAG':'1',
                'BEGIN_DATE':'',
                'END_DATE':'',
                'ACCT_DATE':'201701',
                'FIND_TYPE':'4',
                'SERV_NO':'',
                'QRY_FLAG':'1',
                'ValueType':'4',
                'MOBILE_NAME':str(self.login_account),
                'OPER_TYPE':'CR1',
                'PASSWORD':''
                }
            queryPageUrlresp = self.session.post(queryPageUrl, data = sms_data, headers = queryPageHeader, verify = False) 
            #print(queryPageUrlresp.text)
           
            smsHtml = BeautifulSoup(queryPageUrlresp.text,'html.parser')
            smsResult = smsHtml.find('flag').text
            if(str(smsResult) == "0"):
                data = {
                    'status' : 'true',
                    'step' : '2',
                    'again' : 'true',
                    'msg': '请输入短信验证码',
                    'username': self.login_account,
                    'words' : [
                            {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                        ]
                }
            elif (str(smsResult) == "-196910"):
                '''data = {
                    'status' : 'true',
                    'step' : '0',
                    'again' : 'true',
                    'msg': smsHtml.find('msg').text,
                    'words' : [
                            {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                        ]
                }'''
                data = CTCC.init( self )        
                data['msg'] = smsHtml.find('msg').text
            else:
                CTCC.uploadException( self, username = self.login_account, step = 'sendSMSpwd', errmsg = queryPageUrlresp.text)
                returnData = CTCC.init( self )
                returnData['msg'] = smsHtml.find('msg').text
                return returnData
                '''data = {
                    'status' : 'true',
                    'step' : '2',
                    'again' : 'true',
                    'msg':'服务密码或短信验证码错误',
                    'words' : [
                            {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                        ]
                }'''
            #print(data)
            return data
        except Exception :
                respText = traceback.format_exc()
                #print(respText)
                CTCC.uploadException( self, username = self.login_account, step = '2', errmsg = respText)
                returnData = CTCC.init( self )
                returnData['msg'] = '系统异常,请稍后重试,code:1005'
                return returnData
                
    def getUserBillDatas(self, obj):
        try:
            time.sleep(1)
            #闀块�旀竻鍗� (LongDistance List)
            longDistanceUrl = 'http://ha.189.cn/service/iframe/bill/iframe_inxx.jsp'
            longDistanceHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'53',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha',
                    'User-Agent':'python-requests/2.12.3',
                    'X-Requested-With':'XMLHttpRequest',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';'
                }
            
            longDistance_post_data = {
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'ACCTNBR97':''
                }
            longDistanceResp = self.session.post(longDistanceUrl, data = longDistance_post_data, headers = longDistanceHeader, verify = False) 
            #print(longDistanceResp.text)
            
            longDistanceRespHtml = BeautifulSoup(longDistanceResp.text,'html.parser')
            monthListTags = longDistanceRespHtml.findAll('select',{"id":"ACCT_DATE"})
            monthselect = BeautifulSoup(str(monthListTags[0]),'html.parser')
            self.monthArray = []
            for option in monthselect.find_all('option'):
                self.monthArray.append(option['value'])
            #print(self.monthArray)
            
            FIND_TYPE_Tags = longDistanceRespHtml.findAll('select',{"id":"FIND_TYPE"})
            typeselect = BeautifulSoup(str(FIND_TYPE_Tags[0]),'html.parser')
            self.findtypeArray = []
            for option1 in typeselect.find_all('option'):
                self.findtypeArray.append(option1['value'])
            #print(self.findtypeArray)
            
            CTCC.uploadException(self, self.login_account, 'typeselect', str(typeselect))
            return CTCC.sendMobileSMS(self, obj)
        except Exception :
            respText = traceback.format_exc()
            #print(respText)
            CTCC.uploadException( self, username = self.login_account, step = '2', errmsg = respText)
            returnData = CTCC.init( self )
            returnData['msg'] = '系统异常,请稍后重试,code:1005'
            return returnData
        
        
        #mobilecode = raw_input("Mobile Code: ")
        
        
    def getPhoneCallList(self):
        try:
            longDistanceUrl1 = 'http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp'
            longDistanceHeader1 = {
                    'Accept':'text/html, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'256',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha',
                    'User-Agent':'python-requests/2.12.3',
                    'X-Requested-With':'XMLHttpRequest'
                }
            
            longDistance_post_data1 = {
                'PRODTYPE':self.productId,
                'RAND_TYPE':'002',
                'BureauCode':self.AreaCode,
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'PROD_PWD':'',
                'REFRESH_FLAG':'1',
                'BEGIN_DATE':'',
                'END_DATE':'',
                'ACCT_DATE': str(self.monthArray[0]),
                'FIND_TYPE': '4',#str(self.findtypeArray[2]),
                'SERV_NO':'',
                'QRY_FLAG':'1',
                'ValueType':'4',
                'MOBILE_NAME':str(self.login_account),
                'OPER_TYPE':'CR1',
                'PASSWORD':self.mobilecode
                }
            longDistanceResp1 = self.session.post(longDistanceUrl1, data = longDistance_post_data1, headers = longDistanceHeader1, verify = False) 
            
            #print(longDistanceResp1.text)
            longDistanceHtml = BeautifulSoup(longDistanceResp1.text,'html.parser')
            TableTags = longDistanceHtml.findAll('tbody')
            internetDetailArr = []
            try:
                trVal = TableTags[0].findAll('tr') 
                #print(TableTags)
                
                for tr in trVal:
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        netDate = td[1].text[0:8]
                        netMoney = td[5].text 
                        netFlow  = td[7].text 
                        if(netMoney != '' and netMoney != None):
                            netMoney = str(float(netMoney) * 100)
                            
                        GB = re.findall(re.compile(r'(\d*)GB'),netFlow)
                        MB = re.findall(re.compile(r'(\d*)MB'),netFlow)
                        KB = re.findall(re.compile(r'(\d*)KB'),netFlow)
                        
                        if( len(GB) == 0 and len(MB) == 0 and len(KB) == 0):
                            netTraffic = netFlow
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
                        
                        internetDetailArr.append(
                            {
                                
                                "netType": td[4].text ,
                                "startTime": td[1].text,
                                "totalTime": td[3].text ,
                                "totalFee": netMoney,
                                "totalTraffic": str(netTraffic),
                                "netPlace":""
                            })
            except Exception:
                CTCC.uploadException(self, self.login_account, 'internetDetailArr', str(longDistanceResp1.text))
                respText = traceback.format_exc()
                
                CTCC.uploadException( self, username = self.login_account, step = 'check sms fail', errmsg = respText)
                returnData = CTCC.init( self )
                returnData['msg'] = '短信密码验证失败,code:1005'
                return returnData
                    
            #print(self.session.cookies)
            
            #For 6 months Data
            for val in range(1, len(self.monthArray)):
                longDistance_post_data1 = {
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'BEGIN_DATE':'',
                'END_DATE':'',
                'ValueType':'4',
                'REFRESH_FLAG':'1',
                'FIND_TYPE': '4', #str(self.findtypeArray[2]),
                'radioQryType':'on',
                'QRY_FLAG':'1',
                'ACCT_DATE':str(self.monthArray[val]),
                'ACCT_DATE_1':str(self.monthArray[val-1])
                }
                #print(str(self.monthArray[val]))
                longDistanceResp1 = self.session.post(longDistanceUrl1, data = longDistance_post_data1, headers = longDistanceHeader1, verify = False) 
    #             print("http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp "+str(self.monthArray[val]))
                #print(longDistanceResp1.text)
                longDistanceHtml1 = BeautifulSoup(longDistanceResp1.text,'html.parser')
                TableTags1 = longDistanceHtml1.findAll('tbody')
                #print(TableTags1)
                arr = longDistanceHtml1.findAll('tbody')
                if(len(arr) != 0):
                    try:
                        for tr in longDistanceHtml1.findAll('tbody')[0].findAll('tr'):
                            netMoney = '0'
                            trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                            td = trTD.findAll('td')
                            netDate = td[1].text[0:8]
                            netMoney = td[5].text 
                            netFlow  = td[7].text 
                            if(netMoney != '' and netMoney != None):
                                netMoney = str(int(float(netMoney) * 100)) 
                                
                            GB = re.findall(re.compile(r'(\d*)GB'),netFlow)
                            MB = re.findall(re.compile(r'(\d*)MB'),netFlow)
                            KB = re.findall(re.compile(r'(\d*)KB'),netFlow)
                            
                            if( len(GB) == 0 and len(MB) == 0 and len(KB) == 0):
                                netTraffic = netFlow
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
                            
                            internetDetailArr.append(
                                {
                                    "netType": td[4].text ,
                                    "startTime": td[1].text,
                                    "totalTime": td[3].text ,
                                    "totalFee": netMoney,
                                    "totalTraffic": str(netTraffic),
                                    "netPlace":""
                                    
                                })
                    except Exception:
                        CTCC.uploadException(self, self.login_account, '1 internetDetailArr', str(longDistanceResp1.text))
                   
                self.result_info['netDetail'] = internetDetailArr
                    
            
            
            
            #Getting Telephone DataList 
            teleHeader1 = {
                    'Accept':'text/html, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'166',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-2&fastcode=20000356&cityCode=ha',
                    'User-Agent':'python-requests/2.12.3',
                    'X-Requested-With':'XMLHttpRequest'
                }
            phoneDetailArr = []
            messageDetailArr = []
            for val in range(0, len(self.monthArray)):
                tele_post_data1 = {
                    'ACC_NBR':str(self.login_account),
                    'PROD_TYPE':self.productId,
                    'BEGIN_DATE':'',
                    'END_DATE':'',
                    'ValueType':'4',
                    'REFRESH_FLAG':'1',
                    'FIND_TYPE': '1',#str(self.findtypeArray[1]),
                    'radioQryType':'on',
                    'QRY_FLAG':'1',
                    'ACCT_DATE':str(self.monthArray[val]),
                    'ACCT_DATE_1':str(self.monthArray[val-1])
                    }
                telephoneDataResp1 = self.session.post(longDistanceUrl1, data = tele_post_data1, headers = teleHeader1, verify = False) 
    #             print("http://ha.189.cn/service/iframe/bill/iframe_inxxall.jsp "+str(self.monthArray[val])+ " TYpe:: "+str(self.findtypeArray[1]))
                #print(telephoneDataResp1.text)
                telephoneDataHtml1 = BeautifulSoup(telephoneDataResp1.text,'html.parser')
                #TableTags2 = telephoneDataHtml1.findAll('table', {"id": "listQry"})
                TableTags2 = telephoneDataHtml1.findAll('tbody')
                #print(TableTags2)
                
                try:
                    for tr in telephoneDataHtml1.findAll('tbody')[0].findAll('tr'):
                        trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                        td = trTD.findAll('td')
                        i = 0
                        callType  = td[5].text
                        commTotalTime = td[4].text 
                        
                        if( commTotalTime.find(':') != -1):
                            commTotalTimeArr = commTotalTime.split(':')
                            hours = commTotalTimeArr[0]
                            minis = commTotalTimeArr[1]
                            secs = commTotalTimeArr[2]
                            commTotalTime = str((int(hours) * 3600) + (int(minis) * 60) + int(secs))
                            
                            
                        cost  = td[6].text 
                        commDate =  td[2].text[0:8]
                        commDate = commDate.replace(':','')
                        commTime =  td[2].text[8:len(td[2].text)]
                        commTime = commTime.replace(':', '')
                        if(callType == "主叫"):
                            commPhoneNo = td[1].text[0:11]
                        elif(callType == "被叫"):
                            commPhoneNo = td[0].text
                        else:
                            commPhoneNo = td[0].text
                            
                        '''endDatestr = time.strptime(commDate.strip(),"%Y-%m-%d")
                        commDate = time.strftime("%Y%m%d",endDatestr)
                        
                        endDatestr = time.strptime(commTime.strip(),"%H:%M:%S")
                        commTime = time.strftime("%H%M%S",endDatestr)'''
                            
                            
                        if(cost != '' and cost != None):
                            cost = str(int(float(cost) * 100)) 
                        
                        phoneDetailArr.append(
                            {
                                "callTypeName": str(callType).strip(),
                                "callPlace":"",
                                "otherPhoneNum": str(commPhoneNo).strip(),
                                "startDate": commDate,
                                "startTime": commTime,
                                "totalTime": commTotalTime,
                                "totalFee":  str(cost).strip()
                            })
                except Exception:
                    respText = traceback.format_exc()
#                     print(respText)
                    CTCC.uploadException( self, username = self.login_account, step = 'phoneDetailArr', errmsg = respText)
                    CTCC.uploadException( self, username = self.login_account, step = 'phoneDetailArr', errmsg = str(telephoneDataHtml1))
                    
                self.result_info['callDetail'] = phoneDetailArr
                
                message_post_data1 = {
                    'ACC_NBR':str(self.login_account),
                    'PROD_TYPE':self.productId,
                    'BEGIN_DATE':'',
                    'END_DATE':'',
                    'ValueType':'4',
                    'REFRESH_FLAG':'1',
                    'FIND_TYPE': '5',#str(self.findtypeArray[3]),
                    'radioQryType':'on',
                    'QRY_FLAG':'1',
                    'ACCT_DATE':str(self.monthArray[val]),
                    'ACCT_DATE_1':str(self.monthArray[val-1])
                    }
                messageDataResp1 = self.session.post(longDistanceUrl1, data = message_post_data1, headers = teleHeader1, verify = False) 
                
                messageDataHtml1 = BeautifulSoup(messageDataResp1.text,'html.parser')
                try:
                    for tr1 in messageDataHtml1.findAll('tbody')[0].findAll('tr'):
                        trTD1 = BeautifulSoup(str(tr1).strip(),'html.parser')
                        td = trTD1.findAll('td')
                        msgDate = td[2].text[0:8]
                        smsTime = td[2].text[8:len(td[2].text)]
                        msgPhone = td[1].text[0:11]
                        sendType = td[3].text 
                        cost  =  td[4].text
                        
                        #endDatestr = time.strptime(msgDate.strip(),"%Y-%m-%d")
                        #msgDate = time.strftime("%Y%m%d",endDatestr)
                        
                        #endDatestr = time.strptime(commTime.strip(),"%H:%M:%S")
                        #commTime = time.strftime("%H%M%S",endDatestr)
                        if(cost != '' and cost != None):
                            cost = str(int(float(cost) * 100) )
                        messageDetailArr.append(
                            {
                                "smsType": str(sendType),
                                "otherPhoneNum": str(msgPhone),
                                "smsDate": msgDate,
                                "smsTime": smsTime,
                                "totalFee": str(cost),
                                "place":""
                            })
                except Exception:
                    respText = traceback.format_exc()
                    #print(respText)
                    CTCC.uploadException( self, username = self.login_account, step = 'messageDetailArr', errmsg = respText)
                    CTCC.uploadException( self, username = self.login_account, step = 'messageDetailArr', errmsg = str(messageDataHtml1))
                    
                
                
                #print(phoneDetailArr)
                self.result_info['smsDetail'] = messageDetailArr
            print('-----------CTCC Successful List------------')
            #print(self.result_info)       
            isSuccess = CTCC.uploadData(self, self.result_info)    
            if isSuccess :
                returnData = { 
                    'status' : 'true' ,
                    'again' : 'false' ,
                    'msg' : 'success'
                }
                CTCC.uploadException(self, self.login_account, 'Upload Data', 'Upload Data Success')
                CTCC.uploadException(self, self.login_account, 'Uploaded call', str(len(self.result_info['callDetail'])))
                CTCC.uploadException(self, self.login_account, 'Uploaded sms', str(len(self.result_info['smsDetail'])))
                CTCC.uploadException(self, self.login_account, 'Uploaded netDetail', str(len(self.result_info['netDetail'])))
                return returnData
            else:
                returnData = { 
                    'status' : 'false' ,
                    'again' : 'false' ,
                    'msg' : 'false'
                }
                return returnData
        except Exception:
            respText = traceback.format_exc()
            print(respText)
            CTCC.uploadException( self, username = self.login_account, step = '2', errmsg = respText)
            returnData = CTCC.init( self )
            returnData['msg'] = '系统异常,请稍后重试,code:1005'
            return returnData
        
    def getBalanceQuery(self, obj):
        try:
            balanceQueryUrl = "http://ha.189.cn/service/iframe/bill/iframe_ye.jsp"
            balanceQueryHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'53',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +';',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/iframe/feeQuery_iframe.jsp?SERV_NO=FSE-2-1&fastcode=20000354&cityCode=ha',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            datas = {
                'ACC_NBR':str(self.login_account),
                'PROD_TYPE':self.productId,
                'ACCTNBR97':''
                }
            balanceQueryResp = self.session.post(balanceQueryUrl, data = datas, headers = balanceQueryHeader, verify = False) 
            #print(balanceQueryResp.text)
           
            self.balance = "0"
            balanceQueryRespHtml = BeautifulSoup(balanceQueryResp.text,'html.parser')
            try:
                TableTags = balanceQueryRespHtml.findAll('span',{"class":"sum"})
                balanceSpan = str(TableTags[1])
                #print(TableTags)
                getWord = '<span class="sum">'
                self.balance = balanceSpan[ (balanceSpan.find(getWord)) + len(getWord) : balanceSpan.rfind("</span>") ]
                #print(self.balance)
                balanceObj = {"balance": self.balance}
                self.balance = str(int(float(self.balance) * 100)) 
            except Exception:            #         monthArray = []
                #self.result_info['phoneInfo']["balance"] = ''
                respText = str(balanceQueryResp.text) + '_' + traceback.format_exc()
                CTCC.uploadException( self, username = self.login_account, step = 'balanceSpan', errmsg = respText)
            #self.result_info['phoneInfo'].append(balanceObj)
    #         self.result_info['phoneInfo']["balance"] = self.balance
    #         monthselect = BeautifulSoup(str(monthListTags[0]),'html.parser')
    #         monthArray = []
    #         for option in monthselect.find_all('option'):
    #             monthArray.append(option['value'])
            
            
            #print(self.session.cookies)
        except Exception :
            respText = traceback.format_exc()
            #print(respText)
            CTCC.uploadException( self, username = self.login_account, step = '2', errmsg = respText)
            returnData = CTCC.init( self )
            returnData['msg'] = '系统异常,请稍后重试,code:1005'
        
    
    
    def getUserInfo(self):
        try:
            mySelfInfoUrl = 'http://ha.189.cn/service/iframe/manage/my_selfinfo_iframe.jsp?fastcode=20000374&cityCode=ha'
            mySelfInfoHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +'; ',
                    'Host':'ha.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=20000374',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            mySelfInfo_PostData = {
                    'fastcode':'20000374',
                    'cityCode':'ha'
                }
            mySelfInfoResp = self.session.get(mySelfInfoUrl, data = mySelfInfo_PostData, headers = mySelfInfoHeader, verify = False) 
            #print(mySelfInfoResp.text)
            myselfInfoHtml = BeautifulSoup(str(mySelfInfoResp.text).strip(),'html.parser')
            self.idValue = ''
            custAddr = ''
            self.customerName = ''
            email = ''
            try:
                try:
                    custAddr = myselfInfoHtml.find_all("input", id="CustAddress")
                    custAddr = custAddr[0]['value']
                    
                    RelaEmail = myselfInfoHtml.find_all("input", id="RelaEmail")
                    email = RelaEmail[0]['value']
                except:
                    respText = str(mySelfInfoResp.text) + '_' + traceback.format_exc()
                    CTCC.uploadException( self, username = self.login_account, step = 'address and email', errmsg = respText)
                #print(custAddr)
                #print(custAddr[0]['value'])
                
                TableTags1 = myselfInfoHtml.findAll('td')
                flag = False
                i = 0
                for row in TableTags1:
                    identification = row.find(text = "证件号码：")
                    customerNameVal = row.find(text = "客户名称：")
                    if (identification != None):
                        idval = str(TableTags1[i+1])
                        self.idValue = idval[ (idval.find("<td>")) + 4 : idval.rfind("</td>") ]
                    #print(self.idValue)
                    if (customerNameVal != None):
                        custval = str(TableTags1[i+1])
                        self.customerName = custval[ (custval.find("<td>")) + 4 : custval.rfind("</td>") ]
                    #print(self.customerName)
                       
                    i += 1
            except:
                respText = str(mySelfInfoResp.text) + '_' + traceback.format_exc()
                CTCC.uploadException( self, username = self.login_account, step = 'userInfo', errmsg = respText)
                
            #identification = str(TableTags1.findAll('证件号码：')).strip()
            #.find_next_sibling("td").text
            userInfo = {
                    "certNum" : self.idValue,
                    "address" : str(custAddr),
                    "name": self.customerName,
                    "email" : email,
                    "certType":"",
                    "inNetDate":""
                }
            
            self.result_info['userInfo'] = userInfo
            self.result_info["userInfo"]["balance"] = self.balance
            self.result_info["userInfo"]["oweFee"] = self.realMoney
            self.result_info["userInfo"]["status"] = "0"
            
            #payment Record
            todayDate = datetime.date.today()
            prev_six_month = (datetime.date.today() + datetime.timedelta((-6)*365/12))
            paymentUrl = "http://ha.189.cn/service/pay/khxxgl/myserv_snList.jsp"
            pay_postData = {
                    'REFRESH_FLAG':'2',
                    'IPAGE_INDEX':'1',
                    'ASK_TYPE':'100',
                    'SERV_TYPE1':'',
                    'AREACODE':self.AreaCode,#'0371'
                    'SERV_NO1':'',
                    'OPEN_TYPE':'',
                    'START_ASK_DATE':str(prev_six_month),
                    'END_ASK_DATE': str(todayDate),
                    'STATE':'ALL'
                }
            paymentHeaderStr = {
                    'Accept':'text/html, */*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'148',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+ self.session.cookies["userId"] +'; isLogin='+ self.session.cookies["isLogin"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=ha; SHOPID_COOKIEID='+ self.session.cookies["SHOPID_COOKIEID"] +'; JSESSIONID='+ self.session.cookies["JSESSIONID"] +'; BIGipServerwt_fore_pl='+ self.session.cookies["BIGipServerwt_fore_pl"] +'; ',
                    'Host':'ha.189.cn',
                    'Origin':'http://ha.189.cn',
                    'Referer':'http://ha.189.cn/service/pay/',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            
            paymentResp = self.session.post(paymentUrl, data = pay_postData, headers = paymentHeaderStr, verify = False) 
            paymentHtml = BeautifulSoup(paymentResp.text,'html.parser')
            paymentHtml = paymentHtml.findAll('tbody')
            trVal = paymentHtml[0].findAll('tr') 
            paymentRecordArr = []
            for tr in trVal:
                    trTD = BeautifulSoup(str(tr).strip(),'html.parser')
                    td = trTD.findAll('td')
                    payDate  = td[3].text[0:10]
                    payFee  = td[2].text 
                    payChannel   = td[1].text 
                    
                    pattern = re .compile(r'\-.*\-')
                    tmpval = re.findall(pattern, str(td[3].text))
#                     print(tmpval)
                    if tmpval and len(tmpval) > 0:
                        endDatestr = time.strptime(payDate.strip(),"%Y-%m-%d")
                        payDate = time.strftime("%Y%m%d",endDatestr)
                        
                        billTime = td[3].text[10:len(td[3].text)]
                        endDatestr = time.strptime(billTime.strip(),"%H:%M:%S")
                        billTime = time.strftime("%H%M%S",endDatestr)
                    else:
                        payDate =  td[3].text[0:8]
                        billTime = td[3].text[8:len(td[3].text)]
                    
                    if(payFee != '' and payFee!= None):
                        payFee = str(int(float(payFee)) * 100)
                            
                    paymentRecordArr.append(
                        {
                            "billDate": payDate,
                            "billTime": billTime,
                            "billFee": str(payFee),
                            "busiName": str(payChannel)
                        })
            
            self.result_info['billDetail'] = paymentRecordArr
    
    #         print("SELF INFO END")
            #print(self.session.cookies)
            returnData = {
                    'status' : 'true' ,
                    'success1': 'true',
                    'msg' : ''
                }
            return returnData
        except Exception:
            respText = traceback.format_exc()
            CTCC.uploadException( self, username = self.login_account, step = '2', errmsg = respText)
            returnData = CTCC.init( self )
            returnData['success1'] =  'false'
            returnData['msg'] = '系统异常,请稍后重试,code:1005'
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
    
