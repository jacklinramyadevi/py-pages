#coding=utf-8
import datetime
import json
import pdb
import re
import time

from pip._vendor.distlib.compat import raw_input

from Pybridge import SpiderRouter

 
 
spiderRouter = SpiderRouter()

print('aaaa')

jsonParam = {
        'type':'telecommunications', 
        'name': 'teletest',
        'class':'Chinamobile'
    }


from mail import mail139
email = mail139.Crawler()
res_json = email.init()
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
    jsonParams['debug'] = True
    #return json.dumps(jsonParams)
    return email.doCapture(json.dumps(jsonParams))

def step1(PicCode,URI):
    jsonParams = {}
    jsonParams['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
    jsonParams['PicCode'] = PicCode
    jsonParams['step'] = '1'
    #return json.dumps(jsonParams)
    return email.doCapture(json.dumps(jsonParams))

def step2(smsCode,verifyCode):
    jsonParams = {}
    jsonParams['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
    jsonParams['smsCode'] = smsCode
    jsonParams['verifyCode'] = verifyCode
    jsonParams['step'] = '2'
    #return json.dumps(jsonParams)
    return email.doCapture(json.dumps(jsonParams))
 
UserId = '13145883278@139.com'
password = 'Dakshan04'

# UserId = raw_input('Please Input to CMB AccountNo:')
# password = raw_input('Please Input to CMB Password:')
res_json = step0(UserId,password)
print(res_json)
print('****************************************** \n')





