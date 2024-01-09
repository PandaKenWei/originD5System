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
isUserExist : 檢查dc_id是否已存在
createUser : 新增帳號密碼
createUserInfo : 第五基本資料 userIdx, highestHumanRank, highestHunterRank, humanSegment, hunterSegment, D5name, YTname
getUserIdx : dc_id -> UserIdx
applyGame : 新增觀眾場資料 'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
checkSameD5name : 資料庫內的第五暱稱
updateD5name : 更新第五暱稱
getLastApplyInfo : 提取上一次的觀眾廠資料
isApply : 檢查本次觀眾場是否已有報名資料
updateApply : 修改本次觀眾場報名資料
fetchAllThisData : 調取本次所有觀眾場資料
fetchAllUserInfo : [第五暱稱-求生區段-監管區段]資料
isDCIdxTheSameACPW : 比對資料庫中的 DCidx 和 帳密是否相同
updateSegment : 修改區段
isDCIdxInWithdrawList : 查詢 DCidx 是否存在於退出清單中
addWithdrawListMember : 新增 DCidx 到退出歷史資料庫中
deleteApply : 根據 DCidx 與 date 刪除報名紀錄
getAccountFromDCidx : 根據 DCidx 查詢帳號
updateRank : 根據 userIdx、陣營、段位去修改「最高段位」
getSegmentFromUserIdx : 根據 userIdx 查詢區段
isAnyGameListFromUserIdx : 根據 userIdx 檢查是否在 gameList 中存有任何一筆紀錄

'''


# 設置 Flask root URL
base_url = 'http://140.116.179.24:5001'

# 檢查dc_id是否已存在
def isUserExist(DCidx):
    # 設定 api 路由
    DCidx = int(DCidx)
    endpoint = f'/isUserExist/{DCidx}'
    response = requests.get(base_url + endpoint)

    # 检查响应状态码
    if response.status_code == 200:
        result = response.json()  # 獲取響應的 JSON
        return True, result
    else:
        return False, False

# 帳號密碼
def createUser(account, password, DCidx):
    # 設定 api 路由
    account = str(account)
    password = str(password)
    DCidx = int(DCidx)

    endpoint = f'/createUser/{account}/{password}/{DCidx}'
    response = requests.post(base_url + endpoint)
    if response.status_code == 201:
        return True, f"用戶 {DCidx} 創建成功"
    else:
        return False, f"用戶 {DCidx} 創建失敗，api 或 路由相關問題"

# 第五基本資料 userIdx, highestHumanRank, highestHunterRank, humanSegment, hunterSegment, D5name, YTname
def createUserInfo(user_info_dict):
    # 設定 api 路由
    endpoint = f'/createUserInfo'

    # 定義資料庫輸入轉換字典
    #dictRank = {'1':'一階', 
    #            '2':'二階',
    #            '3':'三階',
    #            '4':'四階',
    #            '5':'五階',
    #            '6':'六階',
    #            '7':'七階',
    #            '巔7':'巔峰七階',
    #            '巅7':'巔峰七階'
    #}
    #dictSegment = {'一':'一區',
    #               '二':'二區',
    #               '三':'三區',
    #               '四':'四區',
    #               '五':'五區'
    #}
    
    # 將資料進行封裝
    data = {
        'userIdx': int(user_info_dict['userIdx']),
        'highestHumanRank': user_info_dict['highestHumanRank'],
        'highestHunterRank': user_info_dict['highestHunterRank'],
        'humanSegment' : user_info_dict['humanSegment'],
        'hunterSegment' : user_info_dict['hunterSegment'],
        'D5name' : str(user_info_dict['D5name']),
        'YTname' : str(user_info_dict['YTname']),
    }
    response = requests.post(base_url + endpoint, json = data)
    if response.status_code == 201:
        return True, response.json().get('message')
    else:
        return False, response.json().get('message')

# dc_id -> UserIdx
def getUserIdx(DCidx):
    # 設定 api 路由
    endpoint = f'/getUserIdx/{DCidx}'
    response = requests.get(base_url + endpoint)

    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json().get('userIdx')
        return True, result
    else:
        return False, "此dc_id無對應帳號"

# 新增觀眾場資料
def applyGame(apply_info_dict):
    # 設定 api 路由
    endpoint = f'/applyGame'
    
    # 將資料進行封裝 - 'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
    data = {
        'userIdx': int(apply_info_dict['userIdx']),
        'isHallLevel': apply_info_dict['isHallLevel'],
        'isReginalSelection': apply_info_dict['isReginalSelection'],
        'availableTime' : apply_info_dict['availableTime'],
        'isApplyHuman' : apply_info_dict['isApplyHuman'],
        'isApplyHunter' : apply_info_dict['isApplyHunter'],
        'date' : apply_info_dict['date'],
        'remark' : apply_info_dict['remark'],
        'applyCurrentTime' : apply_info_dict['applyCurrentTime'],
    }
    response = requests.post(base_url + endpoint, json = data)
    if response.status_code == 201:
        return True, response.json().get('message')
    else:
        return False, response.json().get('message')

# 資料庫內的第五暱稱
def checkSameD5name(userIdx):
    # 設定 api 路由
    endpoint = f'/checkSameD5name/{userIdx}'
    response = requests.get(base_url + endpoint)

    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json().get('D5name')
        return True, result
    else:
        return False, False

# 更新第五暱稱
def updateD5name(userIdx, NewD5name):
    # 設定 api 路由
    endpoint = f'/updateD5name/{userIdx}/{NewD5name}'
    response = requests.put(base_url + endpoint)
    
    # 檢查響應狀態
    if response.status_code == 200:
        return True, response.json().get('message')
    else:
        return False, response.json().get('message')

# 提取上一次的觀眾廠資料
def getLastApplyInfo(userIdx):
    # 設定 api 路由
    endpoint = f'/getLastApplyInfo/{userIdx}'
    response = requests.get(base_url + endpoint)
    
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json()
        if result:
            return True, result
        else:
            return False, "無資料"
    else:
        return False, response.json().get('message')

# 檢查本次觀眾場是否已有報名資料
def isApply(userIdx, date):
    # 設定 api 路由
    date = date.replace('/', '-')
    endpoint = f'/isApply/{userIdx}/{date}'
    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json().get('updateIdx')
        return True, result
    else:
        return False, response.json().get('message')

# 修改本次觀眾場報名資料
def updateApply(update_apply_info_dict, updateIdx):
    # 設定 api 路由
    endpoint = f'/updateApply/{updateIdx}'
    
    # 將資料進行封裝
    data = {
        'userIdx': int(update_apply_info_dict['userIdx']),
        'isHallLevel': update_apply_info_dict['isHallLevel'],
        'isReginalSelection':update_apply_info_dict['isReginalSelection'],
        'availableTime' : update_apply_info_dict['availableTime'],
        'isApplyHuman' :update_apply_info_dict['isApplyHuman'],
        'isApplyHunter' : update_apply_info_dict['isApplyHunter'],
        'date' : update_apply_info_dict['date'],
        'remark' : update_apply_info_dict['remark'],
        'applyCurrentTime' : update_apply_info_dict['applyCurrentTime'],
    }
    response = requests.put(base_url + endpoint, json = data)
    if response.status_code == 201:
        return True, response.json().get('message')
    else:
        return False, response.json().get('message')

# input：今天日期 ( YYYY/MM/DD )   ouput：這一次(依照日期)報的全部觀眾場的 全部 row 所需 columns，並返回前端 DataFrame
def fetchAllThisData(date):
    # 設定 api 路由
    date = date.replace('/', '-')
    endpoint = f'/fetchAllThisData/{date}'

    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json()
        if result:
            resultDF = pd.DataFrame(result)
            return True, resultDF
        else:
            return False, "無資料"
    else:
        return False, response.json().get('message')
'''
使用方法：
state, result = fetchAllThisData('2023-6-23')
    for item in result:
        print("---------------")
        for key, value in item.items():
            print(f'{key}: {value}')
