'''
Created on 2016骞�12鏈�3鏃�

@author: cary.zhu
'''

import json
from Pybridge import SpiderRouter
from pip._vendor.distlib.compat import raw_input
import base64
 
 
spiderRouter = SpiderRouter()
jsonParam = {
        'type':'telecommunications', 
        'name': 'ctcc_ln',#'ctcc_henan',
        'class':'CTCC'
    }
usernameParam = spiderRouter.init(json.dumps(jsonParam))
print(usernameParam)
data = {
        'username':'15326239089',#18083298002, 18937341036, 17327368034, 17387185069, 13337543061
        'password':'147951',#147987, 147258
        'mobile': '15326239089',
        'debug1': True,
        'flowNo':'b636c341169a4dd4be0b8e51e6725136',
        'step':'0'
    }

doCaptureResult = spiderRouter.execute(json.dumps(data))

print(doCaptureResult)
result = json.loads(doCaptureResult).get('result')
print(result)
step = json.loads(json.dumps(result)).get('step')
print(step)
if(jsonParam['name'] == 'ctcc_sx'):
    if(step == "4" ):
        words = json.loads(json.dumps(result)).get('words')
        dataobj = json.loads(json.dumps(result))
        ID = words[0]["ID"]
        print(ID)
        if(ID == "piccode"):
            imgData = base64.b64decode(dataobj["words"][0]["source"])
            fileName = 'C:/work/temp/resp.png'
            with open(fileName, 'wb') as f:
                f.write(imgData)  
        
        getSmsPassword = raw_input("Please input "+ ID +" code: ")
        result[ID] = getSmsPassword
        if(len(words) == 2):
            ID = words[1]["ID"]
            getSmsPassword = raw_input("Please input "+ ID +" code: ")
            result[ID] = getSmsPassword
        result = {}
        result['step'] =  step
        result[ID] = getSmsPassword
        params = {"status": "true", "result": result }
        params = result
        doCaptureResult1 = spiderRouter.execute(json.dumps(params))
        print("RESULT *****************")
        print(doCaptureResult1)
        result = json.loads(doCaptureResult1).get('result')
        print(result)
        step = json.loads(json.dumps(result)).get('step')
    if( step == '1' ):
        words = json.loads(json.dumps(result)).get('words')
        i = 0
        for val in words:
            ID = words[i]["ID"]
            if(ID == "piccode"):
                imgData = base64.b64decode(val["source"])
                fileName = 'C:/work/temp/resp.png'
                with open(fileName, 'wb') as f:
                    f.write(imgData)  
            piccode = raw_input("Please input "+ ID +" code: ")
            result[ID] = piccode
             
            i = i + 1
        params = {"status": "true", "result": result }
        doCaptureResult1 = spiderRouter.execute(json.dumps(params))
        print("RESULT *****************")
        print(doCaptureResult1)
        result = json.loads(doCaptureResult1).get('result')
        print(result)
        step = json.loads(json.dumps(result)).get('step')
        print(step)
        if(step == '2'):
            words = json.loads(json.dumps(result)).get('words')
            ID = words[0]["ID"]
            dataobj = json.loads(json.dumps(result))
            if(ID == "piccode"):
                imgData = base64.b64decode(dataobj["words"][0]["source"])
                fileName = 'C:/work/temp/resp.png'
                with open(fileName, 'wb') as f:
                    f.write(imgData)  
            piccode = raw_input("Please input "+ ID +" code: ")
            result[ID] = piccode
            params = {"status": "true", "result": result }
            doCaptureResult1 = spiderRouter.execute(json.dumps(params))
            print("RESULT *****************")
            print(doCaptureResult1)
            result = json.loads(doCaptureResult1).get('result')
            print(result)
            step = json.loads(json.dumps(result)).get('step')
            print(step)
        if(step == '3'):
            words = json.loads(json.dumps(result)).get('words')
            ID = words[0]["ID"]
            dataobj = json.loads(json.dumps(result))
            piccode = raw_input("Please input "+ ID +" code: ")
            result[ID] = piccode
            params = {"status": "true", "result": result }
            doCaptureResult1 = spiderRouter.execute(json.dumps(params))
            print("RESULT *****************")
            print(doCaptureResult1)
            
        
if( step == '0' ):
    getSmsPassword = raw_input("Please input sms code: ")
    result["password"] = getSmsPassword
    data = {
        'username':'13315923020',#18083298002, 18937341036, 17327368034, 17387185069, 13337543061
        'password': getSmsPassword,#147987, 147258
        'flowNo':'b636c341169a4dd4be0b8e51e6725136',
        'step':'0'
    }

    params = {"status": "true",'debug1': True, "result": data }
    doCaptureResult = spiderRouter.execute(json.dumps(data))
    
