import requests
import pandas as pd
import json
import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from base64 import b64encode
import ipdb

'''
isRoleExistFromDCidxAndIdentity : 根據 DCidx 跟 identity 來檢查資料庫是否存在這位「職位者」
'''

# 設置 Flask root URL
base_url = 'http://140.116.179.24:5001'

# 根據傳入路由設定連線路由
def ConnectTo(endPoint, data, requestType):
    # 設定 api 路由並傳入相應資料
    if requestType == 'GET':
        return requests.get('http://140.116.179.24:2095' + endPoint, json = data)
    if requestType == 'POST':
        return requests.post('http://140.116.179.24:2095' + endPoint, json = data)
    if requestType == 'PUT':
        return requests.put('http://140.116.179.24:2095' + endPoint, json = data)
    if requestType == 'DELETE':
        return requests.delete('http://140.116.179.24:2095' + endPoint, json = data)

# 根據 DCidx 跟 identity 來檢查資料庫是否存在這位「職位者」
def isRoleExistFromDCidxAndIdentity(DCidx, identity):
    data = {
        'DCidx':DCidx,
        'identity':identity
    }
    response = ConnectTo('/isRoleExistFromDCidxAndIdentity', data, 'GET')
    if response.status_code == 200:
        result = response.json().get('result')
        return True, result
    else:
        return False, response.json().get('message')

# 根據 DCidx 與 identity 新增紀錄到「職位者」資料庫中
def addRoleHolder(DCidx, identity):
    data = {
        'DCidx':DCidx,
        'identity':identity
    }
    response = ConnectTo('/addRoleHolder', data, 'POST')
    if response.status_code == 200:
        result = response.json().get('message')
        return True, result
    else:
        return False, response.json().get('message')

# 根據 DCidx 與 identity 將「職位者」在資料庫中的紀錄填入 endDate
def endRoleHolder(DCidx, identity):
    data = {
        'DCidx':DCidx,
        'identity':identity
    }
    response = ConnectTo('/endRoleHolder', data, 'PUT')
    if response.status_code == 200:
        result = response.json().get('message')
        return True, result
    else:
        return False, response.json().get('message')