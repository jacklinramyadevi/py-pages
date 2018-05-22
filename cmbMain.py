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


from bank import cmb
cmbBank = cmb.Bank()
res_json = cmbBank.init()
print(res_json)
print('****************************************** \n')


DEBUG_FLAG = '0'
DEBUG_LOCAL = '1'

def step0(UserId,password):
    jsonParams = {}
    jsonParams['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
    jsonParams['step'] = '0'
    jsonParams['AccountNo'] = UserId
    jsonParams['Password'] = password
    jsonParams['DEBUG'] = DEBUG_FLAG
    jsonParams['DEBUG_LOCAL'] = DEBUG_LOCAL
    #return json.dumps(jsonParams)
    return cmbBank.doCapture(json.dumps(jsonParams))

def step1(PicCode):
    jsonParams = {}
    jsonParams['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
    jsonParams['verifycode'] = PicCode
    jsonParams['step'] = '4'
    #return json.dumps(jsonParams)
    return cmbBank.doCapture(json.dumps(jsonParams))

def step2(smsCode,verifyCode):
    jsonParams = {}
    jsonParams['flowNo'] = 'aa3a464e12704f579a3c1afdc6bf1aee'
    jsonParams['smsCode'] = smsCode
    jsonParams['verifyCode'] = verifyCode
    jsonParams['step'] = '2'
    #return json.dumps(jsonParams)
    return cmbBank.doCapture(json.dumps(jsonParams))

UserId = '6225887801108016'
password = '205896'


'''
UserId = '18639499811'
password = 'qwer1234'
'''
''' 
UserId = '13760369175'
password = '714807'
'''

# UserId = raw_input('Please Input to CMB AccountNo:')
# password = raw_input('Please Input to CMB Password:')
res_json = step0(UserId,password)
print('randomId:'+res_json)
print('****************************************** \n')

smsCode = raw_input('Please Input to CMB smsCode:')


res_json = step1(smsCode)
print(res_json)

'''
smsCode = raw_input('Please Input to ICBC smsCode:')
verifyCode = raw_input('Please Input to ICBC verifyCode:')
res_json = step2(smsCode,verifyCode)'''



