# -*- coding: utf-8 -*-
'''
@author: Jacklin
'''
import json
import requests
from bs4 import BeautifulSoup
import re 
import datetime
import time
import traceback
from builtins import str
import calendar
import base64

class CTCC() :
    '''中国电信爬虫-江苏省
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
    
    def init(self, params = None) :
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
        respText = ''
        try:
            self.session = requests.session()
            self.login_account = ''
        
            result = {
                'status':'true',
                'again':'true',
                'step':'0',
                'msg':'需要初始化',
                'words':[
                    {'ID':'username','index': 0,'needUserInput':'true', 'label':'手机号码', 'type': 'text'},
                    {'ID':'password','index': 1,'needUserInput':'true', 'label':'服务密码', 'type': 'password'}
                ]
            }
            return result
        except Exception :
            CTCC.uploadException(self , username = '' , step = 'init' , errmsg = respText)
            returnData = {
                'status' : 'false',
                'again' : 'true',
                'msg' : '系统异常，请稍后重试,code:1000',
                'words':[
                    {'ID' : 'mobile' , 'index' : '0' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '移动手机号码' , 'type' : 'text'}
                ]
            }
            return returnData

    #上传数据到服务器
    def uploadData(self, data):
        #print(data)
        try:
            trycount = 0
            resultFlag = False
            while(trycount < 3 and resultFlag == False):
                trycount += 1
                headers = {
                    'Accept':'*/*',
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
                }
                postData = {
                    'heade':{'code':'uploadIspData','token':'','timestamp':''},
                    'body':{
                        'attach':'',
                        'content':data
                    }
                }
    #             print('uploadData-->[post] ctcc_js data to ' + self.crawlerServiceUrl)
                resp = requests.post(self.crawlerServiceUrl, headers = headers, data = {'content':json.dumps(postData, ensure_ascii=False)})
                respText = resp.text;
                #print(resp.text)
                respObj = json.loads(str(resp.text).strip(), encoding = 'utf-8')
                if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
                    resultFlag = True
                    
                else :
                    CTCC.uploadException(self, username=self.username, step=str(trycount) + '_uploadData', errmsg=respText)
                    resultFlag = False
            
            return resultFlag
                   

        except Exception:
#             print('uploadData-->[post] ctcc_js data error, ' + self.crawlerServiceUrl)
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=str(self.username), step=str(trycount) + '_uploadData', errmsg=respText)
            return False
   
    #上传异常信息
    def uploadException(self, username = '', step = '', errmsg = ''):
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'ctcc_js','login_account':username}
        try:
            if '192.168.1.82' not in self.uploadExceptionUrl:
                requests.post(self.uploadExceptionUrl, headers = headers, data = {'content':json.dumps(data, ensure_ascii=False)})
        except:
            print('uploadException-->[post] exception error')

    
    def passwordEncryption(self, username, password):
        jiamiUrl_headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
        }
        jiamiUrl_params = {
            'ctrlType':'CTCC',
            'password': password,
            'loginInfo': self.loginInfo
        }
        
        try:
            resp = self.session.post(self.jiamiUrl, headers = jiamiUrl_headers, data = {'content':json.dumps(jiamiUrl_params,ensure_ascii=False)}, allow_redirects = True)
            #print('jiami post sucess'+str(resp.text))
            jiamiObj = json.loads(resp.text, encoding = 'utf-8')
            
            self.param['password'] = jiamiObj['password']
            self.password = jiamiObj['password']
            self.ECS_ReqInfo_login1 = jiamiObj['loginInfo']
            
        except Exception:
            respText = respText = traceback.format_exc()
            CTCC.uploadException(self, username=str(self.username), step='5', errmsg=respText)
            data = {
                    'status':'true',
                    'step':'0',
                    'msg':'系统错误！请重试',
                    'words':[
                                {'ID':'username','index': '0',  'label':'手机号码', 'type': 'text'},
                                {'ID':'password','index': '1', 'label':'服务密码', 'type': 'password'}
                            ]
                }
            
        return self.param
            
    def doCapture(self, jsonParams):
        try:
            return CTCC.doCapture1(self,jsonParams)
        except:
            respText = 'Code_000 except:'+traceback.format_exc()
            #print(respText)
            CTCC.uploadException(self, self.username, 'doCapture', respText)
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
            jsonParams = json.loads(jsonParams, encoding='utf-8')
#             print("DO capture")

            self.jsonParams = jsonParams
            self.debug = False
            self.havePiccode = False
            if 'debug1' in jsonParams.keys():
                self.debug = True
            if 'step' in jsonParams.keys():
                step = jsonParams["step"]
            else:
                step = str(jsonParams["result"]["step"])
                obj = {"result":jsonParams["result"]}
                '''jsonParams["username"] = jsonParams["result"]["username"]
                jsonParams["password"] = jsonParams["result"]["password"]'''
#             print(step)
            if(step == "2"):
                self.havePiccode = True
                piccode = ''
                obj = {
                        "result" : {
                            'status':'true',
                            'again':'true',
                            'step':step,
                            'username':self.username,
                            'password':self.Oldpassword,
                            'gostep':''
                        }
                      }
                piccode = ''
                if 'piccode' in jsonParams.keys():
                    piccode = str(jsonParams["piccode"])
                elif 'piccode' in jsonParams["result"].keys():
                    piccode = str(jsonParams["result"]["piccode"])
                self.piccode = piccode
                print(self.piccode)
                step = '0'
                
            if(step == "3"):
                obj = {
                        "result" : {
                            'status':'true',
                            'again':'true',
                            'step':step,
                            'username':self.username,
                            'password':self.Oldpassword,
                            'gostep':''
                        }
                      }
                jspiccode = ''
                if 'jspiccode' in jsonParams.keys():
                    jspiccode = str(jsonParams["jspiccode"])
                elif 'jspiccode' in jsonParams["result"].keys():
                    piccode = str(jsonParams["result"]["jspiccode"])
                self.jspiccode = jspiccode
                print(self.jspiccode)
                CTCC.uploadException(self, username=str(self.username), step='self.jspiccode', errmsg=str(self.jspiccode))
                
                loginData = CTCC.doJsLogin(self, obj)
                if(loginData['result'] == 'True'):
                    data = CTCC.sendAndCheckMblCode(self, obj)
                    return data
                else:
                    return loginData
                
                
            if(step == "0"):
                if(self.havePiccode == False):
                
                    
                    if 'flowNo' in jsonParams.keys():
                        self.flowNo = jsonParams['flowNo']
                    else:
                        self.flowNo = str(jsonParams["result"]["flowNo"])
    #                 print(jsonParams)
                    self.param = {
                            'username': jsonParams["username"],
                            'password': jsonParams["password"]
                        }
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
                    obj["result"]["username"] = jsonParams["username"]
                    obj["result"]["password"] = jsonParams["password"]
                    self.username = obj["result"]["username"]
                    self.password = obj["result"]["password"]
                    self.Oldpassword = obj["result"]["password"]
                    self.login_account = self.username
                    CTCC.uploadException(self, self.username, 'docapture1', 'init_' + self.password)
                    self.loginCount = 0
                    if CTCC.getLoginAjax(self) == False:
                        
                        
                        returnData = {
                                'status' : 'true',
                                'step' : '2',
                                'again' : 'true',
                                'msg': "",
                                'username': self.username,
                                'words': [{'ID':'username','index': 0,'needUserInput':'true', 'label':'手机号码', 'type': 'text'},
                                          {'ID':'password','index': 1,'needUserInput':'true', 'label':'服务密码', 'type': 'password'}]
                            }
                        if(self.imgbyteBase64Str != None):
                            returnData['words'] = []
                            returnData['words'] = [
                                    {'ID' : 'piccode' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '请输入四位黑色验证码' , 'type' : 'piccode' , 'source' : self.imgbyteBase64Str }
                                ] 
                        return returnData
                    else:
                        loginData = CTCC.doLogin(self, obj)
                else:
                    loginData = CTCC.doLogin(self, obj)
                    
                    
                if(loginData["result"] == "True"):
                    logincheckUrl = 'http://js.189.cn/user_getSessionInfoforCookie.action'
                    loginCheckHeader = {
                                'Accept':'application/json, text/javascript, */*; q=0.01',
                                'Accept-Encoding':'gzip, deflate',
                                'Accept-Language':'zh-CN,zh;q=0.8',
                                'Content-Length':'0',
                                'Host':'js.189.cn',
                                'Origin':'http://www.189.cn',
                                'Connection':'keep-alive',
                                #'Proxy-Connection':'keep-alive',
                                'Referer':'http://www.189.cn/js/',
                                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                        }
                    #loginCheckresp = self.session.post(logincheckUrl, headers = loginCheckHeader, verify = False, timeout = None) 
                    #print(loginCheckresp.text)
                    
                    #loginCheckresp2 = self.session.get(logincheckUrl, headers = loginCheckHeader, verify = False, timeout = None) 
                    #print(loginCheckresp2.text)
                    
                    '''self.session.cookies["loginStatus"] = "logined"
                    self.session.cookies["cityCode"] = "js"
                    self.session.cookies["SHOPID_COOKIEID"] = "10011"
                    '''
                    
                    if(loginData["msg"] == "captcha"):
                        returnData = {
                            'status' : 'true',
                            'step' : '3',
                            'again' : 'true',
                            'msg': "",
                            'username': self.username,
                            'words': []
                        }
                        if(self.imgbyteBase64Str != None):
                            returnData['words'] = [
                                    {'ID' : 'jspiccode' , 'index' : '2' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '请输入四位黑色验证码' , 'type' : 'piccode' , 'source' : loginData["imgbyteBase64Str"]  }
                                ] 
                        CTCC.uploadException(self, username=str(self.username), step='js_capthca', errmsg=str(returnData))
                        return returnData
                        
                    #print(self.session.cookies["servJSessionID"])
#                     print(self.session.cookies)
                    
                    if( CTCC.goFrontPage(self) == True):
                
                        data = CTCC.sendAndCheckMblCode(self, obj)
                        return data
                    else:
                        returnData = CTCC.init(self)
                        returnData['msg'] = ' 系统错误！ 请退出输入'
                        return returnData
                else:
                    if( self.havePiccode == True):
                        CTCC.uploadException(self, username=str(self.username), step='0', errmsg=loginData["msg"])
                        data = CTCC.init(self)
    #                     data = json.loads(data)
                        data["msg"] = loginData["msg"]
                        return data
                    else:    
                        return loginData
            elif step == "1":
                '''obj["result"]["username"] = jsonParams["username"]
                obj["result"]["password"] = jsonParams["password"]'''
                if 'smsPwd' in jsonParams.keys():
                    smsPwd = str(jsonParams["smsPwd"])
                elif 'smsPwd' in jsonParams["result"].keys():
                    smsPwd = str(jsonParams["result"]["smsPwd"])
                self.mblCode = smsPwd#obj["result"]["smsPwd"]
                if CTCC.checkSMSPWD(self) == True:
                    return CTCC.getDatas(self)
                else:
                    respText = "短信验证失败，请退出"
                    CTCC.uploadException(self, username=str(self.username), step='5', errmsg=respText)
                    data = CTCC.init(self)
#                     data = json.loads(data)
                    data["msg"] = "短信验证失败，请退出"
                    return data
        except Exception:
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=str(self.username), step='5', errmsg=respText)
            data = CTCC.init(self)
#             data = json.loads(data)
            data["msg"] = "系统错误！请稍后重试!errcode:A10101"
            return data
        
    def getLoginAjax(self):
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
                #'User-Agent' : 'python-requests/2.12.3',
                #'Proxy-Connection':'keep-alive'
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            }
            
            url = 'http://login.189.cn/web/login' 
            getECSLoginresp = self.session.get(url, headers = headerStr, verify = False, allow_redirects = True) 
            ##time.sleep(10)
            #for get ProvinceID
            ajaxUrl = 'http://login.189.cn/web/login/ajax'
            ajax_post_data = {
                    'm': 'checkphone',
                    'phone': str(self.login_account)
                }
            ajaxHeaderStr = {
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9,en-IN;q=0.8,en;q=0.7',
                'Connection':'keep-alive',
                'Content-Length':'30',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Host':'login.189.cn',
                'Origin':'http://login.189.cn',
                'Referer':'http://login.189.cn/login',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest'
                }
            #print(ajax_post_data)
            getProvinceresp = self.session.post(ajaxUrl, data = ajax_post_data, headers = ajaxHeaderStr, verify = False, allow_redirects = True) 
            #print(getProvinceresp.text)
            #print(getProvinceresp.url)
            self.ProvinceID = json.loads(getProvinceresp.text)["provinceId"]
            self.AreaCode = json.loads(getProvinceresp.text)["areaCode"]
            
            self.loginInfo = self.username +'$$201$地市 （中文/拼音） $'+ self.ProvinceID +'$$$0'
            
            #13315923020$$201$地市（中文/拼音）$05$$$0"
            ##time.sleep(10)
            ajaxUrl2 = 'http://login.189.cn/web/login/ajax'
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
                'Accept-Language':'zh-CN,zh;q=0.9,en-IN;q=0.8,en;q=0.7',
                'Connection':'keep-alive',
                'Content-Length':'71',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Host':'login.189.cn',
                'Origin':'http://login.189.cn',
                'Referer':'http://login.189.cn/login',
                #'User-Agent' : 'python-requests/2.12.3',
                'X-Requested-With':'XMLHttpRequest',
                #'Proxy-Connection':'keep-alive'
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
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
            print(traceback.format_exc() )
            CTCC.uploadException( self, username = self.login_account, step = 'getLoginCookies', errmsg = traceback.format_exc() )
            return False
        
    def getVerifyCode(self):
        try:
            verifyCodeUrl = 'http://login.189.cn/web/captcha?undefined&source=login&width=200&height=67&0.5360629215832975'
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
           
        except Exception:
#             print(traceback.format_exc())
            CTCC.uploadException( self, username = self.login_account, step = 'doLogin', errmsg = traceback.format_exc() )
            returnData = CTCC.init( self )
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData    
    
    def doLogin(self, obj):
        time.sleep(1)
        dataResult = {
                    "result": "False",
                    "msg":""
                }
        try:
            self.haveservJSessionID = False  
            encry_obj = CTCC.passwordEncryption(self, str(self.username), str(self.Oldpassword))
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
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                'Cookie': 'EcsCaptchaKey='+ self.session.cookies['EcsCaptchaKey'] 
            }
            ##self.session.cookies["ECS_ReqInfo_login1"] = "U2FsdGVkX196M7FM0p64n8M+z1I12RQm+Bca/XNBE0ElXoV6BF2yUkGvqWFQSeCNFdcTLxKln7nOqrBYWi32Lgh3o9IPg4ReDihEJ1iITFk="
            
            #self.param["password"] = obj['result']['password']
            
            
            #obj['result']['password'] = encry_obj["password"]
            
            
            login_post_data = {
                'Account': str(self.username),
                'AreaCode': '',
                'Captcha':  self.piccode ,
                'CityNo': '',
                'Password': str(self.password),
                'ProvinceID': self.ProvinceID,
                'RandomFlag': '0',
                'UType': '201'
            }
            #login_post_data = 'Account='+ str(self.username) +'&UType=201&ProvinceID='+ self.ProvinceID +'&AreaCode=&CityNo=&RandomFlag=0&Password='+ str(self.password) +'&Captcha='+ self.piccode
            #print(login_post_data)
            url = 'http://login.189.cn/web/login' 
            getLoginresp = self.session.post(url, data = login_post_data, headers = headerStr, verify = False, timeout = None, allow_redirects = False) 
            print(getLoginresp.url)
            #print(getLoginresp.text)
            print(self.session.cookies)  
            if(getLoginresp.url.find("ecs.do") > 0 or ('Location' in getLoginresp.headers.keys() and getLoginresp.headers['Location'].find("ecs.do") > 0)):
                print('logined')
                print(getLoginresp.headers['Location'])
                time.sleep(1)
                CTCC.uploadException(self, username = str(self.login_account), step = 'logined', errmsg = 'logined')  
                header = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cache-Control':'max-age=0',
                        'Connection':'keep-alive',
                        'Host':'www.189.cn',
                        'Referer':'http://login.189.cn/login',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                        'Cookie': 'EcsLoginToken=' + self.session.cookies['EcsLoginToken']
                    }  
                getECSresp = self.session.get(getLoginresp.headers['Location'],  headers = header, verify = False, timeout = None, allow_redirects = True) 
                print(getECSresp.url)  
                
                CTCC.uploadException(self, username=str(self.login_account), step='getECSresp.url', errmsg=str(getECSresp.url))  
                #CTCC.uploadException(self, username=str(self.login_account), step='self.session.cookies', errmsg=str(self.session.cookies))  
                
                if(str(getECSresp.url) == 'http://js.189.cn/index'):
                    self.servJSessionID = self.session.cookies['servJSessionID']
                    js_captcha_url = 'http://js.189.cn/rand.action?t=1513130947472'
                    js_captcha_header = {
                            'Accept':'image/webp,image/apng,image/*,*/*;q=0.8',
                            'Accept-Encoding':'gzip, deflate',
                            'Accept-Language':'zh-CN,zh;q=0.9',
                            'Connection':'keep-alive',
                            'Host':'js.189.cn',
                            'Referer':'http://js.189.cn/self_service/validateLoginNew.action?favurl=http://js.189.cn/index',
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
                        }
                    getCaptcharesp = self.session.get(js_captcha_url,  headers = js_captcha_header, verify = False, timeout = None) 
                    imgbyteBase64Str = base64.b64encode(getCaptcharesp.content).decode(encoding = 'utf-8')
                    dataResult = {
                        "result": "True",
                        "msg":"captcha",
                        "imgbyteBase64Str": imgbyteBase64Str
                    }
                    return dataResult
                    
                 
                dataResult = {
                    "result": "True",
                    "msg":"success"
                }
                return dataResult
            elif(getLoginresp.url.find("login.189.cn") > 0):
                CTCC.uploadException(self, username=str(self.login_account), step='getLoginresp fail', errmsg=str(getLoginresp.text))  
                #print("password error ")
                #print(getLoginresp.text)
                respSoup = BeautifulSoup(getLoginresp.text,'html.parser')
                nameTags = respSoup.findAll('form',{"data-errmsg":True})
                #print(nameTags)
                errorMsg = "登录错误"
                data_resultcode =''
                for n in nameTags:
                    errorMsg = (n['data-errmsg'])
                    data_resultcode = str(n['data-resultcode'])
                    
                if errorMsg == "瀵嗙爜宸茶閿佸畾":
                    #print("Password locked try random password")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                elif data_resultcode == "9103":
                    #print("Password error")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                elif data_resultcode == "9999":
                    #print("need Verification code")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                elif data_resultcode == "9113":
                    #print("Password locked")
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : "9113"
                    }
                else:
#                     print("Password simple"+ str(errorMsg))
                    dataResult = {
                        "result": "False",
                        "msg": errorMsg,
                        "data_resultcode" : data_resultcode
                    }
                CTCC.uploadException(self, username=str(self.login_account), step='dologin', errmsg=dataResult['msg'])       
                
                return dataResult
            else:
                dataResult = {
                        "result": "False",
                        "msg": '登录错误',
                        "data_resultcode" : getLoginresp.url,
                        'getLoginresp' : getLoginresp.text
                    }
                CTCC.uploadException(self, username=str(self.login_account), step='getLoginresp.Url else', errmsg=str(getLoginresp.url))  
                CTCC.uploadException(self, username=str(self.login_account), step='getLoginresp.text else', errmsg=str(getLoginresp.text))  
                CTCC.uploadException(self, username=str(self.login_account), step='dologin else', errmsg=str(dataResult))  
                return  dataResult 
            return  dataResult  
                
        except Exception:
            respText = traceback.format_exc()
            print(respText)
            CTCC.uploadException(self, username=str(self.username), step='doLogin', errmsg=respText)
            returnData = CTCC.init( self )
            returnData["result"] = "False"
            returnData["msg"] = "统异常,请稍后重试,code:1005"
            return returnData
        
    def doJsLogin(self, obj):
        try:
            jsloginUrl = 'http://js.189.cn/self_service/validateLogin.action'
            jsLoginHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.9',
                    'Cache-Control':'max-age=0',
                    'Connection':'keep-alive',
                    'Content-Length':'165',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'js.189.cn',
                    'Origin':'http://js.189.cn',
                    'Referer':'http://js.189.cn/self_service/validateLoginNew.action?favurl=http://js.189.cn/index',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
                }
            jsPostData = {
                    'logonPattern':'1',
                    'userType':'2000004',
                    'validateCode':self.jspiccode,
                    'qqNum':'',
                    'newTargetUrl':'http://js.189.cn/index',
                    'newUamType':'-1',
                    'productId': self.username,
                    'userPwd':self.Oldpassword,
                    'validate':self.jspiccode
                }
            jsloginResp = self.session.post(jsloginUrl, headers = jsLoginHeader, data = jsPostData, verify = False, timeout = None) 
            #print(sessionresp.text)
            #CTCC.uploadException(self, username = str(self.username), step = 'jsloginResp', errmsg = str(jsloginResp.text) )
            
            jsloginstr = str(jsloginResp.text)
            
            searchstr = "var errorMsg = '"
            endStr = "';"
            start = jsloginstr.find(searchstr)
            end = jsloginstr.find( endStr , start)
            errorMsg = jsloginstr[start + len( searchstr ) : end]
            if(start != -1):
                CTCC.uploadException(self, username=str(self.username), step='doJsLogin error', errmsg= errorMsg)
                returnData = CTCC.init( self )
                returnData["result"] = "False"
                returnData["msg"] = errorMsg
                return returnData
                
            else: 
                
                try:
                    soup = BeautifulSoup(jsloginstr,'html.parser')
                    loginform = soup.find('form',attrs={'id':'loginform'})
                    
                    loginAction = soup.find('form', id='loginform').get('action')
                    print(loginAction)
                    
                    inputs = loginform.findAll('input')
                    hiddenValues = []
                    
                    for item in inputs:
                        hiddenValues.append({item.get('name'):item.get('value')})
                        
                    jsLoginHeader = {
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.9',
                        'Cache-Control':'max-age=0',
                        'Connection':'keep-alive',
                        'Content-Length':'165',
                        'Content-Type':'application/x-www-form-urlencoded',
                        'Host':'uam.telecomjs.com',
                        'Origin':'https://uam.telecomjs.com',
                        'Referer':'http://js.189.cn/self_service/validateLoginNew.action?favurl=http://js.189.cn/index',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
                    }
                    jsPostData = {}
                    for item in hiddenValues:
                        for key in item:
                            jsPostData[key] = item[key]
                    
                        
                    jsloginResp1 = self.session.post(loginAction, headers = jsLoginHeader, data = jsPostData, verify = False, timeout = None) 
                    '''CTCC.uploadException(self, username=str(self.username), step='uamtelecomjspjsPostData', errmsg= str(jsPostData))
                    CTCC.uploadException(self, username=str(self.username), step='uamtelecomjsp', errmsg= str(jsloginResp1.text))
                    CTCC.uploadException(self, username = str(self.username), step = 'uamtelecomjsp.cookies', errmsg = str(jsloginResp1.cookies) )'''
                        
                except:
                    respText = traceback.format_exc()
                    CTCC.uploadException(self, username=str(self.username), step='doJsLogin error', errmsg= respText)
            
                cookieVal = ''
                '''if('servJSessionID' not in cookieVal):
                    cookieVal = 'servJSessionID='+ self.session.cookies["servJSessionID"] + ';' + cookieVal'''
                '''CTCC.uploadException(self, username = str(self.username), step = 'sessionresp cookies', errmsg = str(self.session.cookies) )
                CTCC.uploadException(self, username = str(self.username), step = 'jsloginResp1.cookies', errmsg = str(jsloginResp1.cookies) )'''
                self.servJSessionID = jsloginResp1.cookies['servJSessionID']
                getSessUrl = 'http://js.189.cn/getSessionInfo.action'
                sessionHeader = {
                        'Accept':'application/json, text/javascript, */*',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'0',
                        'Host':'js.189.cn',
                        'Origin':'http://js.189.cn',
                        'Referer':'http://js.189.cn/service/bill?tabFlag=billing2',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest',
                        'Cookie' :'servJSessionID='+ self.servJSessionID + ';'
                    }
                sessionresp = self.session.post(getSessUrl, headers = sessionHeader, verify = False, timeout = None) 
                #print(sessionresp.text)
                #CTCC.uploadException(self, username = str(self.username), step = 'jslogin sessionresp init', errmsg = str(sessionresp.text) )
                
                dataResult = {
                        "result": "True",
                        "msg":"success"
                    }
            return dataResult
            
        except Exception:
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=str(self.username), step='doJsLogin', errmsg=respText)
            returnData = CTCC.init( self )
            returnData["result"] = "False"
            returnData["msg"] = "统异常,请稍后重试,code:1005"
            return returnData
        
    def goFrontPage(self):
        try:
            time.sleep(1)
            indexurl = 'http://www.189.cn/login/index.do'
            indexHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'www.189.cn',
                    'Referer':'http://www.189.cn/html/login/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            indexurlresp = self.session.get(indexurl, headers = indexHeader, verify = False) 
            #print(indexurlresp.url)
            #CTCC.uploadException(self, username = str(self.username), step = 'indexurlresp.url', errmsg = str(indexurlresp.url) + '-' + str(indexurlresp.text) )
            
            url = 'http://www.189.cn/dqmh/frontLinkSkip.do?method=skip&shopId=10011&toStUrl=http://js.189.cn/service/bill?tabFlag=billing2'
            frontPageHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'www.189.cn',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
                }
            frontPageUrlresp = self.session.get(url, headers = frontPageHeader, verify = False) 
            #print(frontPageUrlresp.url)
            
            '''#print(frontPageUrlresp.text)
            try:
                # This will create a new file or **overwrite an existing file**.
                f = open("C:/work/temp/file.txt", "w")
                try:
                    f.write( frontPageUrlresp.text ) # Write a string to a file
                finally:
                    f.close()
            except IOError:
                pass'''
            time.sleep(1)
            cookieVal = ''
            if('servJSessionID' not in cookieVal):
                cookieVal = 'servJSessionID='+ self.session.cookies["servJSessionID"] + ';' + cookieVal
                self.servJSessionID = self.session.cookies["servJSessionID"]
            #print(self.session.cookies)
            getSessUrl = 'http://js.189.cn/getSessionInfo.action'
            sessionHeader = {
                    'Accept':'application/json, text/javascript, */*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'0',
                    'Host':'js.189.cn',
                    'Cookie':cookieVal,
                    'Origin':'http://js.189.cn',
                    'Referer':'http://js.189.cn/service/bill?tabFlag=billing2',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            sessionresp = self.session.post(getSessUrl, headers = sessionHeader, verify = False, timeout = None) 
            #print(sessionresp.text)
            #CTCC.uploadException(self, username = str(self.username), step = 'sessionresp init', errmsg = str(sessionresp.text) )
            return True
        except:
            respText = traceback.format_exc()
            #print(respText)
            CTCC.uploadException(self, username=str(self.username), step='goFrontPage', errmsg=respText)
            returnData = CTCC.init( self )
            returnData["result"] = "False"
            returnData["msg"] = "统异常,请稍后重试,code:1005"
            return returnData
            
    def sendAndCheckMblCode(self, obj):
        try:
            time.sleep(1)
            cookieVal = 'servJSessionID='+ self.servJSessionID
            '''if(self.haveservJSessionID == True):
                cookieVal = 'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.username +';isLogin=logined; cityCode='+ self.cityCode +'; SHOPID_COOKIEID=10011; loginStatus=logined;'
            else:
                cookieVal = 'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+  self.username +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                '''
            sendCodeMblUrl = 'http://js.189.cn/queryValidateSecondPwdAction.action'
            sendCodeHeader = {
                'Accept':'application/json, text/javascript, */*',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Content-Length':'0',
                'Host':'js.189.cn',
                'Origin':'http://js.189.cn',
                'Referer':'http://js.189.cn/service/bill?tabFlag=billing2',
                'Connection':'keep-alive',
                #'Proxy-Connection':'keep-alive',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest',
                #'Cookie': 'aactgsh111220=17327368034; userId=201%7C20160000000050442023; isLogin=logined; .ybtj.189.cn=3C2D5DE6A423DF23DBC4B6BEDCD4E127; SHOPID_COOKIEID=10011; loginStatus=logined; Js_userId=2000004%3B17328367034; Js_isLogin=yes; Js_cityId=48; nTalk_CACHE_DATA={uid:kf_9643_ISME9754_17327368034_2000004,tid:1483584563011365}; NTKF_T2D_CLIENTID=guestTEMPD815-152C-725D-D379-6C87E7458943; s_cc=true; cityCode=js_xz; s_fid=0B735D3EAD73EDA2-1CBE8BC0FE7C419D; s_sq=eship-189-js%3D%2526pid%253Djs.189.cn%25252Fservice%25252Fbill%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BcheckValidateValueZDCX%252528%252527generate%252527%252529%25257D%2526oidt%253D2%2526ot%253DA%26eshipeship-189-all%3D%2526pid%253D%25252Fjs%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.189.cn%25252Fdqmh%25252FfrontLinkSkip.do%25253Fmethod%25253Dskip%252526shopId%25253D10011%252526toStUrl%25253Dhttp%25253A%25252F%25252Fjs.189.cn%25252Fservice%25252Fbi%2526ot%253DA'
                'Cookie': cookieVal#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                }#Js_userId=2000004%3B17328367034;Js_isLogin=yes;Js_cityId=48;NTKF_T2D_CLIENTID=guestTEMP9742-D42F-9EBC-B846-7169CDD7C50C;nTalk_CACHE_DATA={uid:kf_9643_ISME9754_17327368034_2000004,tid:1483666476501426};s_cc=true;s_fid=44CDDD2BFF021E27-3F8535F1A963EC78;s_sq=eship-189-js%3D%2526pid%253Djs.189.cn%25252Fservice%25252Fbill%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BcheckValidateValueZDCX%252528%252527generate%252527%252529%25257D%2526oidt%253D2%2526ot%253DA
            #Set-Cookie: servJSessionID=2525ED3305393AE5C635B06BEA246670-an3; Path=/
            send_post_data = {
                'inventoryVo.accNbr':str(self.username),
                'inventoryVo.productId':'2000004',
                'inventoryVo.action':'generate',
                'inventoryVo.inputRandomPwd':''
            }
            sendCheckresp = self.session.post(sendCodeMblUrl, headers = sendCodeHeader, data = send_post_data, verify = False, timeout = None) 
    #        print(sendCheckresp.text)
            CTCC.uploadException(self, username = str(self.username), step = 'sendCheckresp', errmsg = str(sendCheckresp.text) )
            if(sendCheckresp.text.find("TSR_RESULT")) == -1:
                data  = CTCC.init(self)
    #             data = json.loads(data)
                data["msg"] = "短信发送失败。系统错误。"
                return data
            else:
                data = {
                        'status' : 'true',
                        'step' : '1',
                        'again' : 'true',
                        'msg': '请输入短信验证码',
                        'username': self.login_account,
                        'words' : [
                                {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                            ]
                    }
            return data
            #TSR_RESULT
        except Exception:
            respText = traceback.format_exc()
            #print(respText)
            CTCC.uploadException(self, username = str(self.username), step = 'sendAndCheckMblCode', errmsg = respText)
            data = CTCC.init(self)
#             data = json.loads(data)
            data["msg"] = "系统错误。请退出，请稍后再试!errcode:A10101"
            return data
        
        
        #mblCode = raw_input("Please enter Mobile Code: ")
        
    def checkSMSPWD(self):
        try:
            if(self.haveservJSessionID == True):
                cookieVal = 'servJSessionID='+ self.servJSessionID +';aactgsh111220='+ self.username +';isLogin=logined; cityCode='+ self.cityCode +'; SHOPID_COOKIEID=10011; loginStatus=logined;'
            else:
                cookieVal = 'servJSessionID='+ self.servJSessionID +';aactgsh111220='+ self.username +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'#.ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';userId='+ self.session.cookies["userId"] +'; 
                
            sendCodeMblUrl = 'http://js.189.cn/queryValidateSecondPwdAction.action'
            sendCodeHeader = {
                'Accept':'application/json, text/javascript, */*',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Content-Length':'0',
                'Host':'js.189.cn',
                'Origin':'http://js.189.cn',
                'Referer':'http://js.189.cn/service/bill?tabFlag=billing2',
                'Connection':'keep-alive',
                #'Proxy-Connection':'keep-alive',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest',
                #'Cookie': 'aactgsh111220=17327368034; userId=201%7C20160000000050442023; isLogin=logined; .ybtj.189.cn=3C2D5DE6A423DF23DBC4B6BEDCD4E127; SHOPID_COOKIEID=10011; loginStatus=logined; Js_userId=2000004%3B17328367034; Js_isLogin=yes; Js_cityId=48; nTalk_CACHE_DATA={uid:kf_9643_ISME9754_17327368034_2000004,tid:1483584563011365}; NTKF_T2D_CLIENTID=guestTEMPD815-152C-725D-D379-6C87E7458943; s_cc=true; cityCode=js_xz; s_fid=0B735D3EAD73EDA2-1CBE8BC0FE7C419D; s_sq=eship-189-js%3D%2526pid%253Djs.189.cn%25252Fservice%25252Fbill%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BcheckValidateValueZDCX%252528%252527generate%252527%252529%25257D%2526oidt%253D2%2526ot%253DA%26eshipeship-189-all%3D%2526pid%253D%25252Fjs%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.189.cn%25252Fdqmh%25252FfrontLinkSkip.do%25253Fmethod%25253Dskip%252526shopId%25253D10011%252526toStUrl%25253Dhttp%25253A%25252F%25252Fjs.189.cn%25252Fservice%25252Fbi%2526ot%253DA'
                'Cookie': cookieVal#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                }
            
            send_post_data = {
                'inventoryVo.accNbr':str(self.username),
                'inventoryVo.productId':'2000004',
                'inventoryVo.action':'check',
                'inventoryVo.inputRandomPwd': str(self.mblCode)
            }
            sendCheckresp1 = self.session.post(sendCodeMblUrl, headers = sendCodeHeader, data = send_post_data, verify = False, timeout = None) 
           
            if(sendCheckresp1.text.find("TSR_RESULT")) == -1:
                return False
            else:
                CTCC.uploadException(self, self.username, 'checkSMSPWD', 'Passed')
                return True
        except Exception:
            respText = traceback.format_exc()
            #print(respText)
            CTCC.uploadException(self, username=str(self.username), step='5', errmsg=respText)
            return False
       
    def getDatas(self):
        try:
            time.sleep(1)
            if(self.haveservJSessionID == True):
                cookieVal = 'servJSessionID='+ self.servJSessionID +';aactgsh111220='+ self.username +';isLogin=logined; cityCode='+ self.cityCode +'; SHOPID_COOKIEID=10011; loginStatus=logined;'
            else:
                cookieVal = 'servJSessionID='+ self.servJSessionID +';aactgsh111220='+ self.username +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'#.ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';userId='+ self.session.cookies["userId"] +'; 
                
            self.result_info = {}
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
            self.result_info['phoneNum'] = self.username
            self.result_info['userInfo'] = userInfo
            self.result_info['ispName'] = "电信"
            self.result_info['ispCode'] = 'CTCC'
            self.result_info['ispProvince'] = '江苏'
            self.result_info['flow_no'] = self.flowNo
            self.result_info['createTime'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.result_info["billDetail"] = []
            self.result_info["paymentRecord"] = []
            #self.result_info['historyBillInf'] = []
            getCallVoiceListUrl = 'http://js.189.cn/queryVoiceMsgAction.action'
            
            today = datetime.date.today()
            first = today.replace(day=1)
            rest = first - datetime.timedelta(days=1)
            
            lastMonth = today.strftime("%m")
            lastYear = today.strftime("%Y")
            lastDay = calendar.monthrange(int(lastYear), int(lastMonth))[1]
            i = 0
            phoneInfoArr = []
            smsInfoArr = []
            dataInfoArr = []
            paymentInfoArr = []
            while i < 6:
                i += 1
                callVoiceListHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Content-Length':'210',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'js.189.cn',
                    'Origin':'http://js.189.cn',
                    'Referer':'http://js.189.cn/service/bill?tabFlag=billing4',
                    'Connection':'keep-alive',
                    #'Proxy-Connection':'keep-alive',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest',
                    #'Cookie': 'aactgsh111220=17327368034; userId=201%7C20160000000050442023; isLogin=logined; .ybtj.189.cn=3C2D5DE6A423DF23DBC4B6BEDCD4E127; SHOPID_COOKIEID=10011; loginStatus=logined; Js_userId=2000004%3B17328367034; Js_isLogin=yes; Js_cityId=48; nTalk_CACHE_DATA={uid:kf_9643_ISME9754_17327368034_2000004,tid:1483584563011365}; NTKF_T2D_CLIENTID=guestTEMPD815-152C-725D-D379-6C87E7458943; s_cc=true; cityCode=js_xz; s_fid=0B735D3EAD73EDA2-1CBE8BC0FE7C419D; s_sq=eship-189-js%3D%2526pid%253Djs.189.cn%25252Fservice%25252Fbill%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BcheckValidateValueZDCX%252528%252527generate%252527%252529%25257D%2526oidt%253D2%2526ot%253DA%26eshipeship-189-all%3D%2526pid%253D%25252Fjs%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.189.cn%25252Fdqmh%25252FfrontLinkSkip.do%25253Fmethod%25253Dskip%252526shopId%25253D10011%252526toStUrl%25253Dhttp%25253A%25252F%25252Fjs.189.cn%25252Fservice%25252Fbi%2526ot%253DA'
                    'Cookie': cookieVal#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                    }
                call_post_data = {
                    'inventoryVo.accNbr':str(self.username),
                    'inventoryVo.getFlag':'1',
                    'inventoryVo.begDate': str(lastYear)+str(lastMonth)+'01',
                    'inventoryVo.endDate': str(lastYear)+str(lastMonth)+str(lastDay),
                    'inventoryVo.family':'4',
                    'inventoryVo.accNbr97':'',
                    'inventoryVo.productId':'4',
                    'inventoryVo.acctName':str(self.username)
                }
#                 print("start: "+ str(lastYear)+str(lastMonth)+'01' +" end: "+str(lastYear)+str(lastMonth)+str(lastDay))
                sendCheckresp1 = self.session.post(getCallVoiceListUrl, headers = callVoiceListHeader, data = call_post_data, verify = False, timeout = None) 
                #print(sendCheckresp1.text)
                str_sendCheckresp1 = sendCheckresp1.text
                if(sendCheckresp1.text.find("items")) == -1:
                    print("no result ")
                    CTCC.uploadException(self, self.username, 'Phone info result',  str(sendCheckresp1.text))
                else:
                    try:
                        sendCheckresp1 = json.loads(sendCheckresp1.text, encoding = 'utf-8')
                        itemsArr = sendCheckresp1["items"]
                        for item in itemsArr:
                #            print(item)
                            callType = item["ticketType"]
                            commType = item["ticketType"]
                            commPhoneNo = item["accNbr"]
                            commDate = item["startDateNew"]
                            commTotalTime = item["durationCh"]
                            cost = item["ticketChargeCh"]
                            commTime = item["startTimeNew"]
                            
                            endDatestr = time.strptime(commDate,"%Y-%m-%d")
                            commDate = time.strftime("%Y%m%d",endDatestr)
                            
                            endDatestr = time.strptime(commTime,"%H:%M:%S")
                            startTime = time.strftime("%H%M%S",endDatestr)
                            
                            callTypestr = ""
                            if( callType.find("主叫") == -1 ):
                                if( callType.find("被叫") != -1 ):
                                    callTypestr = "被叫"  
                            else:
                                callTypestr = "主叫"  
                                
                            timeVal = commTotalTime.split(":")
                            hourval = timeVal[0]
                            minval = timeVal[1]
                            secval = timeVal[2]
                            
                            totalTime = ( int(hourval) * 3600 ) + ( int(minval) * 60 ) + int(secval)
                            if( float(cost) != 0):
                                cost = str(int(float(cost) * 100 ))
                            else:
                                cost = '0'
                                
                            phoneInfoArr.append({
                                "callTypeName": callTypestr,
                                "callPlace":"",
                                "otherPhoneNum": commPhoneNo,
                                "startDate": commDate,
                                "startTime": startTime,
                                "totalTime": str(totalTime),
                                "totalFee": cost,
                                "commType" : commType
                                })
                    except:
                        CTCC.uploadException(self, self.username, 'exce Phone info result',  str(str_sendCheckresp1) + str(traceback.format_exc()))
                    
                    
               
                
                getdataListUrl = 'http://js.189.cn/queryNewDataMsgListAction.action'
                dataListHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Content-Length':'210',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'js.189.cn',
                    'Origin':'http://js.189.cn',
                    'Referer':'http://js.189.cn/service/bill?tabFlag=billing4',
                    'Connection':'keep-alive',
                    #'Proxy-Connection':'keep-alive',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest',
                    #'Cookie': 'aactgsh111220=17327368034; userId=201%7C20160000000050442023; isLogin=logined; .ybtj.189.cn=3C2D5DE6A423DF23DBC4B6BEDCD4E127; SHOPID_COOKIEID=10011; loginStatus=logined; Js_userId=2000004%3B17328367034; Js_isLogin=yes; Js_cityId=48; nTalk_CACHE_DATA={uid:kf_9643_ISME9754_17327368034_2000004,tid:1483584563011365}; NTKF_T2D_CLIENTID=guestTEMPD815-152C-725D-D379-6C87E7458943; s_cc=true; cityCode=js_xz; s_fid=0B735D3EAD73EDA2-1CBE8BC0FE7C419D; s_sq=eship-189-js%3D%2526pid%253Djs.189.cn%25252Fservice%25252Fbill%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BcheckValidateValueZDCX%252528%252527generate%252527%252529%25257D%2526oidt%253D2%2526ot%253DA%26eshipeship-189-all%3D%2526pid%253D%25252Fjs%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.189.cn%25252Fdqmh%25252FfrontLinkSkip.do%25253Fmethod%25253Dskip%252526shopId%25253D10011%252526toStUrl%25253Dhttp%25253A%25252F%25252Fjs.189.cn%25252Fservice%25252Fbi%2526ot%253DA'
                    'Cookie': cookieVal#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                    }
                data_post_data = {
                    'inventoryVo.accNbr':str(self.username),
                    'inventoryVo.getFlag':'1',
                    'inventoryVo.begDate': str(lastYear)+str(lastMonth)+'01',
                    'inventoryVo.endDate': str(lastYear)+str(lastMonth)+str(lastDay),
                    'inventoryVo.family':'4',
                    'inventoryVo.accNbr97':'',
                    'inventoryVo.productId':'4',
                    'inventoryVo.acctName':str(self.username)
                }
                getDataresp1 = self.session.post(getdataListUrl, headers = dataListHeader, data = data_post_data, verify = False, timeout = None) 
        #        print(getDataresp1.text)
                #CTCC.uploadException(self, self.username, 'net 11 info result',  str(getDataresp1.text))
                if(getDataresp1.text.find("items")) == -1:
                    print("no result ")
                    CTCC.uploadException(self, self.username, 'net info result',  str(getDataresp1.text))
                else:
                    getDataresp1 = json.loads(getDataresp1.text, encoding = 'utf-8')
                    
                    itemsArr = getDataresp1["items"]
                    for item in itemsArr:
            #            print(item)
                        netDate = item["START_TIME"]
                        netMoney  = item["TICKET_CHARGE_CH"]
                        netType  = item["SERVICE_TYPE"]
                        netFlow  = item["BYTES_CNT"]
                        netTotalTime  = item["DURATION_CH"]
                        
                        endDatestr = time.strptime(netDate,"%Y-%m-%d %H:%M:%S")
                        netDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                        
#                         timeVal = netTotalTime.find("分钟")
#                         secVal = netTotalTime.find("秒")
#                         minuteVal = netTotalTime[0:timeVal]
#                         
#                         secondsVal = "0"
#                         #4小时53分钟29秒
#                         if(secVal != -1):
#                             secondsVal = netTotalTime[timeVal + len("分钟") : secVal]
                        try:
                            hourVal = '0'        
                            minuteVal = '0'        
                            secondsVal = '0'
                            
                            hour = re.compile(r'(.*?)小时')
                            hourA = re.findall(hour,netTotalTime)
                            if(len(hourA) > 0):
                                hourVal = hourA[0]
                                
                                netTotalTime = netTotalTime.split('小时')
                                netTotalTime = netTotalTime[1]
                            
                            minute = re.compile(r'(.*?)分钟')
                            minuteA = re.findall(minute,netTotalTime)
                            if(len(minuteA) > 0):
                                minuteVal = minuteA[0]
                                netTotalTime = netTotalTime.split('分钟')
                                netTotalTime = netTotalTime[1]
                                
                            
                            seconds = re.compile(r'(.*?)秒')
                            secondsA = re.findall(seconds,netTotalTime)
                            if(len(secondsA) > 0):
                                secondsVal = secondsA[0]
                            
                            totalTime = (int(hourVal) * 3600 ) + ( int(minuteVal) * 60 ) + int(secondsVal)

                        except Exception:
                            CTCC.uploadException(self, self.username, 'timeformat', str(netTotalTime))
                            totalTime = "0"
#                         print(netMoney)
                        if( float(netMoney) != 0):
                            netMoney = str(int(float(netMoney) * 100 ))
                        else:
                            netMoney = "0"
                            
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
                        
                        dataInfoArr.append({
                            "netType": netType,
                            "startTime": netDate,
                            "totalTime": totalTime,
                            "totalFee": netMoney,
                            "totalTraffic": netTraffic,
                            "netPlace":""
                            })
                    
            #        print(dataInfoArr)
                    
               
                
                SMSListUrl = 'http://js.189.cn/mobileInventoryAction.action'
                SMSListHeader = {
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Content-Length':'210',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'js.189.cn',
                    'Origin':'http://js.189.cn',
                    'Referer':'http://js.189.cn/service/bill?tabFlag=billing4',
                    'Connection':'keep-alive',
                    #'Proxy-Connection':'keep-alive',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest',
                    #'Cookie': 'aactgsh111220=17327368034; userId=201%7C20160000000050442023; isLogin=logined; .ybtj.189.cn=3C2D5DE6A423DF23DBC4B6BEDCD4E127; SHOPID_COOKIEID=10011; loginStatus=logined; Js_userId=2000004%3B17328367034; Js_isLogin=yes; Js_cityId=48; nTalk_CACHE_DATA={uid:kf_9643_ISME9754_17327368034_2000004,tid:1483584563011365}; NTKF_T2D_CLIENTID=guestTEMPD815-152C-725D-D379-6C87E7458943; s_cc=true; cityCode=js_xz; s_fid=0B735D3EAD73EDA2-1CBE8BC0FE7C419D; s_sq=eship-189-js%3D%2526pid%253Djs.189.cn%25252Fservice%25252Fbill%2526pidt%253D1%2526oid%253Dfunctiononclick%252528event%252529%25257BcheckValidateValueZDCX%252528%252527generate%252527%252529%25257D%2526oidt%253D2%2526ot%253DA%26eshipeship-189-all%3D%2526pid%253D%25252Fjs%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fwww.189.cn%25252Fdqmh%25252FfrontLinkSkip.do%25253Fmethod%25253Dskip%252526shopId%25253D10011%252526toStUrl%25253Dhttp%25253A%25252F%25252Fjs.189.cn%25252Fservice%25252Fbi%2526ot%253DA'
                    'Cookie': cookieVal#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                    }
                sms_post_data = {
                    'inventoryVo.accNbr':str(self.username),
                    'inventoryVo.getFlag':'1',
                    'inventoryVo.begDate': str(lastYear)+str(lastMonth)+'01',
                    'inventoryVo.endDate': str(lastYear)+str(lastMonth)+str(lastDay),
                    'inventoryVo.family':'4',
                    'inventoryVo.accNbr97':'',
                    'inventoryVo.productId':'4',
                    'inventoryVo.acctName':str(self.username)
                }
                getSMSresp1 = self.session.post(SMSListUrl, headers = SMSListHeader, data = sms_post_data, verify = False, timeout = None) 
                #print(getSMSresp1.text)
                if(getSMSresp1.text.find("items")) == -1:
                    print("no result ")
                    CTCC.uploadException(self, self.username, 'sms info result',  str(getSMSresp1.text))
                else:
                    getSMSresp1 = json.loads(getSMSresp1.text, encoding = 'utf-8')
                    #print(getSMSresp1)
                    itemsArr = getSMSresp1["items"]
                    for item in itemsArr:
                        msgDate = item["startDateNew"]
                        msgPhone  = item["accNbr"]
                        sendType  = item["ticketType"]
                        cost  = item["ticketChargeCh"]
                        
                        endDatestr = time.strptime(msgDate,"%Y-%m-%d")
                        msgDate = time.strftime("%Y%m%d",endDatestr)
                        
                        msgTime = item["startTimeNew"]
                        endDatestr = time.strptime(msgTime,"%H:%M:%S")
                        smsTime = time.strftime("%H%M%S",endDatestr)
                        
                        if( float(cost) != 0):
                            cost = str(int(float(cost) * 100 ))
                        else:
                            cost = '0'
                        
                        smsInfoArr.append({
                            "smsType": sendType,
                            "otherPhoneNum":msgPhone,
                            "smsDate": msgDate,
                            "smsTime": smsTime,
                            "totalFee": cost,
                            "place":""
                            })
                paymentdetailUrl = "http://js.189.cn/queryRechargeRecord.action?queryType=0&queryNbr="+ str(self.username) +"&proType=4&begDate="+str(lastYear)+str(lastMonth)+'01'+"&endDate="+str(lastYear)+str(lastMonth)+str(lastDay)
                payment_postData = {
                    'Action':'post',
                    'Name':'queryRecharge'
                    }
                paymentHeaderStr = {
                        'Accept':'application/json, text/javascript, */*',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'30',
                        'Content-Type':'application/x-www-form-urlencoded',
                        'Cookie':cookieVal,#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;',
                        'Host':'js.189.cn',
                        'Origin':'http://js.189.cn',
                        'Referer':'http://js.189.cn/queryRechargeInfo/forwadToQueryRecharge.action',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest'
                    }
                paymentresp1 = self.session.post(paymentdetailUrl, data = payment_postData,  headers = paymentHeaderStr, verify = False, timeout = None) 
                str_paymentresp1 = paymentresp1.text
                try:
                    paymentresp1 = json.loads(str(paymentresp1.text), encoding = 'utf-8')
                    #print(items)
                    
                    if 'items' in paymentresp1.keys():
                        items = paymentresp1["items"]
                        for item in items:
                            payDate = item["startDate"]
                            payFee  = str(item["paymentCharge"]) 
                            payChannel  = item["fundsTypeName"]
                            
                            endDatestr = time.strptime(payDate,"%Y-%m-%d")
                            payDate = time.strftime("%Y%m%d",endDatestr)
                            
                            billTime1 = item["startTime"]
                            endDatestr = time.strptime(billTime1,"%H:%M:%S")
                            billTime = time.strftime("%H%M%S",endDatestr)
                            '''if( int(payFee) != 0):
                                payFee = str(int(float(payFee) * 100))'''
                                
                            paymentInfoArr.append({
                                "billDate":  payDate,
                                "billTime": billTime,
                                "billFee": str(payFee),
                                "busiName": payChannel
                                })
                except:
                    respText = traceback.format_exc()
                    CTCC.uploadException(self, username=str(self.username), step=' paymentInfoArr ', errmsg = str(str_paymentresp1) + "_"+ respText)        
                
                
               
                d1 = datetime.date(int(lastYear), int(lastMonth), int(lastDay))
                first = d1.replace(day=1)
                rest = first - datetime.timedelta(days=1)
                lastMonth = rest.strftime("%m")
                lastYear = rest.strftime("%Y")
                lastDay = calendar.monthrange(int(lastYear), int(lastMonth))[1]
                
            
            
            self.result_info['callDetail'] = phoneInfoArr
            self.result_info['netDetail'] = dataInfoArr
            self.result_info['smsDetail'] = smsInfoArr
            self.result_info['billDetail'] = paymentInfoArr
            #self.getUserInfo()
            userInfoUrl = "http://js.189.cn/getSessionInfo.action"
            userInfoHeader = {
                    'Accept':'application/json, text/javascript, */*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Content-Length':'0',
                    'Cookie':cookieVal,#'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;',
                    'Host':'js.189.cn',
                    'Origin':'http://js.189.cn',
                    'Referer':'http://js.189.cn/service/manage?in_cmpid=yhzx-zzgl-grzl',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            getuserresp1 = self.session.post(userInfoUrl, headers = userInfoHeader, verify = False, timeout = None) 
    #        print(getuserresp1.text)
            getuserresp1 = json.loads(getuserresp1.text, encoding = 'utf-8')
            userInfoObj = {
                "certNum": getuserresp1["indentCode"],
                "address": getuserresp1["userAddress"],
                "name": getuserresp1["userName"],
                "inNetDate" : '',
                "email" : getuserresp1["email"]
                }
            productCollection = getuserresp1["productCollection"]
            self.userLoginType = getuserresp1["userLoginType"]
            self.result_info['userInfo'] = userInfoObj
            
            balance = str(int(float(getuserresp1["blanceMoney"]) * 100)) 
            realmoney = str(int(float(getuserresp1["realMoney"]) * 100)) 
            
            self.result_info["userInfo"]["balance"] = balance
            self.result_info["userInfo"]["oweFee"] = realmoney
            self.result_info["userInfo"]["status"] = "0"
            
            
            #GET Package infos
            '''packageInfoUrl = "http://js.189.cn/queryWare.action?userID="+ str(self.username) +"&userType="+ self.userLoginType
            packageInfoHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'servJSessionID='+ self.session.cookies["servJSessionID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;',
                    'Host':'js.189.cn',
                    'Referer':'http://js.189.cn/service/account',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            getpackageresp1 = self.session.get(packageInfoUrl, headers = packageInfoHeader, verify = False, timeout = None) 
            getpackageArr = eval(getpackageresp1.text)
            phoneInfoObj = {
                    "status":'OK',
                    "serviceLevel": '',
                    "inNetDate": '',
                    "totalCreditValue": '',
                    "realMoney": str(getuserresp1["realMoney"]),
                    "balance": str(getuserresp1["blanceMoney"]),
                    "pointValue": str(getuserresp1["points"]),
                    "basicMonthFee": str(getuserresp1["basicMonthFee"]),
                    "packageInfos": getpackageArr
                }
            
            #print(phoneInfoObj)
            #self.result_info['phoneInfo'] = phoneInfoObj'''
            
            
            
    #        print(self.result_info)
            
            if self.result_info :
                print('-----------CTCC Successful List------------')
                self.isSuccess = CTCC.uploadData( self, self.result_info)
                if self.isSuccess :
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : 'success'
                    }
                    CTCC.uploadException(self, self.username, 'Upload Data', 'Upload Data Success')
                    CTCC.uploadException(self, self.username, 'Uploaded call_SMS_Net detail', str(len(self.result_info['callDetail'])) + "_" + str(len(self.result_info['smsDetail'])) + "_" + str(len(self.result_info['netDetail'])) )
                    return returnData
                else:
                    returnData = { 
                        'status' : 'true' ,
                        'again' : 'false' ,
                        'msg' : 'false'
                    }
                    return returnData
        except Exception:
            respText = traceback.format_exc()
#             print(respText)
            CTCC.uploadException(self, username=str(self.username), step='5', errmsg=respText)
            data = CTCC.init(self)
#             data = json.loads(data)
            data["msg"] = "系统错误！请稍后重试!errcode:A10101"
            return data