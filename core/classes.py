import discord
from discord.ext import commands

class cog_extension(commands.Cog) :
    def __init__(self,bot:commands.Bot) :
        self.bot = bot

def is_in_channel(channel_id):
    async def predicate(ctx: commands.Context):
        if ctx.channel.id != channel_id:
            await ctx.send(f'親~要到這裡輸入指令喔~<#{channel_id}>', delete_after=5)
            await ctx.message.delete()
        else:
            return True  # 返回 True 表示检查成功

    return commands.check(predicate)