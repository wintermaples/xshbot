import discord


class CommandManager:
    commands = list()

    def __init__(self, cmd_prefix: str):
        self.cmd_prefix = cmd_prefix

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
            if command.room_list is not None and message.channel.name not in command.room_list:
                continue
            if command.is_match(cmd_label, args):
                print("Executed %s command." % command.cmd_label)
                await command.execute(args, client, message)
                return True
