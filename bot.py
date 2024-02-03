import discord
from discord.ext import commands
import json
import os
import asyncio

bot = commands.Bot(command_prefix="%", intents=discord.Intents.all())

with open('setting.json','r',encoding='utf8') as jfile :
  jdata = json.load(jfile)

@bot.event
async def on_ready():
  await cog_load()
  print(f"logged as {bot.user.name}")
async def cog_load():
  for filename in os.listdir('./cmds') :
    if filename.endswith('.py') :
      await bot.load_extension(f'cmds.{filename[:-3]}')
      print(f"complete {filename[:-3]}")


async def main ():
    async with bot :
      await bot.start(jdata["TOKEN_pd"])


asyncio.run(main())