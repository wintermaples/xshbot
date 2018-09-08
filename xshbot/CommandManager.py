import discord
from xshbot.util.logging import StreamLoggerFactory
from logging import DEBUG


class CommandManager:

    def __init__(self, cmd_prefix: str):
        self.cmd_prefix = cmd_prefix
        self.commands = list()
        self.logger = StreamLoggerFactory.create(__name__, DEBUG)

    async def execute(self, cmd_str: str, client, message: discord.Message):
        # 全角でも認識できるようにする
        cmd_str = cmd_str.replace('　', ' ')

        prefix = cmd_str[0]
        if self.cmd_prefix != prefix:
            return False

        cmd_str_without_prefix = cmd_str[1:]
        splited_cmd_str = cmd_str_without_prefix.split(' ')
        cmd_label = splited_cmd_str[0]
        args = splited_cmd_str[1:]
        # 空文字の引数は消去
        args = list(filter(
            lambda arg: arg != '',
            args
        ))
        for command in self.commands:
            if not CommandManager.can_execute_command_on(message, command):
                continue
            if command.is_match(cmd_label, args):
                self.logger.info(f'Executed {command.cmd_label} command.')
                await command.execute(args, client, message, message.channel is not discord.ChannelType.private)
                return True

    @staticmethod
    def can_execute_command_on(message: discord.Message, command) -> bool:
        if message.channel.type is not discord.ChannelType.private:
            if command.room_list is not None and message.channel.name in command.room_list:
                return True
            else:
                return False
        else:
            if command.can_execute_on_DM:
                return True
            else:
                return False
