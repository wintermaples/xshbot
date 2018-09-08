import discord


async def get_id_from_name(server : discord.Server, name : str) -> str:
    for member in server.members:
        if member.name == name:
            return member.id
    return ""


async def get_discriminator_from_name(server : discord.Server, name : str) -> str:
    for member in server.members:
        if member.name == name:
            return member.discriminator
    return ""


async def mention(client, dist_channel: discord.Channel, dist_user: discord.User, message: str, embed=None):
    await client.send_message(dist_channel, "<@" + dist_user.id + "> " + message, embed=embed)


async def dm(client: discord.Client, dist_user: discord.User, message: str, embed=None):
    await client.send_message(dist_user, message, embed=embed)


async def dm_or_mention(client: discord.Client, dist_channel: discord.Channel, dist_user: discord.User, message:str, embed=None):
    if dist_channel.type is discord.ChannelType.private:
        await dm(client, dist_user, message, embed=embed)
    else:
        await mention(client, dist_channel, dist_user, message, embed=embed)