'''

# 返回全部 userInfo 的 all row，但只包含 [humanSegment, hunterSegment, D5name] columns，並返回前端 DataFrame
def fetchAllUserInfo():
    # 設定 api 路由
    endpoint = f'/fetchAllUserInfo'

    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json()
        if result:
            resultDF = pd.DataFrame(result)
            return True, resultDF
        else:
            return False, "無資料"
    else:
        return False, response.json().get('message')
'''
使用方法：
state, result = fetchAllUserInfo()
    print(result)
'''

# 比對資料庫中的 DCidx 和 帳密是否相同
def isDCIdxTheSameACPW(queryDict):
    # 設定 api 路由
    endpoint = f'/isDCIdxTheSameACPW'
    
    #key
    key = b'cutekawaiipandaa'

    # 將資料轉為 JSON 格式
    json_data = json.dumps(queryDict)
    json_data_bytes = json_data.encode('utf-8')
    # 創建新的 IV 與 cipher
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 加密
    ciphertext = cipher.encrypt(pad(json_data_bytes, AES.block_size))
    
    # 將 IV 和密文組合並進行 base64 編碼
    encoded_ciphertext = b64encode(iv + ciphertext).decode('utf-8')

    response = requests.get(base_url + endpoint, json = {'data':encoded_ciphertext})
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json().get('state')
        return True, result
    else:
        return False, response.json().get('message')
'''
使用方法：
queryDict = {
        'account':'咲雨',
        'password':'024012',
        'DCidx':'416123235822731265',
    }
    state, result = isDCIdxTheSameACPW(queryDict)
    if state:
        print(result)
    else:
        print("zzzz")
'''

# 修改區段
def updateSegment(userIdx, camp, segment):
    endpoint = f'/updateSegment/{userIdx}/{camp}/{segment}'
    response = requests.put(base_url + endpoint)

    #檢查響應狀態
    if response.status_code == 201:
        return True, response.json().get('message')
    else:
        return False, response.json().get('message') 
'''
state, result = updateSegment(17,"human", "二區")
    if state:
        print(f'the DC idx is Exist ? {result}')
    else:
        print("zzzz")