if(step == "3" ):
    words = json.loads(json.dumps(result)).get('words')
    dataobj = json.loads(json.dumps(result))
    ID = words[0]["ID"]
    print(ID)
    if(ID == "piccode"):
        imgData = base64.b64decode(dataobj["words"][0]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
    
    getSmsPassword = raw_input("Please input "+ ID +" code: ")
    result[ID] = getSmsPassword
    if(len(words) == 2):
        ID = words[1]["ID"]
        getSmsPassword = raw_input("Please input "+ ID +" code: ")
        result[ID] = getSmsPassword
    result = {}
    result['step'] =  step
    result[ID] = getSmsPassword
    params = {"status": "true", "result": result }
    params = result
    doCaptureResult1 = spiderRouter.execute(json.dumps(params))
    print("33 333 RESULT *****************")
    print(doCaptureResult1)
    result = json.loads(doCaptureResult1).get('result')
    print(result)
    step = json.loads(json.dumps(result)).get('step')
    
    
    
if(step == '1'):
    words = json.loads(json.dumps(result)).get('words')
    ID = words[0]["ID"]
    dataobj = json.loads(json.dumps(result))
    print(ID)
    if(ID == "piccode"):
        imgData = base64.b64decode(dataobj["words"][0]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
    getSmsPassword = raw_input("Please input "+ ID +" code: ")
    result[ID] = getSmsPassword
    if(len(words) == 2):
        ID = words[1]["ID"]
        getSmsPassword = raw_input("Please input "+ ID +" code: ")
        result[ID] = getSmsPassword
    
    params = {"status": "true",'debug1': True, "result": result }
    doCaptureResult1 = spiderRouter.execute(json.dumps(params))
    print("11111 RESULT *****************")
    print(doCaptureResult1)
    result = json.loads(doCaptureResult1).get('result')
    print(result)
    step = json.loads(json.dumps(result)).get('step')
    print(step)
    
    print(step)
    words = json.loads(json.dumps(result)).get('words')
    if(step == '2'):
        result = {}    
        if(len(words) == 3):
            for item in words:  
                if(item['ID'] == "piccode"):
                    imgData = base64.b64decode(item["source"])
                    fileName = 'C:/work/temp/resp.png'
                    with open(fileName, 'wb') as f:
                        f.write(imgData)  
                    
                result[item['ID']] = raw_input("Please " + item['ID'] + ": ")
        result['step'] =  step
        print(result)
        params = {"status": "true", "result": result }
        params = result
        doCaptureResult1 = spiderRouter.execute(json.dumps(params))


if(step == "2" ):
    words = json.loads(json.dumps(result)).get('words')
    dataobj = json.loads(json.dumps(result))
    ID = words[0]["ID"]
    print(ID)
    if(ID == "piccode"):
        imgData = base64.b64decode(dataobj["words"][0]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
    
    getSmsPassword = raw_input("Please input "+ ID +" code: ")
    result[ID] = getSmsPassword
    if(len(words) == 2):
        ID = words[1]["ID"]
        getSmsPassword = raw_input("Please input "+ ID +" code: ")
        result[ID] = getSmsPassword
    result = {}
    result['step'] =  step
    result[ID] = getSmsPassword
    params = {"status": "true", "result": result }
    params = result
    doCaptureResult1 = spiderRouter.execute(json.dumps(params))
    print("RESULT *****************")
    print(doCaptureResult1)
    result = json.loads(doCaptureResult1).get('result')
    print(result)
    step = json.loads(json.dumps(result)).get('step')
    print(step)

if(step == "2"):
    result = json.loads(doCaptureResult1).get('result')
    print(result)
    words = json.loads(json.dumps(result)).get('words')
    dataobj = json.loads(json.dumps(result))
    ID = words[0]["ID"]
    print(ID)
    if(ID == "piccode"):
        imgData = base64.b64decode(dataobj["words"][0]["source"])
        fileName = 'C:/work/temp/resp.png'
        with open(fileName, 'wb') as f:
            f.write(imgData)  
    
    getSmsPassword = raw_input("22Please input "+ ID +" code: ")
    result = {}
    if(ID == "piccode"):
        result['step'] = '2'
   
    result[ID] = getSmsPassword
    params = {"status": "true", "result": result }
    doCaptureResult1 = spiderRouter.execute(json.dumps(params))
    print("RESULT *****************")
    print(doCaptureResult1)
    
result = json.loads(doCaptureResult1).get('result')
print(result)
step = json.loads(json.dumps(result)).get('step')
if(step == '1'):
    words = json.loads(json.dumps(result)).get('words')
    ID = words[0]["ID"]
    print(ID)
    getSmsPassword = raw_input("Please input "+ ID +" code: ")
    result[ID] = getSmsPassword
    params = {"status": "true", "result": result }
    doCaptureResult1 = spiderRouter.execute(json.dumps(params))
    print("RESULT *****************")
    print(doCaptureResult1)

