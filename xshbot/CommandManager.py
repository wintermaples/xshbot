import discord

class CommandManager():

    commands = list()

    def __init__(self, cmdPrefix : str):
        self.cmdPrefix = cmdPrefix

    async def execute(self, cmdStr : str, client, message : discord.Message):
        #全角でも認識できるようにする
        cmdStr = cmdStr.replace('　', ' ')

        prefix = cmdStr[0]
        if self.cmdPrefix != prefix:
            return False

        cmdStrWithoutPrefix = cmdStr[1:]
        splitedCmdStr = cmdStrWithoutPrefix.split(' ')
        cmdLabel = splitedCmdStr[0]
        args = splitedCmdStr[1:]
        # 空文字の引数は消去
        args = list(filter(
            lambda arg: arg != '',
            args
        ))
        for command in self.commands:
            if command.roomList is not None and not message.channel.name in command.roomList:
               continue
            if command.is_match(prefix, cmdLabel, args):
                print("Executed %s command." % command.cmdLabel)
                await command.execute(args, client, message)
                return True
