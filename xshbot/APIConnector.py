from typing import Sequence
from urllib import request
from urllib import parse
import json
import enum

apiUrl = "http://192.168.0.30:8000/"

def _postToAPI(api, params):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = parse.urlencode({'data': params}).encode("utf-8")

    req = request.Request(apiUrl + api, data=params, method="POST")
    with request.urlopen(req) as response:
        response_body = response.read().decode("utf-8")
        return response_body

class APIConnector:

    def create(token: str, id: str) -> str:
        jsondata =  _postToAPI("wallet/create/",
            {
                "token": token,
                "id": id
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return data["result"]


    def address(token : str, id : str) -> str:
        jsondata =  _postToAPI("wallet/address/",
            {
                "token": token,
                "id": id
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        if len(data["result"]) == 0:
            return ""
        return data["result"]

    def tip(token : str, fromId : str, toId : str, amount : float, feePercent: float) -> float:
        jsondata =  _postToAPI("wallet/tip/",
            {
                "token": token,
                "from": fromId,
                "to": toId,
                "amount": amount,
                "feePercent": feePercent
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return float(data['result'])

    def send(token : str, fromId : str, toAddr : str, amount : float, feePercent: float) -> float:
        jsondata =  _postToAPI("wallet/send/",
            {
                "token": token,
                "from": fromId,
                "to": toAddr,
                "amount": amount,
                "feePercent": feePercent
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return float(data['result'])

    def balance(token : str, id : str) -> float:
        jsondata =  _postToAPI("wallet/balance/",
            {
                "token": token,
                "id": id
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return float(data["result"])

    def delete(token : str, id : str) -> bool:
        jsondata =  _postToAPI("wallet/delete/",
            {
                "token": token,
                "id": id
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return True

    def list(token : str):
        jsondata =  _postToAPI("wallet/list/",
            {
                "token": token
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return data["result"]

    def rain(token : str, id : str, destList : Sequence[str], pricePerOne : float, feePercent: float):
        destDic = {'to[%s]' % dest: str(pricePerOne) for dest in destList}
        params = {
                "token": token,
                "from": id,
                "to": destList,
                "amount": pricePerOne,
                "feePercent": feePercent
            }
        jsondata =  _postToAPI("wallet/rain/", params)
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return True

    class Status(enum.Enum):
        SUCCESS = '0'
        AUTH_FAILED = 'G-0'
        INTERNAL_ERROR = 'G-1'
        INSUFFICIENT_ARGS = 'G-2'
        WALLET_NOT_FOUND = 'G-3'
        INSUFFICIENT_FUNDS = 'G-4'
        NEGATIVE_VALUE_SPECIFIED = 'G-5'
        AMOUNT_TOO_SMALL = 'G-6'

class APIError(Exception):

    def __init__(self, message : str, status : APIConnector.Status):
        self.message = message
        self.status = status

#import random
#import discord
#import time
#online = list()
#offline = list()
#allMembers = list()
#for i in range(0, 100000):
#    online.append(discord.Member(
#        user={
#        'id': random.randrange(0, 1000000000000),
#        'status': discord.Status.online,
#            'voice_state': discord.VoiceState.voice_channel
#        }
#    ))
#
#for j in range(0, 200000):
#    online.append(discord.Member(
#        user={
#        'id': random.randrange(0, 1000000000000),
#        'status': discord.Status.online,
#            'voice_state': discord.VoiceState.voice_channel
#        }
#    ))
#
#
#allMembers.extend(online)
#allMembers.extend(offline)
#
#walletHave = online[0:75000]
#
#start = time.time()
#for k in range(0, 1000):
#    onlineMembersId = [member.id for member in allMembers if
#                       member.status == discord.Status.online and not member.is_afk]  # オンラインの人のID取得
#    ownerIdListOfWallets = [wallet.id for wallet in walletHave]  # ウォレット一覧取得
#    onlineMembersIdWhoHasWallet = [memberId for memberId in onlineMembersId if
#                                   memberId in ownerIdListOfWallets]  # オンラインの人の中から、ウォレットを持ってる人のID一覧取得
#
#    destDic = {'to[%s]' % dest: str(1) for dest in onlineMembersIdWhoHasWallet}
#    params = {
#        "token": 'aueo',
#        "from": id
#    }
#    params.update(destDic)
#
#elasptedTime = time.time() - start
#print(elasptedTime)