'''

#查詢 DCidx 是否存在於退出清單中
def isDCIdxInWithdrawList(DCidx):
    # 設定 api 路由
    endpoint = f'/isDCIdxInWithdrawList/{DCidx}'

    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json().get('result')
        return True, result
    else:
        return False, response.json().get('message') 
'''
state, result = isDCIdxInWithdrawList(855505480876163072)
    if state:
        print(f'{result}')
    else:
        print(result) 
'''

#新增 DCidx 到退出歷史資料庫中
def addWithdrawListMember(DCidx):
    # 設定 api 路由
    endpoint = f'/addWithdrawListMember/{DCidx}'

    response = requests.post(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 201:
        result = response.json().get('message')
        return True, result
    else:
        return False, response.json().get('message')
'''
DCidx = 416123235822731265
state, result = isDCIdxInWithdrawList(DCidx)
if state:
    if result:
        print("zzz")
    else:
        state, message = addWithdrawListMember(DCidx)
        print(message)
else:
    print(result) 
'''

#根據 DCidx 與 date 刪除報名紀錄
def deleteApply(userIdx, date):
    # 設定 api 路由
    date = date.replace('/', '-')
    endpoint = f'/deleteApply/{userIdx}/{date}'

    response = requests.delete(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json()
        if result:
            result = response.json().get('message')
        return True, result
    else:
        return False, response.json().get('message')
'''
使用範例
userIdx = 68
state, message = deleteApply(userIdx, '2023/7/5')
print(message) 
'''

#根據 DCidx 查詢帳號
def getAccountFromDCidx(DCidx):
    # 設定 api 路由
    endpoint = f'/getAccountFromDCidx/{DCidx}'
    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == "success":
            return True, result.get('account')
        else:
            return True, result.get('message')
    else:
        return False, response.json().get('message')
'''
使用範例
DCidx = 855505480876163072
state, result = getAccountFromDCidx(DCidx)
print(result) 
'''

#根據 userIdx、陣營、段位去修改「最高段位」
def updateRank(userIdx, camp, rank):
    # 設定 api 路由
    endpoint = f'/updateRank/{userIdx}/{camp}/{rank}'
    response = requests.put(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 201:
        return True, response.json().get('message')
    else:
        return False, response.json().get('message') 
'''
使用範例
userIdx = 68
state, message = updateRank(userIdx, 'human', '巔峰7階')
print(message)
'''

#根據 userIdx 查詢區段
def getSegmentFromUserIdx(userIdx):
    # 設定 api 路由
    endpoint = f'/getSegmentFromUserIdx/{userIdx}'
    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == "success":
            return True, result.get('segment')
        else:
            return True, result.get('message')
    else:
        return False, response.json().get('message')
'''
使用範例
userIdx = 57
state, result = getSegmentFromUserIdx(userIdx)
print(result)
'''

#根據 userIdx 檢查是否在 gameList 中存有任何一筆紀錄
def isAnyGameListFromUserIdx(userIdx):
    # 設定 api 路由
    endpoint = f'/isAnyGameListFromUserIdx/{userIdx}'
    response = requests.get(base_url + endpoint)
    # 檢查響應狀態
    if response.status_code == 200:
        result = response.json().get('result')
        return True, result
    else:
        return False, response.json().get('message')
'''
使用範例
userIdx = 57
state, result = isAnyGameListFromUserIdx(userIdx)
print(result)
'''

def ConnectTo(endPoint, data=None, requestType='POST'):
    # 設定 api 路由並傳入相應資料
    if requestType == 'GET':
        return requests.get('http://140.116.179.24:2095' + endPoint, json = data)
    if requestType == 'POST':
        return requests.post('http://140.116.179.24:2095' + endPoint, json = data)
    if requestType == 'PUT':
        return requests.put('http://140.116.179.24:2095' + endPoint, json = data)
    if requestType == 'DELETE':
        return requests.delete('http://140.116.179.24:2095' + endPoint, json = data)

# 依照 gameList 當日有填報屠夫的 userIdx 去調取 gameScheduleMember 的上次紀錄
def getHunterSortOrder():
    response = ConnectTo('/getHunterSortOrder', None, 'POST')
    if response.status_code == 200:
        result = response.json().get('sortedData')
        result_DF = pd.DataFrame(result)
        return True, result_DF
    else:
        return False, response.json().get('message')
'''
使用範例
state, result = getHunterSortOrder()
    print(result)
'''

# 新增 "事件紀錄" 到 allEvent 表裡面
def addEvent2DB(eventType, description):
    data = {
        'eventType':eventType,
        'description':description
    }
    response = ConnectTo('/addEvent2DB', data, 'POST')
    if response.status_code == 200:
        result = response.json().get('message')
        return True, result
    else:
        return False, response.json().get('message')
'''
使用範例
state, result = addEvent2DB('DC群組', '這是一段描述')
    print(result)
'''