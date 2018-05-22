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
import calendar
import base64
from builtins import str

class CTCC() :
    '''中国电信爬虫-贵州省
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
    
    def init(self, params=None ) :
        #self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        #self.jiamiUrl = 'http://192.168.1.82:8081/creditcrawler/bank/getEncryptParams'
        #self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        self.jiamiUrl = 'http://api.telecom.yuancredit.com/JsEncrypt'
        
        #防止重复初始化覆盖新值
        if not hasattr(self, 'crawlerServiceUrl'):
            self.crawlerServiceUrl = 'http://192.168.1.82:8081/creditcrawler/common/service'
        if not hasattr(self, 'uploadExceptionUrl'):
            self.uploadExceptionUrl = 'http://192.168.1.82:8081/creditcrawler/base/addErrorInfo'
        
        respText = ''
        
        if params :
            self.initCfg(self, params)  
            
        self.param = {
            'username':'',
            'password':''
        }
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
            respText = traceback.format_exc()
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
       # print(data)
        try:
            headers = {
                'Accept':'*/*',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
            }
            postData = {
                'heade':{'code':'uploadIspData','token':'','timestamp':''},
                'body':{
                    'attach':'',
                    'content':data
                }
            }
            print('uploadData-->[post] ctcc_gz data to ' + self.crawlerServiceUrl)
            resp = requests.post(self.crawlerServiceUrl, headers = headers, data = {'content':json.dumps(postData, ensure_ascii=False)})
            respText = resp.text;
            #print(resp.text)
            respObj = json.loads(str(resp.text).strip(), encoding = 'utf-8')
            if 'resCode' in respObj.keys() and '0' == str(respObj['resCode']):
                return True
            else:
                CTCC.uploadException(self, username=self.username, step='uploadData', errmsg=respText)
                return False
        except Exception:
            print('uploadData-->[post] ctcc_gz data error, ' + self.crawlerServiceUrl)
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=self.username, step='uploadData', errmsg=respText)
            return False
   
    def uploadException(self, username = '', step = '', errmsg = ''):
        #上传异常信息
        headers = {
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
        }
        data = {'error_info': errmsg,'error_step':step,'error_type':'ctcc_gz','login_account':username}
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
            'loginInfo': self.loginInfo,
            'password': password
        }
#         print(username)
#         print(password)
        resp = self.session.post(self.jiamiUrl, headers = jiamiUrl_headers, data = {'content':json.dumps(jiamiUrl_params,ensure_ascii=False)}, allow_redirects = True)
        #print('jiami post sucess'+str(resp.text))
        jiamiObj = json.loads(resp.text, encoding = 'utf-8')
#         print('jiamiObj=',jiamiObj,'\n')
        self.loginInfo = ''
        try:
            self.param['password'] = jiamiObj['password']
            self.loginInfo = jiamiObj['loginInfo']
#             print(self.param['password'])
            self.password = jiamiObj['password']
#             print(self.param)
        except Exception:
            respText = traceback.format_exc()
            CTCC.uploadException(self, username=username, step='passwordencryption', errmsg=respText)
            data = {     
                    'status':'true',    
                    'step':'0',     
                    'msg':'系统内部错误,请退出重试', 
                    'words':[             
                                {'ID':'username','index': '0',  'label':'手机号码', 'type': 'text'},    
                                {'ID':'password','index': '1', 'label':'服务密码', 'type': 'password'}  
                            ]       
                }
            return data
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
            #print(jsonParams)
            if 'step' in jsonParams.keys():
                step = jsonParams["step"]
            else:
                step = str(jsonParams["result"]["step"])
                obj = {"result":jsonParams["result"]}
                '''jsonParams["username"] = jsonParams["result"]["username"]
                jsonParams["password"] = jsonParams["result"]["password"]'''
#             print(step)
            self.step = step
            if(step == "0"):
                self.havePiccode = False
                self.jsonParams = jsonParams
                if 'flowNo' in jsonParams.keys():
                    self.flowNo = jsonParams['flowNo']
                else:
                    self.flowNo = str(jsonParams["result"]["flowNo"])
                #print(jsonParams)
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
                self.login_password = self.password 
                CTCC.uploadException(self, self.username, 'docapture1', 'init_' + str(self.login_password))
                data = CTCC.doLogin(self, obj)
                if(data['result'] == 'true'):
                    #loginCheckresp2 = self.session.get(logincheckUrl, headers = loginCheckHeader, verify = False, timeout = None) 
                    #print(loginCheckresp2.text)
    #                 print("LOGGINNN CHECK22222")
                    self.session.cookies["loginStatus"] = "logined"
                    self.session.cookies["cityCode"] = "gz"
                    self.session.cookies["SHOPID_COOKIEID"] = "10024"
                    #print(self.session.cookies["servJSessionID"])
                    data = {}
                    if( CTCC.goFrontPage(self) ):
                        #self.getDatas(self, obj)
                        data = CTCC.sendAndCheckMblCode(self)
                        return data
                    else:
                        returnData = CTCC.init(self)
                        returnData = json.loads(json.dumps(returnData), encoding = 'utf-8')
                        returnData['msg'] = '系统内部错误,请退出重试'
                        return returnData
                else:
                    return data
            elif(self.step == "2"):
                self.havePiccode = True
                piccode = ''
                obj = {
                        "result" : {
                            'status':'true',
                            'again':'true',
                            'step':self.step,
                            'username':self.username,
                            'password':self.login_password,
                            'gostep':''
                        }
                      }
                if 'piccode' in jsonParams.keys():
                    piccode = str(jsonParams["piccode"])
                elif 'piccode' in jsonParams["result"].keys():
                    piccode = str(jsonParams["result"]["piccode"])
                self.piccode = piccode
                data = CTCC.doLogin(self, obj)
                if(data['result'] == 'true'):
                    #loginCheckresp2 = self.session.get(logincheckUrl, headers = loginCheckHeader, verify = False, timeout = None) 
                    #print(loginCheckresp2.text)
    #                 print("LOGGINNN CHECK22222")
                    self.session.cookies["loginStatus"] = "logined"
                    self.session.cookies["cityCode"] = "gz"
                    self.session.cookies["SHOPID_COOKIEID"] = "10024"
                    #print(self.session.cookies["servJSessionID"])
                    data = {}
                    if( CTCC.goFrontPage(self) ):
                        #self.getDatas(self, obj)
                        data = CTCC.sendAndCheckMblCode(self)
                        return data
                    else:
                        returnData = CTCC.init(self)
                        returnData = json.loads(json.dumps(returnData), encoding = 'utf-8')
                        returnData['msg'] = '系统内部错误,请退出重试'
                        return returnData
                else:
                    return data
            
            elif step == "1":
                if 'smsPwd' in jsonParams.keys():
                    smsPwd = str(jsonParams["smsPwd"])
                elif 'smsPwd' in jsonParams["result"].keys():
                    smsPwd = str(jsonParams["result"]["smsPwd"])
                self.mblCode = smsPwd#obj["result"]["smsPwd"]
#                 print('smsPwd is ' + str(smsPwd))
                #self.checkSMSPWD(self)
                return CTCC.getDatas(self)
        except Exception:
            respText  = traceback.format_exc()
            
            CTCC.uploadException(self, username=self.username, step='doCapture', errmsg=respText)
        
    def getVerifyCode(self):
        try:
            verifyCodeUrl = 'http://login.189.cn/web/captcha?undefined&source=login&width=100&height=37&0.3061189955455248'
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
    
    
    def doLogin(self, obj):
        
       
        
        try:
            if( self.havePiccode == False):
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
                    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
                }
                
                url = 'http://login.189.cn/login' 
                getECSLoginresp = self.session.get(url, headers = headerStr, verify = False, timeout = None) 
                #print(getECSLoginresp.text)
                #print(self.session.cookies)
                
                #for get ProvinceID
                ajaxUrl = 'http://login.189.cn/web/login/ajax'
                ajax_post_data = {
                        'm': 'checkphone',
                        'phone': str(self.username)
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
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                    }
                getProvinceresp = self.session.post(ajaxUrl, data = ajax_post_data, headers = ajaxHeaderStr, verify = False, timeout = None) 
    #             print(getProvinceresp.text)
        #        print(self.session.cookies)
                self.ProvinceID = json.loads(getProvinceresp.text)["provinceId"]
        #         print(ProvinceID)
                
                ajaxUrl2 = 'http://login.189.cn/web/login/ajax'
                ajax_post_data2 = {
                    'Account': str(self.username),
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
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                    }
                getAJAXresp2 = self.session.post(ajaxUrl2, data = ajax_post_data2, headers = ajaxHeaderStr2, verify = False, timeout = None) 
                jsonRes = json.loads(getAJAXresp2.text, encoding = 'utf-8')
                if(str(jsonRes["captchaFlag"]).lower() == "true"):
                    self.imgbyteBase64Str = CTCC.getVerifyCode(self)
                    returnData = {
                            'result' : 'false',
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
    #         print(getAJAXresp2.text)
    #         print(self.session.cookies)
            
            #U2FsdGVkX1%2B8CHhx2vKYzNLuTUDVPzluCZkMCbGtfnP%2F23IyiS0GB%2FRcQtI1O7z9i3j1ey%2F0WB3cDWFW9OApTql%2B0wG8x9tOXEi%2B6DVS3Wo%3D
            self.param["password"] = obj['result']['password']
            self.loginInfo = self.username +'$$201$地市 （中文/拼音） $'+ self.ProvinceID +'$$$0'
            encry_obj = self.passwordEncryption(self, str(self.username), str(self.password))
            obj['result']['password'] = encry_obj["password"]
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
                'Cookie' : 'ECS_ReqInfo_login1=' + self.loginInfo  +';EcsCaptchaKey='+ self.session.cookies['EcsCaptchaKey']  
            }
            ##self.session.cookies["ECS_ReqInfo_login1"] = "U2FsdGVkX196M7FM0p64n8M+z1I12RQm+Bca/XNBE0ElXoV6BF2yUkGvqWFQSeCNFdcTLxKln7nOqrBYWi32Lgh3o9IPg4ReDihEJ1iITFk="
            
           
    #         print(str(self.password))
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
            
            url = 'http://login.189.cn/web/login' 
            getLoginresp = self.session.post(url, data = login_post_data, headers = headerStr, verify = False, timeout = None) 
            #print(getLoginresp.text)
    #         print("LOGGINNN PAGE")
    #         print(self.session.cookies)
    #         print(getLoginresp.url)# if Fail url http://login.189.cn/login
    #         print(getLoginresp.url.find("UamTO.do"))
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
    #             print(getEcsurl)
                getEcsresp = self.session.get(getEcsurl, headers = headerStr1, verify = True, allow_redirects = True, timeout = None)
                #print(getEcsresp.text)
    #             print(getEcsresp.cookies)
                #time.sleep(10)
    #             print(self.session.cookies)
                dataResult = {
                            "result": "true",
                            "msg": ''
                        }
                return dataResult
            elif(getLoginresp.url.find("login.189.cn") > 0):
                respSoup = BeautifulSoup(getLoginresp.text,'html.parser')
                nameTags = respSoup.findAll('form',{"data-errmsg":True})
                #print(nameTags)
                errorMsg = "loginerror"
                data_resultcode = ""
                for n in nameTags:
                    errorMsg = (n['data-errmsg'])
                    data_resultcode = str(n['data-resultcode'])
                    
                dataResult = {
                    "result": "false",
                    "msg":errorMsg,
                    "data_resultcode" : data_resultcode
                }
                CTCC.uploadException(self, username=self.username, step='dologin', errmsg = errorMsg)
                returnData = CTCC.init(self)
#                 returnData = json.loads(returnData)
                returnData['msg'] = errorMsg
                returnData["result"] =  "false"
                return returnData
        except Exception:
            print(traceback.format_exc())
            CTCC.uploadException(self, username=self.username, step='dologin', errmsg = traceback.format_exc())
            returnData = CTCC.init(self)
#             returnData = json.loads(returnData)
            returnData["result"] =  "false"
            returnData['msg'] = '统异常,请稍后重试,code:1005'
            return returnData
            
        
    def goFrontPage(self):
        try:
            time.sleep(2)
            self.result_info = {}
            self.result_info['ispCode'] = 'CTCC'
            self.result_info['ispName'] = '电信'
            self.result_info['ispProvince'] = '贵州'
            self.result_info['flow_no'] = self.flowNo
            self.result_info['phoneNum'] = self.username
            
            self.result_info['operator'] = '贵州电信'
            self.result_info['createTime'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.result_info['userInfo'] = {}
            self.result_info["billDetail"] = []
            self.result_info["paymentRecord"] = []
           # self.result_info['historyBillInf'] = []
            #billPageUrl = 'http://www.189.cn/dqmh/frontLinkSkip.do?method=skip&shopId=10011&toStUrl=http://js.189.cn/service/bill?tabFlag=billing4'
            billPageUrl = 'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353'
            billFrontPageHeader = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Cookie': 'aactgsh111220='+ self.session.cookies["aactgsh111220"] +';JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; SHOPID_COOKIEID=10011; loginStatus=logined;',
                'Host':'www.189.cn',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
#             print(billPageUrl)
            billPageUrlresp = self.session.get(billPageUrl, headers = billFrontPageHeader, verify = False) 
#             print(billPageUrlresp.url)
#             print("billPageUrlresp CHECK")
    #        respSoup = BeautifulSoup(billPageUrlresp.text,'html.parser')
            '''
            nameTags = respSoup.find('p',{"id":"xiugai"})
            nameSpan = BeautifulSoup(str(nameTags),'html.parser')
            nameSpan = (nameSpan.find('span').text).strip()
            self.result_info['userInfo']["name"] = str(nameSpan.split(" ")[0]).strip()'''
            
            getssolinkUrl = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10024&toStUrl=http://service.gz.189.cn/web/query.php?action=call&fastcode=00320353&cityCode=gz"
            ssoHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +';JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; SHOPID_COOKIEID=10011; loginStatus=logined;',
                    'Host':'www.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            ssoUrlresp = self.session.get(getssolinkUrl, headers = ssoHeader, verify = False) 
            
            
            '''getecsurl = "http://www.189.cn/login/sso/ecs.do?method=linkTo&platNo=10024&toStUrl=http://service.gz.189.cn/web/query.php?action=call&fastcode=00320353&cityCode=gz"
            ecsHeader = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +';JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; SHOPID_COOKIEID=10011; loginStatus=logined;',
                'Host':'www.189.cn',
                'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            ecsUrlresp = self.session.get(getecsurl, headers = ecsHeader, verify = False) 
            print(ecsUrlresp)
            print(ecsUrlresp.url)
            print("getssolinkUrl CHECK")
            print(self.session.cookies)'''
            
            #getECSSSOUrl = "http://www.189.cn/dqmh/ssoLink.do?method=linkTo&platNo=10024&toStUrl=http://service.gz.189.cn/web/query.php?action=call&fastcode=00320353&cityCode=gz"
            ECSSSOssoHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
#                     'Cookie':'ECSLoginReq='+ self.session.cookies["ECSLoginReq"] + ';ECSLoginToken='+ self.session.cookies["ECSLoginToken"] +' ;aactgsh111220='+ self.session.cookies["aactgsh111220"] +';JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; SHOPID_COOKIEID=10011; loginStatus=logined;',
                    'Host':'login.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            ECSSSOssoUrlresp = self.session.get(ssoUrlresp.url, headers = ECSSSOssoHeader, verify = False) 
           
            
            phpHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'aactgsh111220='+ self.session.cookies["aactgsh111220"] +';JSESSIONID-JT='+ self.session.cookies["JSESSIONID-JT"] +'; userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; cityCode=js; SHOPID_COOKIEID=10011; loginStatus=logined;',
                    'Host':'service.gz.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            phpUrlresp = self.session.get(ECSSSOssoUrlresp.url, headers = phpHeader, verify = False) 
           
            
            #chckUrl = "http://service.gz.189.cn/web/query.php?action=call&fastcode=00320353&cityCode=gz"
            chckHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie':'PHPSESSID='+ self.session.cookies["PHPSESSID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+  self.session.cookies["userId"]  +'; isLogin=logined; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=gz; SHOPID_COOKIEID=10024; ',
                    'Host':'service.gz.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            chckresp = self.session.get(phpUrlresp.url, headers = chckHeader, verify = False) 
            #print(chckresp.text)
            monthQueryRespHtml = BeautifulSoup(chckresp.text,'html.parser')
            QUERY_TYPETags = monthQueryRespHtml.findAll('select',{"name":"QUERY_TYPE"})
            QueryMonthlyTags = monthQueryRespHtml.findAll('input',{"name":"ACCTMONTH"}) 
    #        print(QUERY_TYPETags)
            try:
                respHtml = BeautifulSoup(str(QUERY_TYPETags[0]),'html.parser')
                self.QUERY_TYPE = []
                for option in respHtml.findAll('option'):
                    self.QUERY_TYPE.append(option['value'])
            except Exception:
                print("")
    #        print(self.QUERY_TYPE)
    
            self.monthVal = []
            for option in QueryMonthlyTags:
                monthselect = BeautifulSoup(str(option),'html.parser')
                self.monthVal.append(monthselect.find("input")["value"])
#             print(self.monthVal)
            return True

        except Exception:
            respText = traceback.format_exc() 
            print(traceback.format_exc())
            CTCC.uploadException(self, username=self.username, step='getDatas', errmsg = respText)
            
            return False
       
        
    def sendAndCheckMblCode(self):
        time.sleep(2)
        sendSmsUrl = "http://service.gz.189.cn/web/query.php?action=postsms"
        smsHeader = {
            'Accept':'text/plain, */*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'Content-Length':'0',
            'Content-Type':'text/plain;charset=UTF-8',
            'Cookie':'PHPSESSID='+ self.session.cookies["PHPSESSID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +'; userId='+  self.session.cookies["userId"]  +'; isLogin=logined; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +'; loginStatus=logined; cityCode=gz; SHOPID_COOKIEID=10024; ',
            'Host':'service.gz.189.cn',
            'Origin':'http://service.gz.189.cn',
            'Referer':'http://service.gz.189.cn/web/query.php?action=call&fastcode=00320353&cityCode=gz',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'
            }
        sendSms = self.session.post(sendSmsUrl, headers = smsHeader, verify = False) 
#        print(sendSms.text)
        smsTxt = sendSms.text
        data = {
                'status' : 'true',
                'step' : '1',
                'again' : 'true',
                'msg': '请输入短信验证码',
                'username': self.username,
                'words' : [
                        {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                    ]
            }
        return data
    
       
    def getDatas(self):
        time.sleep(1)
        try:
            usernameurl = 'http://www.189.cn/login/index.do'
            userHeader = {
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Cache-Control':'max-age=0',
                    'Connection':'keep-alive',
                    'Cookie':'JSESSIONID-JT='+ self.session.cookies['JSESSIONID-JT'] +'; aactgsh111220='+ self.session.cookies['aactgsh111220'] +'; userId='+ self.session.cookies['userId'] +'; isLogin=logined; .ybtj.189.cn='+ self.session.cookies['.ybtj.189.cn'] +'; loginStatus=logined; cityCode=gz; SHOPID_COOKIEID=10024;',
                    'Host':'www.189.cn',
                    'Referer':'http://www.189.cn/html/login/index.html',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            userResp = self.session.get(usernameurl, headers =  userHeader, verify = False)
            userResp = json.loads(userResp.text, encoding = 'utf-8')
            #if 'OperationStatus' in phoneCallListResp.keys() :
            if type(userResp) != int :#if phoneCallListResp != "-2" :
                if 'dataObject' in userResp.keys() :
                    self.result_info['userInfo']["name"] = userResp['dataObject']['nickName']
            
            self.result_info["userInfo"]["certNum"] = ""
            self.result_info["userInfo"]["certType"] = ""
            self.result_info["userInfo"]["address"] = ""
            self.result_info["userInfo"]["userName"] = ""
            self.result_info["userInfo"]["email"] = ""
            self.result_info["userInfo"]["inNetDate"] = ""
            self.result_info["userInfo"]["balance"] = "0"
            self.result_info["userInfo"]["oweFee"] = "0"
            self.result_info["userInfo"]["status"] = "0"
            
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
            #self.result_info['phone_no'] = self.username
            #self.result_info['userInfo'] = userInfo
      ###      self.result_info['phoneInfo'] = phoneInfo
            
            #phonebalance
            getActionUrl = "http://service.gz.189.cn/web/query.php?action=acctList"
            getActionHeader = {
                    'Accept':'text/html, */*',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Cookie': 'PHPSESSID='+ self.session.cookies["PHPSESSID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;',
                    'Host':'service.gz.189.cn',
                    'Referer':'http://service.gz.189.cn/web/query.php?fastcode=0032&cityCode=gz',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                    'X-Requested-With':'XMLHttpRequest'
                }
            getActionResp = self.session.get(getActionUrl, headers = getActionHeader,  verify = False, timeout = None) 
            Balance = "0"
            realOweAmount = "0"
            try:
                actionHtml = BeautifulSoup(getActionResp.text,'html.parser')
                RadioGroup1 = actionHtml.findAll('input',{"name":"RadioGroup1"}) 
    #             print(RadioGroup1[0]["rel"])

            
                signclass = str(RadioGroup1[0]["class"])
    #             print(signclass[2:len(signclass)-2])
                
                getbalanceURL = "http://service.gz.189.cn/web/query.php?action=getAcctBill"
                getbalHeader = {
                        'Accept':'application/json, text/javascript, */*',
                        'Accept-Encoding':'gzip, deflate',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Content-Length':'64',
                        'Content-Type':'application/x-www-form-urlencoded',
                        'Cookie':'PHPSESSID='+ self.session.cookies["PHPSESSID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;',
                        'Host':'service.gz.189.cn',
                        'Origin':'http://service.gz.189.cn',
                        'Referer':'http://service.gz.189.cn/web/query.php?fastcode=0032&cityCode=gz',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest'
                    }
                getBal_postData = {
                        'data':RadioGroup1[0]["rel"],
                        'sign':signclass[2:len(signclass)-2]
                    }
                getbalResp = self.session.post(getbalanceURL, data = getBal_postData, headers = getbalHeader,  verify = False, timeout = None) 
                #print(getbalResp.text)
                Balance = "0"
                realOweAmount = "0"
                
                
                try:
                    getbalResp = json.loads(getbalResp.text, encoding = 'utf-8')
                    realOweAmount = "0"
                    Balance = "0"
                    if 'realOweAmount' in getbalResp.keys():
                        realOweAmount = getbalResp["realOweAmount"]
                    if 'Balance' in getbalResp.keys():
                        Balance = getbalResp["Balance"]
                except Exception:
                    CTCC.uploadException(self, username=self.username, step='getbalResp', errmsg = str(getbalResp.text))
            except Exception:
                CTCC.uploadException(self, username=self.username, step='getActionResp', errmsg = str(getActionResp.text))
            
            getPackageUrl = "http://service.gz.189.cn/web/query.php?action=business&fastcode=00320356&cityCode=gz"
            packageHeader = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    'Host':'service.gz.189.cn',
                    'Referer':'http://www.189.cn/dqmh/my189/initMy189home.do?fastcode=00320353',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }
            packageListResp = self.session.get(getPackageUrl, headers = packageHeader,  verify = False, timeout = None) 
            packageListRespHTML = BeautifulSoup(packageListResp.text,'html.parser')
            Tags = packageListRespHTML.findAll('ul',{"class":"jb"})
            LiTags = BeautifulSoup(str(Tags[0]),'html.parser').findAll('li')
            packageArr = []
            for items in LiTags:
                packageArr.append(items.text)
                
            #print(packageArr)
            
            
            phoneInfo = {
                "status":'OK',
                "serviceLevel": '',
                "inNetDate": '',
                "pointValue":'',
                "totalCreditValue": '',
                "basicMonthFee":'',
                "realMoney": realOweAmount,
                "balance" : Balance,
                "packageInfos": packageArr
              }
            Balance = str(int(float(Balance) * 100)) 
            realOweAmount = str(int(float(realOweAmount) * 100)) 
            self.result_info["userInfo"]["balance"] = Balance
            self.result_info["userInfo"]["oweFee"] = realOweAmount

            #Phone CALL 
            getCallVoiceListUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getAllCall&QueryMonthly='+ self.monthVal[0] +'&QueryType=1&checkcode='+self.mblCode
            callVoiceListHeader = {
                'Accept':'application/json, text/javascript, */*',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Type':'application/x-www-form-urlencoded',
                'Host':'service.gz.189.cn',
                'Referer':'http://service.gz.189.cn/web/query.php?action=call&fastcode=00320353&cityCode=gz',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest',
                'Cookie': 'PHPSESSID='+ self.session.cookies["PHPSESSID"] +';aactgsh111220='+ self.session.cookies["aactgsh111220"] +';userId='+ self.session.cookies["userId"] +'; .ybtj.189.cn='+ self.session.cookies[".ybtj.189.cn"] +';isLogin=logined; cityCode=js_xz; SHOPID_COOKIEID=10011; loginStatus=logined;'
                }
            
            phoneCallListResp = self.session.get(getCallVoiceListUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
            #print(phoneCallListResp.text)
            try:
                pattern = re .compile(r'\{.*\}')
                tmpval = re.findall(pattern, str(phoneCallListResp.text))
                if tmpval and len(tmpval) > 0:
                    dbt = tmpval[0]
                else:
                    dbt = phoneCallListResp.text
                    
                phoneCallListResp = json.loads(str(dbt), encoding = 'utf-8')
            except Exception:
                CTCC.uploadException(self, username=self.username, step='phoneCallListResp', errmsg = str(phoneCallListResp.text))
                phoneCallListResp = {}
            #if 'OperationStatus' in phoneCallListResp.keys() :
            if type(phoneCallListResp)  is dict  :#if phoneCallListResp != "-2" :
                phoneDetail = []
                if 'CDMA_CALL_CDR' in phoneCallListResp.keys() :
                    CDMA_CALL_CDR = phoneCallListResp["CDMA_CALL_CDR"]
                    if(type(CDMA_CALL_CDR) is list):
                        for item in CDMA_CALL_CDR:
                            phoneListObj = {}
                            dateval = item["START_DATE"][0:10]
                            timeval = item["START_DATE"][11:len(item["START_DATE"])]
                            callType = str(item["CALLING_TYPE_NAME"]).strip()
                            callTypestr = ""
                            if( callType.find("主叫") == -1 ):
                                if( callType.find("被叫") != -1 ):
                                    callTypestr = "被叫"  
                            else:
                                callTypestr = "主叫"  
                            
                            commType = item["NAME"]
                            commPhoneNo = item["ORG_CALLED_NBR"]
                            commDate  = dateval
                            endDatestr = time.strptime(commDate,"%Y-%m-%d")
                            commDate = time.strftime("%Y%m%d",endDatestr)
                            commTotalTime  = item["DURATION"]
                            cost = item["FEE2"]
                            costVal = int(float(cost))
                            commTime  = timeval
                            endDatestr = time.strptime(timeval,"%H:%M:%S")
                            commTime = time.strftime("%H%M%S",endDatestr)
                            if( type(item["ROAMING_AREA"]) is list):        
                                activeCommAddr = ''        
                            else:        
                                activeCommAddr = item["ROAMING_AREA"]
                                
                            phoneListObj["callTypeName"] = str(callTypestr)
                            phoneListObj["callPlace"] = str(activeCommAddr)
                            phoneListObj["otherPhoneNum"] = str(commPhoneNo)
                            phoneListObj["startDate"] = str(commDate)
                            phoneListObj["startTime"] = str(commTime)
                            phoneListObj["totalTime"] = str(commTotalTime)
                            phoneListObj["totalFee"] = str(int(costVal))
                            phoneListObj["commType"] = str(commType)
                            phoneDetail.append(phoneListObj)
                    else:    
                        phoneListObj = {}    
                        item = CDMA_CALL_CDR
                        dateval = item["START_DATE"][0:10]
                        timeval = item["START_DATE"][11:len(item["START_DATE"])]
                        callType = str(item["CALLING_TYPE_NAME"]).strip()
                        callTypestr = ""
                        if( callType.find("主叫") == -1 ):
                            if( callType.find("被叫") != -1 ):
                                callTypestr = "被叫"  
                        else:
                            callTypestr = "主叫"  
                        
                        commType = item["NAME"]
                        commPhoneNo = item["ORG_CALLED_NBR"]
                        commDate  = dateval
                        endDatestr = time.strptime(commDate,"%Y-%m-%d")
                        commDate = time.strftime("%Y%m%d",endDatestr)
                        commTotalTime  = item["DURATION"]
                        cost = item["FEE2"]
                        costVal = int(float(cost))
                        commTime  = timeval
                        endDatestr = time.strptime(timeval,"%H:%M:%S")
                        commTime = time.strftime("%H%M%S",endDatestr)
                        activeCommAddr = item["ROAMING_AREA"]
                        if( type(item["ROAMING_AREA"]) is list):        
                                activeCommAddr = ''        
                        else:        
                            activeCommAddr = item["ROAMING_AREA"]
                                
                        phoneListObj["callTypeName"] = str(callTypestr)
                        phoneListObj["callPlace"] = str(activeCommAddr)
                        phoneListObj["otherPhoneNum"] = str(commPhoneNo)
                        phoneListObj["startDate"] = str(commDate)
                        phoneListObj["startTime"] = str(commTime)
                        phoneListObj["totalTime"] = str(commTotalTime)
                        phoneListObj["totalFee"] = str(int(costVal))
                        phoneListObj["commType"] = str(commType)
                        phoneDetail.append(phoneListObj)
                
                #SMS List
                getSMSListUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getAllCall&QueryMonthly='+ self.monthVal[0] +'&QueryType=2&checkcode='+self.mblCode
                smsListResp = self.session.get(getSMSListUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                #print(smsListResp.text)
                SMSDetail = []
                smsListResp = json.loads(smsListResp.text, encoding = 'utf-8')
                if type(smsListResp) is dict :
                    if 'CDMA_SMS_CDR' in smsListResp.keys() :
                        CDMA_SMS_CDR = smsListResp["CDMA_SMS_CDR"]
                        try:
                            if(type(CDMA_SMS_CDR) is list):
                                for item in CDMA_SMS_CDR:
                                    dateval = item["START_DATE"][0:10]
                                    endDatestr = time.strptime(dateval,"%Y-%m-%d")
                                    dateval = time.strftime("%Y%m%d",endDatestr)
                                    timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                    endDatestr = time.strptime(timeval,"%H:%M:%S")
                                    timeval = time.strftime("%H%M%S",endDatestr)
                                    msgDate  = dateval
                                    msgPhone  = item["ORG_CALLED_NBR"]
                                    sendType  = item["CALLING_TYPE_NAME"]
                                    cost = str(int(item["FEE2"]) )
                                    place = item["CALLED_AREA"]
                                    SMSDetail.append({
                                        "smsType": sendType,
                                        "otherPhoneNum": msgPhone,
                                        "smsDate": msgDate,
                                        "smsTime": timeval,
                                        "totalFee": cost,
                                        "place": place
                                        })
                            else:
                                item = CDMA_SMS_CDR
                                dateval = item["START_DATE"][0:10]
                                endDatestr = time.strptime(dateval,"%Y-%m-%d")
                                dateval = time.strftime("%Y%m%d",endDatestr)
                                timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                endDatestr = time.strptime(timeval,"%H:%M:%S")
                                timeval = time.strftime("%H%M%S",endDatestr)
                                msgDate  = dateval
                                msgPhone  = item["ORG_CALLED_NBR"]
                                sendType  = item["CALLING_TYPE_NAME"]
                                cost = str(int(item["FEE2"]) )
                                place = item["CALLED_AREA"]
                                SMSDetail.append({
                                    "smsType": sendType,
                                    "otherPhoneNum": msgPhone,
                                    "smsDate": msgDate,
                                    "smsTime": timeval,
                                    "totalFee": cost,
                                    "place": place
                                    })
                        except Exception:
                            respText = traceback.format_exc() 
                            CTCC.uploadException(self, username=self.username, step='smsListResp', errmsg = str(CDMA_SMS_CDR) + str(respText))
                            
                #DATALIST
                getDataListUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getAllCall&QueryMonthly='+ self.monthVal[0] +'&QueryType=4&checkcode='+self.mblCode
                dataListResp = self.session.get(getDataListUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                #print(dataListResp.text)
                netDetail = []
                dataListResp1 = json.loads(dataListResp.text, encoding = 'utf-8')
                if type(dataListResp1) is dict :
                    if 'CDMA_DATA_CDR' in dataListResp1.keys() :
                        CDMA_DATA_CDR = dataListResp1["CDMA_DATA_CDR"]
                        if(type(CDMA_DATA_CDR) is list):
                            for item in CDMA_DATA_CDR:
                                dateval = item["START_DATE"][0:10]
                                timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                totalTime   = item["DURATION"]
                                netTime  = timeval
                                netDate   = dateval
                                netType   = item["NETWORK_TYPE"]
                                netMoney  = str(int(item["FEE2"])  )
                                netFlow  = item["AMOUNT"]
                                endDatestr = time.strptime(item["START_DATE"],"%Y-%m-%d %H:%M:%S")
                                netDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                                
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
                                
                                netDetail.append({
                                    "netType": netType,
                                    "startTime": netDate,
                                    "totalTime": totalTime,
                                    "totalFee": netMoney,
                                    "totalTraffic": netTraffic,
                                    "netPlace":""
                                    })
                        else:
                            item = CDMA_DATA_CDR
                            dateval = item["START_DATE"][0:10]
                            timeval = item["START_DATE"][11:len(item["START_DATE"])]
                            totalTime   = item["DURATION"]
                            netTime  = timeval
                            netDate   = dateval
                            netType   = item["NETWORK_TYPE"]
                            netMoney  = str(int(item["FEE2"])  )
                            netFlow  = item["AMOUNT"]
                            endDatestr = time.strptime(item["START_DATE"],"%Y-%m-%d %H:%M:%S")
                            netDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                            
                            
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
                            
                            netDetail.append({
                                "netType": netType,
                                "startTime": netDate,
                                "totalTime": totalTime,
                                "totalFee": netMoney,
                                "totalTraffic": str(netTraffic),
                                "netPlace":""
                                })
                    
                #Payment Record
                yearVal = int(self.monthVal[0][0:4])
                monthVal = int(self.monthVal[0][4:6])
                lastDayMonth = calendar.monthrange(yearVal,monthVal)[1]
                QueryMonthly1 = str(self.monthVal[0]) + '01'
                QueryMonthly2 =  str(self.monthVal[0]) + str(lastDayMonth)
                paymentUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getNewPay&QueryMonthly1='+ QueryMonthly1 +'&QueryMonthly2='+QueryMonthly2
                paymentResp = self.session.get(paymentUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                #print(paymentResp.text)
                paymentRecord  = []
                if(paymentResp.text != "null"):
                    paymentResp = json.loads(paymentResp.text, encoding = 'utf-8')
                    
                    print(type(paymentResp))
                    if (type(paymentResp) is list):
                        for item in paymentResp:
                            payDate = item["PaymentDate"] 
                            payFee = item["Amount"]
                            payFeeVal = int(float(payFee))
                            payChannel  = item["PaymentMethod"]
                            #td[1]
                            billDate = payDate[0:8]
                            billTime = payDate[8: len(payDate)]
                            paymentRecord.append({
                                "billDate": billDate,
                                "billTime": billTime,
                                "billFee": payFeeVal,
                                "busiName": payChannel  
                                })
                    elif (type(paymentResp) is dict):
                        item = paymentResp
                        payDate = item["PaymentDate"] 
                        payFee = item["Amount"]
                        payFeeVal = int(float(payFee))
                        payChannel  = item["PaymentMethod"]
                        
                        billDate = payDate[0:8]
                        billTime = payDate[8: len(payDate)]
                        paymentRecord.append({
                            "billDate": billDate,
                            "billTime": billTime,
                            "billFee": payFeeVal,
                            "busiName": payChannel  
                            })
                
#                 print(len(self.monthVal))
                for val in range(1, len(self.monthVal)):
                    try:
#                        time.sleep(5)
#                         print("inside")
                        getCallVoiceListUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getAllCall&QueryMonthly='+ str(self.monthVal[val]) +'&QueryType=1&checkcode='+self.mblCode
                        phoneCallListResp = self.session.get(getCallVoiceListUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                        #print(phoneCallListResp.text)
                        try:
                            pattern = re .compile(r'\{.*\}')
                            tmpval = re.findall(pattern, str(phoneCallListResp.text))
                            if tmpval and len(tmpval) > 0:
                                dbt = tmpval[0]
                            else:
                                dbt = phoneCallListResp.text
                                
                            phoneCallListResp = json.loads(str(dbt), encoding = 'utf-8')
                        except Exception:
                            CTCC.uploadException(self, username=self.username, step='phoneCallListResp', errmsg = str(phoneCallListResp.text))
                            phoneCallListResp = {}
                        if type(phoneCallListResp) is dict:#if phoneCallListResp != "-2" :
                            if 'CDMA_CALL_CDR' in phoneCallListResp.keys() :
                                CDMA_CALL_CDR = phoneCallListResp["CDMA_CALL_CDR"]
                                if(type(CDMA_CALL_CDR) is list):
                                    for item in CDMA_CALL_CDR:
                                        phoneListObj = {}
                                        dateval = item["START_DATE"][0:10]
                                        timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                        callType = str(item["CALLING_TYPE_NAME"]).strip()
                                        callTypestr = ""
                                        if( callType.find("主叫") == -1 ):
                                            if( callType.find("被叫") != -1 ):
                                                callTypestr = "被叫"  
                                        else:
                                            callTypestr = "主叫"  
                                        
                                        commType = item["NAME"]
                                        commPhoneNo = item["ORG_CALLED_NBR"]
                                        commDate  = dateval
                                        endDatestr = time.strptime(commDate,"%Y-%m-%d")
                                        commDate = time.strftime("%Y%m%d",endDatestr)
                                        commTotalTime  = item["DURATION"]
                                        cost = item["FEE2"]
                                        costVal = int(float(cost))
                                        commTime  = timeval
                                        endDatestr = time.strptime(timeval,"%H:%M:%S")
                                        commTime = time.strftime("%H%M%S",endDatestr)
                                        activeCommAddr = item["ROAMING_AREA"]
                                        if( type(item["ROAMING_AREA"]) is list):        
                                                activeCommAddr = ''        
                                        else:        
                                            activeCommAddr = item["ROAMING_AREA"]
                                                
                                        phoneListObj["callTypeName"] = str(callTypestr)
                                        phoneListObj["callPlace"] = str(activeCommAddr)
                                        phoneListObj["otherPhoneNum"] = str(commPhoneNo)
                                        phoneListObj["startDate"] = str(commDate)
                                        phoneListObj["startTime"] = str(commTime)
                                        phoneListObj["totalTime"] = str(commTotalTime)
                                        phoneListObj["totalFee"] = str(costVal)
                                        phoneListObj["commType"] = str(commType)
                                        phoneDetail.append(phoneListObj)
                                else:
                                    phoneListObj = {}
                                    item = CDMA_CALL_CDR
                                    dateval = item["START_DATE"][0:10]
                                    timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                    callType = str(item["CALLING_TYPE_NAME"]).strip()
                                    callTypestr = ""
                                    if( callType.find("主叫") == -1 ):
                                        if( callType.find("被叫") != -1 ):
                                            callTypestr = "被叫"  
                                    else:
                                        callTypestr = "主叫"  
                                    
                                    commType = item["NAME"]
                                    commPhoneNo = item["ORG_CALLED_NBR"]
                                    commDate  = dateval
                                    endDatestr = time.strptime(commDate,"%Y-%m-%d")
                                    commDate = time.strftime("%Y%m%d",endDatestr)
                                    commTotalTime  = item["DURATION"]
                                    cost = item["FEE2"]
                                    costVal = int(float(cost))
                                    commTime  = timeval
                                    endDatestr = time.strptime(timeval,"%H:%M:%S")
                                    commTime = time.strftime("%H%M%S",endDatestr)
                                    activeCommAddr = item["ROAMING_AREA"]
                                    if( type(item["ROAMING_AREA"]) is list):        
                                            activeCommAddr = ''        
                                    else:        
                                        activeCommAddr = item["ROAMING_AREA"]
                                            
                                    phoneListObj["callTypeName"] = str(callTypestr)
                                    phoneListObj["callPlace"] = str(activeCommAddr)
                                    phoneListObj["otherPhoneNum"] = str(commPhoneNo)
                                    phoneListObj["startDate"] = str(commDate)
                                    phoneListObj["startTime"] = str(commTime)
                                    phoneListObj["totalTime"] = str(commTotalTime)
                                    phoneListObj["totalFee"] = str(costVal)
                                    phoneListObj["commType"] = str(commType)
                                    phoneDetail.append(phoneListObj)
                        #SMS List
                        getSMSListUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getAllCall&QueryMonthly='+ self.monthVal[val] +'&QueryType=2&checkcode='+self.mblCode
                        smsListResp = self.session.get(getSMSListUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                        #print(smsListResp.text)
                        smsListResp = json.loads(smsListResp.text, encoding = 'utf-8')
                        if type(smsListResp) is dict :
                            if 'CDMA_SMS_CDR' in smsListResp.keys() :
                                CDMA_SMS_CDR = smsListResp["CDMA_SMS_CDR"]
                                try:
                                    if(type(CDMA_SMS_CDR) is list):
                                        for item in CDMA_SMS_CDR:
                                            dateval = item["START_DATE"][0:10]
                                            endDatestr = time.strptime(dateval,"%Y-%m-%d")
                                            dateval = time.strftime("%Y%m%d",endDatestr)
                                            timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                            endDatestr = time.strptime(timeval,"%H:%M:%S")
                                            timeval = time.strftime("%H%M%S",endDatestr)
                                            msgDate  = dateval
                                            msgPhone  = item["ORG_CALLED_NBR"]
                                            sendType  = item["CALLING_TYPE_NAME"]
                                            cost = str(int(item["FEE2"])  )
                                            place = item["CALLED_AREA"]
                                            SMSDetail.append({
                                                "smsType": sendType,
                                                "otherPhoneNum": msgPhone,
                                                "smsDate": msgDate,
                                                "smsTime": timeval,
                                                "totalFee": cost,
                                                "place": place
                                                })
                                    else:
                                        item = CDMA_SMS_CDR
                                        dateval = item["START_DATE"][0:10]
                                        endDatestr = time.strptime(dateval,"%Y-%m-%d")
                                        dateval = time.strftime("%Y%m%d",endDatestr)
                                        timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                        endDatestr = time.strptime(timeval,"%H:%M:%S")
                                        timeval = time.strftime("%H%M%S",endDatestr)
                                        msgDate  = dateval
                                        msgPhone  = item["ORG_CALLED_NBR"]
                                        sendType  = item["CALLING_TYPE_NAME"]
                                        cost = str(int(item["FEE2"]))
                                        place = item["CALLED_AREA"]
                                        SMSDetail.append({
                                            "smsType": sendType,
                                            "otherPhoneNum": msgPhone,
                                            "smsDate": msgDate,
                                            "smsTime": timeval,
                                            "totalFee": cost,
                                            "place": place
                                            })
                                except Exception:
                                    respText = traceback.format_exc() 
                                    CTCC.uploadException(self, username=self.username, step='smsListResp', errmsg = str(CDMA_SMS_CDR) + str(respText))
                        
                        #DATA List
                        getDataListUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getAllCall&QueryMonthly='+ self.monthVal[val] +'&QueryType=4&checkcode='+self.mblCode
                        dataListResp = self.session.get(getDataListUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                        #print(dataListResp.text)
                        dataListResp = json.loads(dataListResp.text, encoding = 'utf-8')
                        if type(dataListResp) is dict :
                            if 'CDMA_DATA_CDR' in dataListResp.keys() :
                                CDMA_DATA_CDR = dataListResp["CDMA_DATA_CDR"]
                                if(type(CDMA_DATA_CDR) is list):
                                    for item in CDMA_DATA_CDR:
                                        dateval = item["START_DATE"][0:10]
                                        timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                        totalTime   = item["DURATION"]
                                        netTime  = timeval
                                        netDate   = dateval
                                        netType   = item["NETWORK_TYPE"]
                                        netMoney  = str(int(item["FEE2"])  )
                                        netFlow  = item["AMOUNT"]
                                        endDatestr = time.strptime(item["START_DATE"],"%Y-%m-%d %H:%M:%S")
                                        netDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                                        
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
                                        
                                        netDetail.append({
                                            "netType": netType,
                                            "startTime": netDate,
                                            "totalTime": totalTime,
                                            "totalFee": netMoney,
                                            "totalTraffic": str(netTraffic),
                                            "netPlace":""
                                            })
                                else:
                                    item = CDMA_DATA_CDR
                                    dateval = item["START_DATE"][0:10]
                                    timeval = item["START_DATE"][11:len(item["START_DATE"])]
                                    totalTime   = item["DURATION"]
                                    netTime  = timeval
                                    netDate   = dateval
                                    netType   = item["NETWORK_TYPE"]
                                    netMoney  = str(int(item["FEE2"]) )
                                    netFlow  = item["AMOUNT"]
                                    endDatestr = time.strptime(item["START_DATE"],"%Y-%m-%d %H:%M:%S")
                                    netDate = time.strftime("%Y%m%d%H%M%S",endDatestr)
                                    
                                    
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
                                    
                                    netDetail.append({
                                        "netType": netType,
                                        "startTime": netDate,
                                        "totalTime": totalTime,
                                        "totalFee": netMoney,
                                        "totalTraffic": str(netTraffic),
                                        "netPlace":""
                                        })
                        
                        #Payment Record
                        yearVal = int(self.monthVal[val][0:4])
                        monthVal = int(self.monthVal[val][4:6])
                        lastDayMonth = calendar.monthrange(yearVal,monthVal)[1]
                        QueryMonthly1 = str(self.monthVal[val]) + '01'
                        QueryMonthly2 =  str(self.monthVal[val]) + str(lastDayMonth)
                        paymentUrl = 'http://service.gz.189.cn/web/query.php?_='+ str(round(time.time() * 1000)) +'&action=getNewPay&QueryMonthly1='+ QueryMonthly1 +'&QueryMonthly2='+QueryMonthly2
                        paymentResp = self.session.get(paymentUrl, headers = callVoiceListHeader,  verify = False, timeout = None) 
                        #print(paymentResp.text)
                        if(paymentResp.text != "null"):
                            paymentResp = json.loads(paymentResp.text, encoding = 'utf-8')
                            print(type(paymentResp))
                            if (type(paymentResp) is list):
                                for item in paymentResp:
                                    payDate = item["PaymentDate"] 
                                    payFee = int(float(item["Amount"]) )
                                    payChannel  = item["PaymentMethod"]
                                    
                                    billDate = payDate[0:8]
                                    billTime = payDate[8: len(payDate)]
                                    paymentRecord.append({
                                        "billDate": billDate,
                                        "billTime": billTime,
                                        "billFee": payFee,
                                        "busiName": payChannel  
                                        })
                            elif (type(paymentResp) is dict):
                                item = paymentResp  
                                payDate = item["PaymentDate"] 
                                payFee = int(float(item["Amount"]) )
                                payChannel  = item["PaymentMethod"]
                                
                                billDate = payDate[0:8]
                                billTime = payDate[8: len(payDate)]
                                paymentRecord.append({
                                    "billDate": billDate,
                                    "billTime": billTime,
                                    "billFee": payFee,
                                    "busiName": payChannel  
                                    })
                    except:
                        respText = traceback.format_exc()
                        CTCC.uploadException(self, username=self.username, step='doCapture', errmsg=respText)
                        returnData = CTCC.init(self)        
                        returnData['msg'] = '系统错误！ 请退出输入'        
                        return returnData


                        
                #print("out of loop")
                
                
                #print(phoneDetail)
                #print(SMSDetail)
                #print(netDetail)
                self.result_info["billDetail"] = paymentRecord
                #self.result_info["phoneInfo"] = phoneInfo
                self.result_info["callDetail"] = phoneDetail
                self.result_info["smsDetail"] = SMSDetail
                self.result_info["netDetail"] = netDetail
                #print(self.result_info)
                if self.result_info :
                    print('-----------CTCC Successful List------------')
                    self.isSuccess = self.uploadData( self, self.result_info)
                    if self.isSuccess :
                        returnData = { 
                            'status' : 'true' ,
                            'again' : 'false' ,
                            'msg' : 'success'
                        }
                        CTCC.uploadException(self, self.username, 'Upload Data', 'Upload Data Success')
                        return returnData
                    else:
                        returnData = { 
                            'status' : 'true' ,
                            'again' : 'false' ,
                            'msg' : 'false'
                        }
                        return returnData
            else:
                '''data = {
                            'status' : 'true',
                            'step' : '1',
                            'again' : 'true',
                            'msg':'服务密码或短信验证码错误',
                            'username': self.username,
                            'words' : [
                                    {'ID' : 'smsPwd' , 'index' : '1' , 'needEncrypt' : False , 'needUserInput' : True , 'label' : '短信验证码' , 'type' : 'smsPwd'}
                                ]
                        }'''
                CTCC.uploadException(self, username=self.username, step='checksms', errmsg = '服务密码或短信验证码错误')
                returnData = CTCC.init(self)        
                returnData['msg'] = '服务密码或短信验证码错误'        
                return returnData
            
            #
        except Exception:
            respText = traceback.format_exc() 
            CTCC.uploadException(self, username=self.username, step='getDatas', errmsg = respText)
            returnData = CTCC.init(self)
#             returnData = json.loads(returnData)
            returnData['msg'] = '系统繁忙,请稍后重试,code:100'
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


