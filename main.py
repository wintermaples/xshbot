import aiohttp
import discord
import xshbot
import traceback
import threading
from xshbot import APIConnector
from xshbot.community_event.april_28_fullmoon_party import fullmoon_party

client = discord.Client()

cmdManager = xshbot.CommandManager(",")

@client.event
async def on_message(message: discord.Message):
    try:
        if len(message.content) == 0:
            return
        try:
            await cmdManager.execute(message.content, client, message)
        except xshbot.CommandArgsPatternDoesntMatchException as ex:
            await client.send_message(message.channel, ex.message)
        except xshbot.CommandLengthDoesntMatchException as ex:
            await client.send_message(message.channel, str(ex))
            await client.send_message(message.channel, "HELP: " + ex.help)
    except Exception:
        print(traceback.format_exc())

cmdManager.commands.append(
    xshbot.CreateCommand(
        "register",
        [],
        ['ウォレット作成（register）']
    )
)


cmdManager.commands.append(
    xshbot.AddressCommand(
        "address",
        [],
        ['アドレス確認・入金（address_deposit）']
    )
)

cmdManager.commands.append(
    xshbot.DepositCommand(
        "deposit",
        [],
        ['アドレス確認・入金（address_deposit）']
    )
)

cmdManager.commands.append(
    xshbot.BalanceCommand(
        "balance",
        [],
        ['残高確認・出金（balance_withdraw）']
    )
)

cmdManager.commands.append(
    xshbot.WithdrawCommand(
        "withdraw",
        [
            xshbot.RegexArgsPattern("S[a-zA-Z0-9]{23}", "アドレスの形式が不正です!"),
            xshbot.PositiveNumberArgsPattern()
        ],
        ['残高確認・出金（balance_withdraw）']
    )
)

cmdManager.commands.append(
    xshbot.TipCommand(
        "tip",
        [
            xshbot.RegexArgsPattern(".*", ""),
            xshbot.PositiveNumberArgsPattern()
        ],
        ['イベントルーム', 'xshトーク部屋', 'フリートーク部屋', '技術部屋','トレード部屋','マイニング部屋','質問部屋','商品開発班','イベント班','翻訳班','イラスト班','wiki班','bot開発班', 'フルムーンビーチ','居酒屋しぃるど',]
    )
)

cmdManager.commands.append(
    xshbot.RainCommand(
        "rain",
        [
            xshbot.PositiveNumberArgsPattern()
        ],
        ['イベントルーム', 'xshトーク部屋', 'フリートーク部屋', '技術部屋','トレード部屋','マイニング部屋','質問部屋','商品開発班','イベント班','翻訳班','イラスト班','wiki班','bot開発班', 'フルムーンビーチ','居酒屋しぃるど',]
    )
)

cmdManager.commands.append(
    xshbot.TranslateJPIntoENCommand(
        "trjp",
        [
            xshbot.RegexArgsPattern('.*', '')
        ]
    )
)

cmdManager.commands.append(
    xshbot.TranslateENIntoJPCommand(
        "tren",
        [
            xshbot.RegexArgsPattern('.*', '')
        ]
    )
)

cmdManager.commands.append(
    xshbot.InfoCommand(
        "info",
        [
            xshbot.PositiveNumberArgsPattern(numberOfArgs_=-1)
        ],
        ['価格確認（info）']
    )
)

cmdManager.commands.append(
    xshbot.DiscordIDCommand(
        "getuniqueid",
        list()
    )
)

def connect():
    client.run('NDEzNzE1MDI1MTc4NTI1NzA2.DWc1rA.RfzqO-pkM0v98BVrlb6FAWOAao8')

fullmoon_party_instance = fullmoon_party.FullMoonParty(client)

while True:
    try:
        connect()
    except:
        connect()