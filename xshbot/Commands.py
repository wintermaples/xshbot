import json
from abc import abstractmethod, ABCMeta

import discord
import requests
from DiscordUtil import *
from XSHUtil import *
from discord.embeds import *

from .APIConnector import *
from .CmdPatterns import CommandLengthDoesntMatchException, ArgsPatternPart
from .FXCalculator import *
from Translator import *

token = open('GRIMapi_token.txt').readline()
docomo_api_url = "https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY="
docomo_api_key = open('docomoapi_token.txt').readline()


class Command(metaclass=ABCMeta):
    def __init__(self, cmdLabel: str, argsPatternParts: Sequence[ArgsPatternPart], roomList : Sequence[str] = None):
        self.cmdLabel = cmdLabel
        self.argsPatternParts = argsPatternParts
        self.roomList = roomList

    @abstractmethod
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        raise NotImplementedError()

    @abstractmethod
    def help(self) -> str:
        raise NotImplementedError()

    def isMatch(self, cmdStr: str) -> bool:
        cmdSplited = cmdStr.split(" ")
        if len(cmdSplited) == 0:
            raise AssertionError()

        cmdLabel = cmdSplited[0]
        if cmdLabel != self.cmdLabel:
            return False

        args = cmdSplited[1:]

        if len(args) < self.requiredNumberOfArgs():
            raise CommandLengthDoesntMatchException(self.requiredNumberOfArgs(), self.help())

        index = 0
        for argsPattern in self.argsPatternParts:
            if argsPattern.numberOfArgs() != -1:
                argsPattern.validateArg(args[index:index + argsPattern.numberOfArgs()], index)
                index += argsPattern.numberOfArgs()
            else:
                argsPattern.validateArg(args[index:], index)

        return True

    def requiredNumberOfArgs(self) -> int:
        sum = 0
        for argsPattern in self.argsPatternParts:
            if argsPattern.numberOfArgs() != -1:
                sum += argsPattern.numberOfArgs()
        return sum


class CreateCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            toId = await getIdFromName(message.server, message.author.name)
            if toId != "":
                address = APIConnector.create(token, message.author.id)
                embed = Embed(description='<@%s>の"XSHアドレス"を作成したマジロ...' % (toId), type='rich', colour=0x6666FF)
                embed.add_field(name='XSH Address', value=address)
                embed.set_thumbnail(url='https://api.qrserver.com/v1/create-qr-code/?data=%s' % address)
                await client.send_message(message.channel, embed=embed)
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",register - ウォレットを作成します"


class AddressCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            toId = await getIdFromName(message.server, message.author.name)
            if toId != "":
                address = APIConnector.address(token, message.author.id)
                if address != "":
                    embed = Embed(description='<@%s>の"XSHアドレス"マジ...' % (toId), type='rich', colour=0x6666FF)
                    embed.add_field(name='XSH Address', value=address)
                    embed.set_thumbnail(url='https://api.qrserver.com/v1/create-qr-code/?data=%s' % address)
                    await client.send_message(message.channel, embed=embed)
                else:
                    await client.send_message(message.channel, ',register でウォレット作ってからやってマジ...')
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",address - ウォレットアドレスを確認します"


class DepositCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            toId = await getIdFromName(message.server, message.author.name)
            if toId != "":
                address = APIConnector.address(token, message.author.id)
                if address != "":
                    embed = Embed(description='<@%s>の"XSHアドレス"マジ...' % (toId), type='rich', colour=0x6666FF)
                    embed.add_field(name='XSH Address', value=address)
                    embed.set_thumbnail(url='https://api.qrserver.com/v1/create-qr-code/?data=%s' % address)
                    await client.send_message(message.channel, embed=embed)
                else:
                    await client.send_message(message.channel, ',register でウォレット作ってからやってマジ...')
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",deposit - 受金用ウォレットアドレスを確認します"


class BalanceCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            toId = await getIdFromName(message.server, message.author.name)
            if toId != "":
                priceJPY = await current_price_jpy()
                balance = APIConnector.balance(token, message.author.id)
                embed = Embed(description='<@%s>の"所持XSH数"を表示するマジロ...。' % (toId), type='rich', colour=0x6666FF)
                embed.add_field(name='XSH所持数', value='%.08f XSH' % balance, inline=True)
                embed.add_field(name='日本円換算', value='%0.04f 円' % (priceJPY * balance), inline=True)
                await client.send_message(message.channel, embed=embed)
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",balance - ウォレットの残高を確認します"


class WithdrawCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            if float(args[1]) < 1:
                await client.send_message(message.channel, "引き出しは1XSHからマジ...")
                return
            feePercent = 0.1 / float(args[1]) if float(args[1]) * 0.05 / 100 < 0.1 else 0.05 / 100
            amount = APIConnector.send(token, message.author.id, args[0], float(args[1]), feePercent)
            toId = await getIdFromName(message.server, message.author.name)
            if toId != "":
                await mention(client, message.channel, message.author.name,
                              '"%s"に"%f XSH"した送金マジ...確認してマジ...(txfee: 0.05XSH～(送金額により変動), 手数料: %fXSH)' % (args[0], amount, float(args[1]) - amount))
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",balance (to) (amount) - 指定した金額だけ、指定したアドレスにXSHを送金します"


class TipCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            toId = await getIdFromName(message.server, message.author.name)
            destId = await getIdFromName(message.server, args[0])
            if args[0].upper() == 'DONATE':
                destId = 'DONATE'
            if args[0].upper() == 'RAIN_WALLET':
                destId = 'RAIN_WALLET'
            if destId != "":
                if toId != "":
                    feePercent = 0.002 / 100
                    APIConnector.tip(token, message.author.id, destId, float(args[1]), feePercent)
                    await mention(client, message.channel, message.author.name,
                                  'から<@%s>に"%f XSH"送金したマジ...(手数料: %f％)' % (destId, float(args[1]), feePercent * 100))
            else:
                await client.send_message(message.channel, "%sなんていないマジ..." % args[0])
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",tip (toName) (amount) - 指定した金額だけ、指定した名前の人にXSHを送金します"


class RainCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            amount = float(args[0])
            if not await self.balanceIsMoreThan(message.author.id, amount):
                await client.send_message(message.channel,
                                          '所持"XSH"が足りないマジ...。残高は%fマジよ...' % APIConnector.balance(token,
                                                                                                    message.author.id))
                return

            onlineMembersId = [member.id for member in message.server.members if member.status != discord.Status.offline] # オンラインの人のID取得
            ownerIdListOfWallets = [wallet['name'] for wallet in APIConnector.list(token) if float(wallet['balance']) >= 1] # ウォレット一覧取得(残高が1XSH以上)
            onlineMembersIdWhoHasWallet = [memberId for memberId in onlineMembersId if memberId in ownerIdListOfWallets] # オンラインの人の中から、ウォレットを持ってる人のID一覧取得

            pricePerOne = amount / len(onlineMembersIdWhoHasWallet)

            import time
            s = time.time()

            APIConnector.rain(token, message.author.id, onlineMembersIdWhoHasWallet, pricePerOne, 0)

            toId = await getIdFromName(message.server, message.author.name)

            e = time.time()
            print("Elasped Time: %f" % (e - s))

            await client.send_message(message.channel,
                                      '<@%s> から"%f XSH"を受け取ったマジ...%d人に"%.04f XSH"ずつあげたマジ...' % (toId, amount, len(onlineMembersIdWhoHasWallet), pricePerOne))
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    async def balanceIsMoreThan(self, id: str, amount: float):
        if (APIConnector.balance(token, id)) >= amount:
            return True
        return False

    def help(self):
        return ",rain (amount) - オンラインの人に指定した数量だけXSHを均等配分します"


class InfoCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        amount = float(args[0]) if len(args) > 0 else 1
        price = await current_price_jpy()
        priceBTC = await current_price_btc()
        embed = Embed(type='rich', colour=0xF7D358)
        embed.add_field(name="XSH/BTC", value="%.08f BTC" % priceBTC, inline=True)
        embed.add_field(name="XSH/JPY", value="%.08f JPY" % price, inline=True)
        if amount != 1:
            embed.add_field(name="ㅤ", value="ㅤ", inline=False)
            embed.add_field(name="%.04f XSH/BTC" % amount, value="%.08f BTC" % (priceBTC * amount), inline=True)
            embed.add_field(name="%.04f XSH/JPY" % amount, value="%.08f JPY" % (price * amount), inline=True)
        embed.set_footer(text='https://coinmarketcap.com/currencies/shield-xsh/')
        embed.set_thumbnail(
            url='http://files.coinmarketcap.com.s3-website-us-east-1.amazonaws.com/static/img/coins/200x200/shield-xsh.png')
        await client.send_message(message.channel, embed=embed)

    def help(self):
        return ",info [amount] - 現在のSHIELDの価格を表示します"


class TranslateJPIntoENCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        await mention(client, message.channel, message.author.name, translate(' '.join(args), 'jp', 'en'))

    def help(self):
        return ',trjp (japanese) - 日本語から英語に翻訳します'


class TranslateENIntoJPCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        await mention(client, message.channel, message.author.name, translate(' '.join(args), 'en', 'jp'))

    def help(self):
        return ',tren (english) - 英語から日本語に翻訳します'


class DiceRainCommand(Command):

    dicerainInstance = None

    async def execute(self, args: Sequence[str], client, message: discord.Message):
        pass

    def help(self):
        return ",dicerain (amount) (people num) (border) - 指定された人数に、一人当り(amount)/(people num) XSHを、diceの値が(border)以上の人にプレゼントします。diceででる値は0-100です。最大試行数は"


class DiscordIDCommand(Command):

    async def execute(self, args: Sequence[str], client, message: discord.Message):
        await client.send_message(message.channel, await getIdFromName(message.server, args[0]))

    def help(self):
        return ",getuniqueid - discordのIDを取得します"