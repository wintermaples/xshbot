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
import re

api_url = 'http://arbor.shieldcurrency.jp/'
token = open('SHIELDdConnectorAPIToken.txt').readline()
connector = APIConnector(api_url, token)

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

    def is_match(self, prefix: str, cmdLabel: str, args: Sequence[str]) -> bool:
        if cmdLabel == '':
            return False

        if cmdLabel != self.cmdLabel:
            return False

        if len(args) < self.required_number_of_args():
            raise CommandLengthDoesntMatchException(self.required_number_of_args(), self.help())

        index = 0
        for argsPattern in self.argsPatternParts:
            if argsPattern.numberOfArgs() != -1:
                argsPattern.validateArg(args[index:index + argsPattern.numberOfArgs()], index)
                index += argsPattern.numberOfArgs()
            else:
                argsPattern.validateArg(args[index:], index)

        return True

    def required_number_of_args(self) -> int:
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
                address = connector.create(message.author.id)
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
                address = connector.address(message.author.id)
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
                address = connector.address(message.author.id)
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
                balance = connector.balance(message.author.id)
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
            feePercent = Decimal(0.1) / Decimal(args[1]) if Decimal(args[1]) * Decimal('0.05') / Decimal(100) < Decimal('0.1') else Decimal('0.05') / Decimal(100)
            amount = connector.send(message.author.id, args[0], Decimal(args[1]), feePercent)
            toId = await getIdFromName(message.server, message.author.name)
            if toId != "":
                await mention(client, message.channel, message.author.name,
                              '"%s"に"%f XSH"送金したマジ...確認してマジ...(txfee: 0.05XSH～(送金額により変動), 手数料: %fXSH)' % (args[0], float(amount), float(Decimal(args[1]) - amount)))
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",balance (to) (amount) - 指定した金額だけ、指定したアドレスにXSHを送金します"


class TipCommand(Command):

    def __parse_id(self, message: str):
        regex = re.compile(r'\<@\!*([0-9]*)\>')
        if not regex.match(message):
            return ''

        return regex.search(message).group(1)

    async def execute(self, args: Sequence[str], client, message: discord.Message):
        try:
            fromId = message.author.id
            destId = self.__parse_id(args[0])
            if args[0].upper() == 'DONATE' or destId == '413715025178525706':
                destId = 'DONATE'
            if args[0].upper() == 'RAIN_WALLET':
                destId = 'RAIN_WALLET'

            if destId != "":
                if fromId != "":
                    feePercent = Decimal('0.002') / Decimal(100)
                    connector.tip(message.author.id, destId, Decimal(args[1]), feePercent)
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
            if amount < 0.05:
                await client.send_message(message.channel,
                                          'こんなんじゃうまく雨が降らないマジ... 0.05XSH以上は欲しいマジよ...')
                return
            if not await self.balanceIsMoreThan(message.author.id, amount):
                await client.send_message(message.channel,
                                          '所持"XSH"が足りないマジ...。残高は%fマジよ...' % connector.balance(message.author.id))
                return

            onlineMembersId = [member.id for member in message.server.members if member.status != discord.Status.offline] # オンラインの人のID取得
            ownerIdListOfWallets = [wallet['name'] for wallet in connector.list() if float(wallet['balance']) >= 1] # ウォレット一覧取得(残高が1XSH以上)
            onlineMembersIdWhoHasWallet = [memberId for memberId in onlineMembersId if memberId in ownerIdListOfWallets] # オンラインの人の中から、ウォレットを持ってる人のID一覧取得

            pricePerOne = Decimal(amount) / Decimal(len(onlineMembersIdWhoHasWallet))

            import time
            s = time.time()

            connector.rain(message.author.id, onlineMembersIdWhoHasWallet, pricePerOne, Decimal(0))

            toId = await getIdFromName(message.server, message.author.name)

            e = time.time()
            print("Elasped Time: %f" % (e - s))

            await client.send_message(message.channel,
                                      '<@%s> から"%f XSH"を受け取ったマジ...%d人に"%.04f XSH"ずつあげたマジ...' % (toId, amount, len(onlineMembersIdWhoHasWallet), pricePerOne))
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    async def balanceIsMoreThan(self, id: str, amount: float):
        if (connector.balance(id)) >= amount:
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
        embed.add_field(name="BTC/XSH", value="%.08f BTC/XSH" % priceBTC, inline=True)
        embed.add_field(name="JPY/XSH", value="%.08f JPY/XSH" % price, inline=True)
        if amount != 1:
            embed.add_field(name="ㅤ", value="ㅤ", inline=False)
            embed.add_field(name="%.04f BTC/XSH" % amount, value="%.08f BTC/XSH" % (priceBTC * amount), inline=True)
            embed.add_field(name="%.04f JPY/XSH" % amount, value="%.08f JPY/XSH" % (price * amount), inline=True)
        embed.set_footer(text='https://coinmarketcap.com/currencies/shield-xsh/')
        embed.set_thumbnail(
            url='http://files.coinmarketcap.com.s3-website-us-east-1.amazonaws.com/static/img/coins/200x200/shield-xsh.png')
        await client.send_message(message.channel, embed=embed)

    def help(self):
        return ",info [amount] - 現在のSHIELDの価格を表示します"


class HowMuchCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message):
        amount = float(args[0]) if len(args) > 0 else 1
        price = await current_price_jpy()
        priceBTC = await current_price_btc()
        embed = Embed(type='rich', colour=0xF7D358)
        embed.add_field(name="XSH/JPY", value="%.08f XSH/1 JPY" % (1 / price), inline=True)
        if amount != 1:
            embed.add_field(name="ㅤ", value="ㅤ", inline=False)
            embed.add_field(name="How Much?", value="%.04f XSH/%.04f JPY" % ( ((1/price) * amount), amount ), inline=True)
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