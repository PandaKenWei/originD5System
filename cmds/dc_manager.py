import discord
from discord.ext import commands
from core.classes import cog_extension
import asyncio
from datetime import datetime, time, timedelta
import pytz
import numpy as np
import ipdb
from discord import File
import re
import os
import sys
sys.path.insert(0, os.getcwd()+"/API")
import API.emoji as emoji
import API.manage as manage
from typing import Optional,Union
import json


'''
1. tag : 自動@有參與觀眾場的人
2. 改名 : 更改暱稱
3. 魔法 : 自動刪除訊息
   - !魔法 %H:%M : 刪除非管理員訊息
   - !魔法 %H:%M all : 刪除所有訊息
4. 運勢 : 隨機產生運勢
   - !運勢 : 四大運勢
   - !運勢 想問的運勢 : 隨機產生想問的運勢的結果
5. 舉報 : 由機器人發出舉報 - 目的為將'違規舉報'設為私人頻道

'''
role_dic = {
    'DC管理員':'DC管理員',
    'YT管理員':'YT管理員',
    '小竹子(戰地記者)':'戰地記者',
    '熊貓的腦袋(開發人員)':'開發人員'
}

class dc_manager_tools(cog_extension):
    async def __check_role(self,ctx):
        allowed_role = ['DC管理員','房管-主播級']
        user_roles = [role.name for role in ctx.author.roles]
        if any (role in user_roles for role in allowed_role) :
            return True
        else :
            return False

    @commands.command()  # 自動tag人 指令 !tag
    async def tag(self, ctx, *members):
        tag_members = []
        for member_str in members:
            if len(member_str) == 4 and member_str.isdigit():  # 如果是 "#" 后的四位数字
                for member in ctx.guild.members:
                    if member.discriminator == member_str:
                        tag_members.append(member)
                        break
            elif member_str.startswith("<@") and member_str.endswith(">"):
                # 如果是用戶標籤，則進一步處理
                member_id = int(member_str[2:-1])
                member = ctx.guild.get_member(member_id)
                if member is not None:
                    tag_members.append(member)
            else:
                # 否則按名稱或 ID 查找成員
                member = discord.utils.get(ctx.guild.members, name=member_str) or discord.utils.get(ctx.guild.members, id=int(member_str))
                if member is not None:
                    tag_members.append(member)
    
        if tag_members:
            await ctx.send(' '.join(member.mention for member in tag_members))        
            await ctx.send(f'今天的觀眾場有你的對局喔，請確定你的對局場次，並準時出席')
            #於發送訊息後，刪除原指令
            await ctx.message.delete()
            
    @commands.command()
    async def 魔法(self,ctx, clear_time_str,  *,member: Optional[Union[discord.Member,str]] = None):

        if await self.__check_role(ctx):
            channel = ctx.message.channel     
            # 解析清除時間
            clear_time = datetime.strptime(clear_time_str, '%H:%M').time()
            # 取得當地時間的日期時間物件（使用Asia/Taipei時區）
            local_tz = pytz.timezone('Asia/Taipei')
            clear_datetime_local = datetime.combine(datetime.now(local_tz).date(), clear_time)
            # 如果指定時間在當前時間之後，則將日期扣上一天
            if clear_datetime_local > datetime.now():
              clear_datetime_local = datetime.combine(datetime.now(local_tz).date()-timedelta(days=1), clear_time)
            # 將本地時間轉換為UTC時間
            clear_datetime_utc = clear_datetime_local.astimezone(pytz.utc)
            # 刪除訊息
            await ctx.message.delete()
            if member == "all" :
                check_message = lambda m: m.created_at >= clear_datetime_utc
            elif member:
                check_message = lambda m: m.author == member and m.created_at >= clear_datetime_utc
            else : 
                allowed_role = ['DC管理員','房管-主播級']
                check_message = lambda m: not any (role.name in allowed_role for role in m.author.roles) and m.created_at >= clear_datetime_utc
            deleted = await channel.purge(
              check = check_message
              )
            sent_message = await ctx.send(f'已刪除 {len(deleted)} 條訊息。')
            await asyncio.sleep(5)
            await sent_message.delete()
            
        else :            
            sent_message = await ctx.send(f'麻瓜熊貓是不能使用魔法的 ಠ⁠∀⁠ಠ')
            await asyncio.sleep(5)
            await ctx.message.delete()
            await sent_message.delete()
            
    @commands.command()
    async def 封印(self, ctx, member: discord.Member):
        check_role = await self.__check_role(ctx)
        if check_role :  # 如果指令發送者有管理訊息的權限
            mute_role = discord.utils.get(ctx.guild.roles, name="黑名單身分")  # 假設你已經建立了名為"Muted"的角色並設定了該角色無法在文字頻道中發送訊息或在語音頻道中發言
            role_to_remove = [role for role in member.roles if role != ctx.guild.default_role]
            role_removed_list = []
                    
            for role in role_to_remove:
                try:
                    await member.remove_roles(role)
                    role_removed_list.append(role)
                except discord.errors.Forbidden:
                    continue

            removed_roles = {role.name: role.id for role in role_removed_list}
            # Save the removed roles into a json file
            if not os.path.exists('./removed_roles.json'):
                with open('./removed_roles.json', 'w') as json_file:
                    json.dump({str(member.id): removed_roles}, json_file)
            else:
                with open('./removed_roles.json', 'r+') as json_file:
                    data = json.load(json_file)
                    data[str(member.id)] = removed_roles
                    json_file.seek(0)  # reset file position to the beginning.
                    json.dump(data, json_file, indent=4)
                
            await member.add_roles(mute_role)  # 禁言用戶
            await ctx.send(f"{member.name}已被封印 {emoji.get_emoji('funny')}")

        else:  # 如果指令發送者沒有管理訊息的權限
            await ctx.send(f"你!!!你想幹嘛!!!是不是想造反{emoji.get_emoji('angry')}")

    @commands.command()
    async def 封印解除(self, ctx, member: discord.Member):
        check_role = await self.__check_role(ctx)
        if check_role :  # 如果指令發送者有管理訊息的權限
            mute_role = discord.utils.get(ctx.guild.roles, name="黑名單身分")  # 假設你已經建立了名為"黑名單身分"的角色並設定了該角色無法在文字頻道中發送訊息或在語音頻道中發言
            try :
                await member.remove_roles(mute_role)
            except :
                ctx.send(f"他沒被封印!! {emoji.get_emoji('angry')}")
            # 從 json 檔加載原有的身分組
            with open('./removed_roles.json', 'r') as json_file:
                data = json.load(json_file)
                removed_roles = data.get(str(member.id))
                if removed_roles:
                    for _, role_id in removed_roles.items():
                        role = discord.utils.get(ctx.guild.roles, id=role_id)
                        if role:
                            await member.add_roles(role)
                    del data[str(member.id)]  # 將使用者移出儲存原身分組的資料

            # Save the updated data back to the json file
            with open('./removed_roles.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)

            await ctx.send(f"{member.name}已被解除封印 {emoji.get_emoji('cute')}。")
        else:  # 如果指令發送者沒有管理訊息的權限
            await ctx.send(f"不可以幫忙偷渡啦!!!! {emoji.get_emoji('angry')}")
    
    @commands.command()
    async def 登記職務(self, ctx, member: discord.Member, addrole : discord.Role):
        allowed_role = ['房管-主播級']
        user_roles = [role.name for role in ctx.author.roles]
        if any (role in user_roles for role in allowed_role) : # 如果指令發送者有管理訊息的權限
            dc_id = member.id
            role_name = role_dic[addrole.name]
            _,isRoleExist = manage.isRoleExistFromDCidxAndIdentity(dc_id,role_name)
            
            if not isRoleExist :
                _, result = manage.addRoleHolder(dc_id, role_name)
                await ctx.send(f"{result} {emoji.get_emoji('cute')}。")
            else :
                await ctx.send(f"{member.name}已有職務在身 {emoji.get_emoji('cute')}。")
        else:  # 如果指令發送者沒有管理訊息的權限
            await ctx.send(f"不可以試圖篡位啦!!!! {emoji.get_emoji('angry')}")

    @commands.command()
    async def 卸任(self, ctx, member: discord.Member, delrole : discord.Role):
        allowed_role = ['房管-主播級']
        user_roles = [role.name for role in ctx.author.roles]
        if any (role in user_roles for role in allowed_role) : # 如果指令發送者有管理訊息的權限
            dc_id = member.id
            role_name = role_dic[delrole.name]
            _,isRoleExist = manage.isRoleExistFromDCidxAndIdentity(dc_id,role_name)
            
            if isRoleExist :
                _, result = manage.endRoleHolder(dc_id, role_name)
                await ctx.send(f"{result} {emoji.get_emoji('cute')}。")
            else :
                await ctx.send(f"{member.name}沒有職務在身 {emoji.get_emoji('cute')}。")
        else:  # 如果指令發送者沒有管理訊息的權限
            await ctx.send(f"不可以試圖篡位啦!!!! {emoji.get_emoji('angry')}")
    
    #### 臨時遍歷身分組並將按讚的漏網清單給正確移除 ####
    # @commands.command()
    # async def 檢查簽到(self, ctx):
    #     try:
    #         # 獲取訊息對象
    #         channel = self.bot.get_channel(953982724367073310)
    #         message = await channel.fetch_message(1172194995311214624)

    #         # 尋找特定反應
    #         for reaction in message.reactions:
    #             if str(reaction.emoji) == "👍":
    #                 # 正確地遍歷反應的用戶
    #                 async for user in reaction.users():
    #                     if isinstance(user, discord.Member):
    #                         # 檢查並移除身分組
    #                         role = discord.utils.get(user.guild.roles, name="未簽到")
    #                         if role and role in user.roles:
    #                             await user.remove_roles(role)
    #                             print(f"移除了 {user.name} 的 '未簽到' 身分組")

    #     except Exception as e:
    #         print(f"在處理時發生錯誤: {e}")
                                                   
async def setup(bot) :
    await bot.add_cog(dc_manager_tools(bot))