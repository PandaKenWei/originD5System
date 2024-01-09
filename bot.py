import discord
from discord.ext import commands
import json
import os
import asyncio
import re
import sys
import random

sys.path.insert(0, os.getcwd()+"/API")
import api
import emoji

import ipdb

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

with open('setting.json','r',encoding='utf8') as jfile :
  jdata = json.load(jfile)
  

'''
on_member_join : 點擊入群連結後，機器人私訊更改暱稱
'''  
@bot.event
async def on_member_join(member):
    dm_channel = await member.create_dm()
    await dm_channel.send(f'歡迎來到我們的粉絲群！請回答下列問題，讓我們協助你正確更改群組暱稱')
    await dm_channel.send('請告訴我你的youtube名稱，例如:奶茶貓')

    def check(message):
        return message.author == member and message.channel == dm_channel

    message = await bot.wait_for('message', check=check)
    name = message.content
    await dm_channel.send('請告訴我你的第五名字，例如:這是一隻熊')
    message = await bot.wait_for('message', check=check)
    idv_name = message.content
    nickname = f"{name} ({idv_name})"
    
    new_line = '\n'
    channel_link = f"https://discord.com/channels/953292249763053569/953621940415922216/993184212121309215"

    await member.edit(nick=nickname)
    await dm_channel.send(f'我已經將你的暱稱設為 {nickname}')
    await dm_channel.send(f'請點擊連結{channel_link}並閱讀規則後，在 #粉絲群規則簽到 根據規則指定之固定格式簽到{new_line}("我是xxx，已閱讀完群組規則並同意遵守"，xxx請填入您的暱稱){new_line}以獲取"彩色的熊貓小夥伴"身分組。')


'''
on_message : 簽到後，確認簽到格式及暱稱正確
'''  
@bot.event
async def on_message(message):
  # 檢查消息是否來自機器人，避免循環回應
  if message.author.bot:
      return

  # 替換以下變量為你想要的特定頻道 ID、指定文字和要分配的角色名稱
  specific_channel_id = 953547677319168070
  specific_text = "已閱讀完群組規則並同意遵守"
  role_name_to_assign = "彩色的熊貓小夥伴"
  
  ordinary_member_role = ["方方最幼的熊貓崽崽們", "彩色的熊貓小夥伴"]
  # 普通成員身分組
  if message.channel.id == specific_channel_id and specific_text.lower() in message.content.lower() :
    message_author_id = message.author.id
    user_role = [i.name for i in message.author.roles if i.name in ordinary_member_role]

    #查詢 DCidx 是否存在於退出清單中
    _,result = api.isDCIdxInWithdrawList(message_author_id)
    if result:
      special_role = discord.utils.get(message.guild.roles, name='DC管理員') # Replace '特殊身分組' with your special role's name
      if special_role:
        await message.channel.send(f'因您之前曾退出過群組，因此請耐心等待<@&{special_role.id}>審核 ')
        
    elif len(user_role)>0:
      sent_message = await message.channel.send(content = f"您已經有身分組囉~小心胖子熊貓咬你 {emoji.get_emoji('funny')}")
      await asyncio.sleep(1)
      await message.delete()
      await asyncio.sleep(5)
      await sent_message.delete()
              
    else :
      ###修改待測試
      if bool(re.search(r'\(|（', message.author.display_name)) and bool(re.search(r'\)|）', message.author.display_name)):
        role = discord.utils.get(message.guild.roles, name=role_name_to_assign)    
        
      else : 
        await message.channel.send(f"您的暱稱須符合指定格式，請先回復群組機器人之私訊，並於修改暱稱後再次簽到 {emoji.get_emoji('angry')}")
        
      if role :
        await message.author.add_roles(role)
  '''
  有人@群組機器人時，自動回復
  '''
  if len(message.mentions) == 1 and bot.user.mentioned_in(message) and message.reference is None:
    channel_send = await message.author.create_dm()
    response = random.choice(jdata["responses"])
    await message.delete()
    await channel_send.send(response)  
        
  await bot.process_commands(message)


'''
on_member_remove : 有群組成員離開後，同一個dc_id進入簽到時，不直接給予身分組
'''
@bot.event
async def on_member_remove(member):
  DCidx = member.id
  #查詢 DCidx 是否存在於退出清單中
  _,result = api.isDCIdxInWithdrawList(member.id)
  if result :
    return
  else :
    #新增 DCidx 到退出歷史資料庫中
    _,result = api.addWithdrawListMember(DCidx)


@bot.event
async def cog_load():
  for filename in os.listdir('./cmds') :
    if filename.endswith('.py') :
      await bot.load_extension(f'cmds.{filename[:-3]}')
      print(f"complete {filename[:-3]}")


async def main ():
    async with bot :
      await cog_load()
      await bot.start(jdata["TOKEN_pd"])

asyncio.run(main())

ipdb.set_trace()

