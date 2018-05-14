import aiohttp
import discord
import xshbot
import traceback
import threading
from xshbot import APIConnector
from xshbot.community_event.april_28_fullmoon_party import fullmoon_party
import json
import datetime

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
        ['イベントルーム', 'xshトーク部屋', 'フリートーク部屋', '技術部屋','チャート部屋','マイニング部屋','質問部屋','商品開発班','イベント班','翻訳班','イラスト班','wiki班','bot開発班', 'フルムーンビーチ','居酒屋しぃるど',]
    )
)

cmdManager.commands.append(
    xshbot.RainCommand(
        "rain",
        [
            xshbot.PositiveNumberArgsPattern()
        ],
        ['イベントルーム', 'xshトーク部屋', 'フリートーク部屋', '技術部屋','チャート部屋','マイニング部屋','質問部屋','商品開発班','イベント班','翻訳班','イラスト班','wiki班','bot開発班', 'フルムーンビーチ','居酒屋しぃるど',]
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
    xshbot.HowMuchCommand(
        "howmuch",
        [
            xshbot.PositiveNumberArgsPattern(numberOfArgs_=1)
        ],
        None
    )
)

cmdManager.commands.append(
    xshbot.DiscordIDCommand(
        "getuniqueid",
        list()
    )
)

@client.event
async def on_socket_raw_receive(msg):
    try:
        msg_json = json.loads(msg)
        if msg_json['t'] == 'MESSAGE_REACTION_ADD' and msg_json['d']['emoji']['name'] == '📌' and msg.find(
                'guild_id') != -1:
            # チャンネルID
            channel_id = msg_json['d']['channel_id']
            # メッセージID
            message_id = msg_json['d']['message_id']
            # ユーザーID
            user_id = msg_json['d']['user_id']
            # チャンネル
            discord_channel = client.get_channel(channel_id)
            # メッセージ
            target_msg = await client.get_message(discord_channel, message_id)
            # メッセージ送信者
            send_user_id = target_msg.author.id
            # メッセージの内容
            msg_content = target_msg.content
            # contentの長さが0の場合、embedsの中身を取得
            if len(msg_content) == 0 and len(target_msg.embeds) != 0:
                embed_content = target_msg.embeds[0]['fields']
                msg_content = embed_content[0]['value']
            res = []
            res.append('SendUser :')
            res.append('<@')
            res.append(send_user_id)
            res.append('>')
            res.append('\n')
            res.append('SendTime :')
            # +9h
            time = target_msg.timestamp
            time = time + datetime.timedelta(hours=9)
            res.append(time.strftime('%Y/%m/%d  %H:%M:%S'))
            res.append('\n')
            res.append('Channel:')
            res.append('<#')
            res.append(channel_id)
            res.append('>')
            res.append('\n')
            res.append('------------------------------------------------')
            res.append('\n')
            res.append(msg_content)
            res.append('\n')
            res_str = ''.join(res)
            user = discord.utils.get(client.get_all_members(), id=user_id)
            if user is not None:
                res = await client.send_message(user, res_str)
                await client.add_reaction(res, '✂')
        # DMのメッセージを消す用
        elif msg_json['t'] == 'MESSAGE_REACTION_ADD' and msg_json['d']['emoji']['name'] == '✂' and msg.find(
                'guild_id') == -1:
            # チャンネルID
            channel_id = msg_json['d']['channel_id']
            # メッセージID
            message_id = msg_json['d']['message_id']
            # ユーザーID
            user_id = msg_json['d']['user_id']
            user = discord.utils.get(client.get_all_members(), id=user_id)
            # チャンネル
            discord_channel = await client.start_private_message(user)
            # メッセージ
            target_msg = await client.get_message(discord_channel, message_id)
            if user != target_msg.author:
                await client.delete_message(target_msg)
    except:
        pass


# fullmoon_party_instance = fullmoon_party.FullMoonParty(client)

client.run('NDEzNzE1MDI1MTc4NTI1NzA2.DWc1rA.RfzqO-pkM0v98BVrlb6FAWOAao8')