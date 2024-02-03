import discord
from discord.ext import commands
from core.classes import *
import asyncio
from datetime import datetime
from discord import File
import re
import os
import API.buttonConfig as BC
import API.emoji as emoji


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
user_channels = {}
class practical_instruction(cog_extension):

    @is_in_channel(1106479974975799317)
    @commands.command() #手動改名 指令 !改名
    async def 改名(self,ctx):
        member = ctx.author
        dm_channel = await member.create_dm()
        await dm_channel.send('請告訴我你的新youtube稱呼，例如:奶茶貓')

        def check(message):
            return message.author == member and message.channel == dm_channel

        message = await self.bot.wait_for('message', check=check)
        new_name = message.content

        await dm_channel.send('請告訴我你的新第五名字，例如:這是一隻熊')
        message = await self.bot.wait_for('message', check=check)
        new_idv_name = message.content

        await dm_channel.send('是否需要其他備註? 不需要請輸入:無')
        message = await self.bot.wait_for('message', check=check)
        otherwise_name = message.content

        if otherwise_name == "無" or otherwise_name == "无":
            new_nickname = f"{new_name} ({new_idv_name})"
        else :
            new_nickname = f"{new_name} ({new_idv_name}){otherwise_name}"

        await member.edit(nick=new_nickname)
        await dm_channel.send(f'我已經將你的暱稱設為 {new_nickname}')
        await ctx.send(f'我已經將你的暱稱設為 {new_nickname}')
    
    @is_in_channel(1106479974975799317)
    @commands.command() #舉報 指令 ！舉報
    async def 舉報(self,ctx):
        def check(msg):
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author

        channel_send = await ctx.author.create_dm()
        member = ctx.guild.get_member(ctx.author.id)
        nickname = member.nick if member.nick else member.name

        #刪除舉報訊息
        await ctx.message.delete()

        full_report = []

        await channel_send.send("請提供您的舉報詳細信息，檢舉內容請包含以下資訊：\n1.發生時間\n2.被檢舉人\n3.被檢舉人所違反的群規\n並於最後發送'done'，以提交舉報內容。\n若您要取消舉報，請輸入'C'，以取消舉報")

        while True:
            msg = await self.bot.wait_for('message', check=check)

            if msg.content.lower() == 'done':
                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonConfirm.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send(f'您是否確定要提交這個舉報？', view=view))
                confirm_msg = await view.wait_for_click()

                if confirm_msg == 'Y':
                    # 找到目標頻道
                    report_channel_id = 976712961282433054  # 違規舉報頻道ID
                    report_channel = self.bot.get_channel(report_channel_id)

                    await report_channel.send(f'{ctx.author.name}-群組暱稱:{nickname}，於{datetime.now().strftime("%Y-%m-%d %H:%M")}提出舉報，舉報內容如下')
                    # 發送舉報訊息
                    for report_item in full_report:
                        if 'images' in report_item:
                            for image in report_item['images']:
                                with open(image, 'rb') as img_file:
                                    discord_file = File(img_file, filename=os.path.basename(image))
                                    await report_channel.send(content=report_item['content'], file=discord_file)

                        else:
                            await report_channel.send(content=report_item['content'])

                    await channel_send.send('您的舉報已完成，請耐心等待管理員審核。')
                    break

                elif confirm_msg == 'N':
                    await channel_send.send('請繼續提交舉報內容')
                    continue

                elif confirm_msg == 'C':
                    await channel_send.send('您的舉報已取消')
                    break

            elif msg.content == 'C':
                await channel_send.send('您的舉報已取消')
                break

            # 如果不是 'done'也不是'C'，則添加到舉報內容中
            report_item = {'content': msg.content}

            if msg.attachments:
                img_files = []
                for att in msg.attachments:
                    custom_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{att.filename}"
                    img_file = os.path.join(os.getcwd(), 'remark_photo', custom_filename)
                    await att.save(img_file)
                    img_files.append(img_file)
                    print(img_files)
                report_item['images'] = img_files
            full_report.append(report_item)
            
    @is_in_channel(1106479974975799317)
    @commands.command()
    async def 語音(self,ctx, limit:int):
        user = ctx.message.author
        guild = ctx.guild
        if user in user_channels and user_channels[user] in [voice_channel for voice_channel in guild.voice_channels]:
            await ctx.send('目前還有你創建的頻道，不能創建新的喔')
            return
        # 1. 使用參數決定該頻道的人數上限        
        name_parts = re.split(r'\(|（', ctx.author.nick)
        yt_name = name_parts[0].strip()  #yt暱稱

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True),
            user: discord.PermissionOverwrite(move_members=True)  # 2. 頻道創建者可以將人移出該語音頻道
        }

        category = discord.utils.get(guild.categories, name="自創語音頻道")
        channel = await guild.create_voice_channel(name=f"{yt_name}-語音", overwrites=overwrites, user_limit=limit,category=category)
        # 保存用戶和創建的頻道的對應關係
        user_channels[user] = channel
        await ctx.send(f'已由 {ctx.author.nick} 創建上限為{limit}人之語音頻道{channel.name}')
            
    @commands.Cog.listener()
    async def on_voice_state_update(self,member, before, after):
        # 3. 當該頻道沒人時自動消失
        if before.channel and len(before.channel.members) == 0 and (before.channel.name.endswith("-語音")):
            await before.channel.delete()
            # 當頻道被刪除時，從字典中移除該用戶和頻道的對應關係
            for user, channel in user_channels.items():
                if channel == before.channel:
                    del user_channels[user]
                    break
                
    @is_in_channel(1106479974975799317)
    @commands.command()
    async def 偷聽(self, ctx, member: discord.Member):
        channel_send = await ctx.author.create_dm()
        
        # 先檢查該使用者是否在該語音頻道
        if member.voice and member.voice.channel:

            # 私訊該使用者，問他是否同意讓指令發送者加入他們的語音頻道
            buttons = [BC.create_button(label,settings) for label, settings in BC.buttonYN.items()]
            view = BC.ModelButtons(buttons)
            asyncio.create_task(member.send(f'{ctx.author.name} 想加入你在 {member.voice.channel.name} 的語音頻道。你同意嗎？', view=view))
            try:
                ans = await asyncio.wait_for(view.wait_for_click(), 300)  # 等待用户响应，最多等待 300 秒
            except asyncio.TimeoutError:  # 如果等待超时，假设答案为 "N"
                ans = "N"
                await channel_send.send(f'等待時間已超過，未獲得同意 {emoji.get_emoji("sad")}')
                await member.send(f'我等你5分鐘啦～已經等到睡著啦～下次要快點理我喔 {emoji.get_emoji("funny")}')
                await view.stop()  # 刪除原來的消息            

            # 如果該使用者點擊了同意按鈕，則讓指令發送者加入該語音頻道
            if ans == "Y":
                if ctx.author.voice:
                    await ctx.author.move_to(member.voice.channel)
                    await ctx.send(f'{ctx.author.name} 已被移動到 {member.voice.channel.name}')
                else:
                    await channel_send.send(f'你必須先加入一個語音頻道後再次使用指令！ {emoji.get_emoji("gogo")}')
                    await member.send(f'{ctx.author.name} 未在其他語音頻到內 {emoji.get_emoji("angry")}')
            elif ans == "N":
                await channel_send.send(f'未獲得同意，無法把你移到語音喔 {emoji.get_emoji("sad")}')
        else:
            await ctx.send(f'{member.name} 不在語音頻道裡 {emoji.get_emoji("cute")}')
                           
async def setup(bot) :
    await bot.add_cog(practical_instruction(bot))