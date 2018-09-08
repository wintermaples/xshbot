import random
import re
from abc import abstractmethod, ABCMeta

from discord.embeds import *

from DiscordUtil import *
from Translator import *
from XSHUtil import *
from .APIConnector import *
from .CmdPatterns import CommandLengthDoesntMatchException, ArgsPatternPart

api_url = 'http://arbor.shieldcurrency.jp/'
token = open('SHIELDdConnectorAPIToken.txt').readline()
connector = APIConnector(api_url, token)
xsh_thumbnail = 'http://files.coinmarketcap.com.s3-website-us-east-1.amazonaws.com' \
                '/static/img/coins/200x200/shield-xsh.png'


class Command(metaclass=ABCMeta):
    def __init__(self, cmd_label: str, arg_pattern_parts: Sequence[ArgsPatternPart], room_list: Sequence[str] = None, can_execute_on_DM: bool = False):
        self.cmd_label = cmd_label
        self.args_pattern_parts = arg_pattern_parts
        self.room_list = room_list
        self.can_execute_on_DM = can_execute_on_DM

    @abstractmethod
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        raise NotImplementedError()

    @abstractmethod
    def help(self) -> str:
        raise NotImplementedError()

    def is_match(self, cmd_label: str, args: Sequence[str]) -> bool:
        if cmd_label == '':
            return False

        if cmd_label != self.cmd_label:
            return False

        if len(args) < self.required_number_of_args():
            raise CommandLengthDoesntMatchException(self.required_number_of_args(), self.help())

        index = 0
        for argsPattern in self.args_pattern_parts:
            if argsPattern.number_of_args() != -1:
                argsPattern.validate_arg(args[index:index + argsPattern.number_of_args()], index)
                index += argsPattern.number_of_args()
            else:
                argsPattern.validate_arg(args[index:], index)

        return True

    def required_number_of_args(self) -> int:
        sum_of_number_of_args = 0
        for argsPattern in self.args_pattern_parts:
            if argsPattern.number_of_args() != -1:
                sum_of_number_of_args += argsPattern.number_of_args()
        return sum_of_number_of_args


class CreateCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            address = connector.create(message.author.id)
            embed = Embed(description='<@%s>の"XSHアドレス"を作成したマジロ...' % message.author.id, type='rich', colour=0x6666FF)
            embed.add_field(name='XSH Address', value=address)
            embed.set_thumbnail(url='https://api.qrserver.com/v1/create-qr-code/?data=%s' % address)
            await dm_or_mention(client, message.channel, message.author, message='', embed=embed)
        except APIError as err:
            await dm_or_mention(client, message.channel, message.author, "ERROR: %s" % err.message)

    def help(self):
        return ",register - ウォレットを作成します"


class AddressCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            address = connector.address(message.author.id)
            if address != "":
                embed = Embed(description='<@%s>の"XSHアドレス"マジ...' % message.author.id, type='rich', colour=0x6666FF)
                embed.add_field(name='XSH Address', value=address)
                embed.set_thumbnail(url='https://api.qrserver.com/v1/create-qr-code/?data=%s' % address)
                await dm_or_mention(client, message.channel, message.author, message='', embed=embed)
            else:
                await dm_or_mention(client, message.channel, message.author, ',register でウォレット作ってからやってマジ...')
        except APIError as err:
            await dm_or_mention(client, message.channel, message.author, "ERROR: %s" % err.message)

    def help(self):
        return ",address - ウォレットアドレスを確認します"


class DepositCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            address = connector.address(message.author.id)
            if address != "":
                embed = Embed(description='<@%s>の"XSHアドレス"マジ...' % message.author.id, type='rich', colour=0x6666FF)
                embed.add_field(name='XSH Address', value=address)
                embed.set_thumbnail(url='https://api.qrserver.com/v1/create-qr-code/?data=%s' % address)
                await dm_or_mention(client, message.channel, message.author, message='', embed=embed)
            else:
                    await dm_or_mention(client, message.channel, message.author, ',register でウォレット作ってからやってマジ...')
        except APIError as err:
            await dm_or_mention(client, message.channel, message.author, "ERROR: %s" % err.message)

    def help(self):
        return ",deposit - 受金用ウォレットアドレスを確認します"


class BalanceCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            price_jpy = get_price_jpy_per_xsh()
            balance = connector.balance(message.author.id)
            embed = Embed(description='<@%s>の"所持XSH数"を表示するマジロ...。' % message.author.id, type='rich', colour=0x6666FF)
            embed.add_field(name='XSH所持数', value='%.08f XSH' % balance, inline=True)
            embed.add_field(name='日本円換算', value='%0.04f 円' % (price_jpy * balance), inline=True)
            await dm_or_mention(client, message.channel, message.author, message='', embed=embed)
        except APIError as err:
            await dm_or_mention(client, message.channel, message.author, "ERROR: %s" % err.message)

    def help(self):
        return ",balance - ウォレットの残高を確認します"


class WithdrawCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            if float(args[1]) < 1:
                await dm_or_mention(client, message.channel, message.author, "引き出しは1XSHからマジ...")
                return

            if Decimal(args[1]) * Decimal('0.0005') < Decimal('0.1'):
                fee_percent = Decimal(0.1) / Decimal(args[1])
            else:
                fee_percent = Decimal('0.05') / Decimal(100)

            amount = connector.send(message.author.id, args[0], Decimal(args[1]), fee_percent)
            await dm_or_mention(client, message.channel, message.author,
                            '"%s"に"%f XSH"送金したマジ...確認してマジ...(txfee: 0.05XSH～(送金額により変動), 手数料: %fXSH)'
                            % (args[0], float(amount), float(Decimal(args[1]) - amount)))
        except APIError as err:
            await dm_or_mention(client, message.channel, message.author, "ERROR: %s" % err.message)

    def help(self):
        return ",balance (to) (amount) - 指定した金額だけ、指定したアドレスにXSHを送金します"


class TipCommand(Command):
    @staticmethod
    def __parse_id(message: str):
        regex = re.compile(r'<@!*([0-9]*)>')
        if not regex.match(message):
            return ''

        return regex.search(message).group(1)

    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            from_id = message.author.id
            dest_id = self.__parse_id(args[0])
            if args[0].upper() == 'DONATE' or dest_id == '413715025178525706':
                dest_id = 'DONATE'
            if args[0].upper() == 'RAIN_WALLET':
                dest_id = 'RAIN_WALLET'

            if dest_id != "":
                if from_id != "":
                    fee_percent = Decimal('0.002') / Decimal(100)
                    connector.tip(message.author.id, dest_id, Decimal(args[1]), fee_percent)
                    await mention(client, message.channel, message.author,
                                  'から<@%s>に"%f XSH"送金したマジ...(手数料: %f％)' % (dest_id, float(args[1]), fee_percent * 100))
            else:
                await client.send_message(message.channel, "%sなんていないマジ..." % args[0])
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    def help(self):
        return ",tip (toName) (amount) - 指定した金額だけ、指定した名前の人にXSHを送金します"


class RainCommand(Command):
    def __init__(self, cmd_label: str, arg_pattern_parts: Sequence[ArgsPatternPart], room_list: Sequence[str] = None):
        super().__init__(cmd_label, arg_pattern_parts, room_list)
        self.last_fetched: datetime = None
        self.wallet_list = None
        self.fetching_interval = 300

    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        try:
            amount = float(args[0])
            # number_of_people = int(float(args[1])) if len(args) >= 2 else -1
            if amount < 0.05:
                await client.send_message(message.channel,
                                          'こんなんじゃうまく雨が降らないマジ... 0.05XSH以上は欲しいマジよ...')
                return

            if not self.balance_is_more_than(message.author.id, amount):
                await client.send_message(message.channel,
                                          '所持"XSH"が足りないマジ...。残高は%fマジよ...' % connector.balance(message.author.id))
                return

            # オンラインの人のID取得
            online_members_id = [member.id for member in message.server.members
                                 if member.status != discord.Status.offline]

            # ウォレット一覧取得(残高が1XSH以上)
            owner_id_list_of_wallets = [wallet['name'] for wallet in self.get_wallet_list()
                                        if float(wallet['balance']) >= 1]

            # オンラインの人の中から、ウォレットを持ってる人のID一覧取得
            online_members_id_who_has_wallet = [member_id for member_id in online_members_id
                                                if member_id in owner_id_list_of_wallets]

            # 宝くじrain用の処理
            # if number_of_people > 0:
            #     online_members_id_who_has_wallet = random.sample(
            #         online_members_id_who_has_wallet,
            #         min(len(online_members_id_who_has_wallet), number_of_people))

            price_per_one = Decimal(amount) / Decimal(len(online_members_id_who_has_wallet))


            connector.rain(message.author.id, online_members_id_who_has_wallet, price_per_one, Decimal(0))

            to_id = await get_id_from_name(message.server, message.author.name)

            await client.send_message(message.channel,
                                      '<@%s> から"%f XSH"を受け取ったマジ...%d人に"%.04f XSH"ずつあげたマジ...' % (
                                          to_id, amount, len(online_members_id_who_has_wallet), price_per_one))
        except APIError as err:
            await client.send_message(message.channel, "ERROR: %s" % err.message)

    @staticmethod
    def balance_is_more_than(wallet_id: str, amount: float):
        if (connector.balance(wallet_id)) >= amount:
            return True
        return False

    def get_wallet_list(self):
        if self.last_fetched is not None:
            delta: float = time.time() - self.last_fetched
            if delta > self.fetching_interval:
                self.wallet_list = connector.list()
                self.last_fetched = time.time()
                return self.wallet_list
            else:
                return self.wallet_list
        else:
            self.wallet_list = connector.list()
            self.last_fetched = time.time()
            return self.wallet_list

    def help(self):
        return ",rain (amount) [number_of_people] - オンラインの人に指定した数量だけXSHを均等配分します"


class InfoCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        amount = float(args[0]) if len(args) > 0 else 1
        price = get_price_jpy_per_xsh()
        price_btc = get_price_btc_per_xsh()
        embed = Embed(type='rich', colour=0xF7D358)
        embed.add_field(name="BTC/XSH", value="%.08f BTC/XSH" % price_btc, inline=True)
        embed.add_field(name="JPY/XSH", value="%.08f JPY/XSH" % price, inline=True)
        if amount != 1:
            embed.add_field(name="ㅤ", value="ㅤ", inline=False)
            embed.add_field(name="%.04f BTC/XSH" % amount, value="%.08f BTC/XSH" % (price_btc * amount), inline=True)
            embed.add_field(name="%.04f JPY/XSH" % amount, value="%.08f JPY/XSH" % (price * amount), inline=True)
        embed.set_footer(text='https://coinmarketcap.com/currencies/shield-xsh/')
        embed.set_thumbnail(
            url=xsh_thumbnail)
        await client.send_message(message.channel, embed=embed)

    def help(self):
        return ",info [amount] - 現在のSHIELDの価格を表示します"


class HowMuchCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        amount = float(args[0]) if len(args) > 0 else 1
        price = get_price_jpy_per_xsh()
        embed = Embed(type='rich', colour=0xF7D358)
        embed.add_field(name="XSH/JPY", value="%.08f XSH/1 JPY" % (1 / price), inline=True)
        if amount != 1:
            embed.add_field(name="ㅤ", value="ㅤ", inline=False)
            embed.add_field(name="How Much?", value="%.04f XSH/%.04f JPY" % (((1 / price) * amount), amount),
                            inline=True)
        embed.set_footer(text='https://coinmarketcap.com/currencies/shield-xsh/')
        embed.set_thumbnail(
            url=xsh_thumbnail)
        await client.send_message(message.channel, embed=embed)

    def help(self):
        return ",info [amount] - 現在のSHIELDの価格を表示します"


class TranslateJPIntoENCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        await mention(client, message.channel, message.author.name, translate(' '.join(args), 'jp', 'en'))

    def help(self):
        return ',trjp (japanese) - 日本語から英語に翻訳します'


class TranslateENIntoJPCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        await mention(client, message.channel, message.author.name, translate(' '.join(args), 'en', 'jp'))

    def help(self):
        return ',tren (english) - 英語から日本語に翻訳します'


class DiceRainCommand(Command):
    dice_rain_instance = None

    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        pass

    def help(self):
        return ",dicerain (amount) (people num) (border) - " \
               "指定された人数に、一人当り(amount)/(people num) XSHを、diceの値が(border)以上の人にプレゼントします。" \
               "diceででる値は0-100です。最大試行数は"


class DiscordIDCommand(Command):
    async def execute(self, args: Sequence[str], client, message: discord.Message, is_dm: bool):
        def __parse_id(chat_message: str):
            regex = re.compile(r'<@!*([0-9]*)>')
            if not regex.match(chat_message):
                return ''

            return regex.search(chat_message).group(1)

        await client.send_message(message.channel, __parse_id(args[0]))

    def help(self):
        return ",getuniqueid - discordのIDを取得します"
