#coding=utf-8
import datetime
import json
import pdb
import re
import time

from pip._vendor.distlib.compat import raw_input

from Pybridge import SpiderRouter
import base64

 
 
spiderRouter = SpiderRouter()

print('aaaa')


from bank import pab
pinganBank = pab.Bank()
res_json = pinganBank.init()
print(res_json)
print('****************************************** \n')

DEBUG_FLAG = '0'
DEBUG_LOCAL = '1'

def step0(UserId,password):
    jsonParams = {}
    jsonParams['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
    jsonParams['step'] = '0'
    jsonParams['UserId'] = UserId
    jsonParams['password'] = password
    jsonParams['DEBUG'] = DEBUG_FLAG
    jsonParams['DEBUG_LOCAL'] = DEBUG_LOCAL
    #return json.dumps(jsonParams)
    dataobj = pinganBank.doCapture(json.dumps(jsonParams))
    print(dataobj)
    dataobj = json.loads(json.dumps(dataobj))
    if (dataobj["step"]== "0" and len(dataobj["words"]) == 3):
        #store it in local
        imgData = base64.b64decode(dataobj["words"][2]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
        
        piccode = raw_input("Please enter verify code: ")
        dataobj["piccode"] = piccode
        dataobj['UserId'] = UserId
        dataobj['password'] = raw_input("Please enter password: ")
        dataobj['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
        dataobj = pinganBank.doCapture(json.dumps(dataobj))
        print(dataobj)
    if (dataobj["step"]== "2" and len(dataobj["words"]) == 3):
        #store it in local
        imgData = base64.b64decode(dataobj["words"][2]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
        
        piccode = raw_input("Please enter verify code: ")
        dataobj["piccode"] = piccode
        dataobj['UserId'] = UserId
        dataobj['password'] = raw_input("Please enter password: ")
        dataobj['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
        dataobj = pinganBank.doCapture(json.dumps(dataobj))
        print(dataobj)
    if (dataobj["step"]== "2"):
        #store it in local
        imgData = base64.b64decode(dataobj["words"][0]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
        
        piccode = raw_input("Please enter verify code: ")
        dataobj["piccode"] = piccode
        
        dataobj['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
        dataobj = pinganBank.doCapture(json.dumps(dataobj))
        print(dataobj)
    if dataobj["step"] == "1":
        otp = raw_input("Please enter OTP: ")
        dataobj["otp"] = otp
        dataobj = pinganBank.doCapture(json.dumps(dataobj))
    
    

UserId = '440921199105133832'#'440921199105133832'#'13017283052'##'ninghualiang'
password = 'credit123'#'credit123'#'yx171229'#nhl200898
#UserId = '320721198205081432'#'440921199105133832'#'ninghualiang'
#password = 'liujiang0508'#'credit123'#nhl200898
#damonzhong135_hz2635819
#441623199205031013_zz076238
res_json = step0(UserId,password)
print('Pingan main ended')
print('******************************************')
