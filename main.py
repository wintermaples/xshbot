import aiohttp
import discord
import xshbot
import traceback
import threading
from xshbot import APIConnector

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
        ['register（ウォレット作成）']
    )
)


cmdManager.commands.append(
    xshbot.AddressCommand(
        "address",
        [],
        ['address_deposit（アドレス確認・入金）']
    )
)

cmdManager.commands.append(
    xshbot.DepositCommand(
        "deposit",
        [],
        ['address_deposit（アドレス確認・入金）']
    )
)

cmdManager.commands.append(
    xshbot.BalanceCommand(
        "balance",
        [],
        ['address_deposit（アドレス確認・入金）']
    )
)

cmdManager.commands.append(
    xshbot.WithdrawCommand(
        "withdraw",
        [
            xshbot.RegexArgsPattern("S[a-zA-Z0-9]{23}", "アドレスの形式が不正です!"),
            xshbot.PositiveNumberArgsPattern()
        ],
        ['address_deposit（アドレス確認・入金）']
    )
)

cmdManager.commands.append(
    xshbot.TipCommand(
        "tip",
        [
            xshbot.RegexArgsPattern(".*", ""),
            xshbot.PositiveNumberArgsPattern()
        ],
        ['イベントルーム', 'general', '雑談部屋']
    )
)

cmdManager.commands.append(
    xshbot.RainCommand(
        "rain",
        [
            xshbot.PositiveNumberArgsPattern()
        ],
        ['イベントルーム', 'general', '雑談部屋']
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
        ['info（価格確認）']
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


while True:
    try:
        connect()
    except:
        connect()