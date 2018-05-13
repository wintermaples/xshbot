from typing import Sequence
from urllib import request
from urllib import parse
import json
import enum
from decimal import *


class APIConnector:

    def __init__(self, api_url, token):
        self.api_url = api_url
        self.token = token

    def __post_to_api(self, api, params):
        params = parse.urlencode(
            {
                'token': self.token,
                'data': json.dumps(params)
            }
        ).encode("utf-8")

        req = request.Request(self.api_url + api, data=params, method="POST")
        with request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            return response_body

    def create(self, name: str) -> str:
        jsondata = self.__post_to_api("wallet/create/",
            {
                "name": name
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return data["result"]

    def address(self, name: str) -> str:
        jsondata = self.__post_to_api("wallet/address/",
            {
                "name": name
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        if len(data["result"]) == 0:
            return ""
        return data["result"]

    def tip(self, from_name: str, to_name: str, amount: Decimal, fee_percent: Decimal) -> Decimal:
        jsondata = self.__post_to_api("wallet/tip/",
            {
                "from": from_name,
                "to": to_name,
                "amount": str(amount),
                "feePercent": str(fee_percent)
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return Decimal(data['result'])

    def send(self, from_name: str, to_addr: str, amount: Decimal, fee_percent: Decimal) -> Decimal:
        jsondata = self.__post_to_api("wallet/send/",
            {
                "from": from_name,
                "to": to_addr,
                "amount": str(amount),
                "feePercent": str(fee_percent)
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return Decimal(data['result'])

    def balance(self, name: str) -> float:
        jsondata = self.__post_to_api("wallet/balance/",
            {
                "name": name
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return float(data["result"])

    def delete(self, name: str) -> bool:
        jsondata = self.__post_to_api("wallet/delete/",
            {
                "name": name
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return True

    def list(self):
        jsondata = self.__post_to_api("wallet/list/",
            {
            }
        )
        data = json.loads(jsondata)
        if data["status"] != APIConnector.Status.SUCCESS.value:
            raise APIError(data["message"], APIConnector.Status(data['status']))
        return data["result"]

    def rain(self, name: str, dest_list: Sequence[str], price_per_one: Decimal, fee_percent: Decimal):
        params = {
                "from": name,
                "to": dest_list,
                "amount": str(price_per_one),
                "feePercent": str(price_per_one)
            }
        jsondata =  self.__post_to_api("wallet/rain/", params)
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