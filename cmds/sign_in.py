import discord
from discord.ext import commands
from datetime import datetime, timedelta, time
import asyncio
import os
import sys
from ID_Config import Channel_ID, Identity_ID
sys.path.insert(0, os.getcwd()+"/API")
import buttonConfig as BC
import emoji

import ipdb

class SignInCog(commands.Cog):
    def __init__(self, bot):
        # 建立一個包含公告日期的 list
        current_year = datetime.now().year
        self.announcement_dates = [
            datetime(2023, 5, 1, 9, 0),
            #datetime(current_year, 11, 1, 9, 0),
            datetime(2023, 11, 9, 18, 13)
        ]
        # 設定一些參數
        self.reminderDay = 17 # 開始公告後幾天會發提醒
        self.reminderDay2 = 19  # 第二次提醒
        self.endRangeFromStart = 20 # 截止
        self.startTime = time(18, 13) # 開始日期，(月, 日)
        self.startTimePeriord = 10 # 公告的觸發分鐘，DC機器人需要誤差
        # DC 的 package
        self.bot = bot
        self.announcement_task = self.bot.loop.create_task(self.announcement_check())
    
    ## Cog 解構自動呼叫
    def cog_unload(self):
        self.announcement_task.cancel()

    ## 背景任務：於特定時間醒來發送簽到公告
    async def announcement_check(self):
        while not self.bot.is_closed():
            try:
                await self.perform_announcement_actions()
                print(f"完成{datetime.now()}的公告函式")
                # 計算出的下一次公告時間還沒有到，則休眠到那個時間
                next_announcement = self.calculate_next_announcement_time()
                if next_announcement and datetime.now() < next_announcement:
                    print(f"下一次公告時間：{next_announcement}")
                    await discord.utils.sleep_until(next_announcement)
            except Exception as e:
                print(f"An error occurred: {e}")
                # 如果出現錯誤，等待一分鐘後重試
                await asyncio.sleep(60)
    
    async def send_announcement(self, channel, message, reaction, send_datetime):
        role_name_to_assign = "未簽到"
        role_to_assign = discord.utils.get(channel.guild.roles, name=role_name_to_assign)

        # for member in channel.guild.members:
        #     print(member)
        #     await member.add_roles(role_to_assign)

        # 計算需要等待的時間（秒）
        wait_seconds = (send_datetime - datetime.now()).total_seconds()
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)  # 暫停直到達到發送時間

        msg = await channel.send(message)  # 發送消息
        await msg.add_reaction(reaction)  # 添加反應

        return msg

    ## 檢查當前日期和時間，並基於這些檢查結果決定是否發布簽到公告或發送提醒    
    async def perform_announcement_actions(self, retries=5, delay=1):
        # 獲取特定頻道 ID 與 身分組 ID
        channel_id = Channel_ID["公告"]
        identity_id = Identity_ID["未簽到"]
        # 指定 Discord Bot 發送的頻道並取得頻道的對象實例
        # 但有時候會因為 Discord Bot 還沒有把資訊完全家載完成，因此會有抓不到 channel 的狀況發生，需要重抓幾次
        for i in range(retries):
            channel = self.bot.get_channel(channel_id)
            if channel:
                break
            await asyncio.sleep(delay)  # 等待一段時間後重試
        now = datetime.now()
        # 是否處於公告日
        for date in self.announcement_dates:
            # 等下會用到的變數
            endTime = (datetime.combine(now.date(), self.startTime) + timedelta(minutes=self.startTimePeriord)).time()
            if (now.month, now.day) == (date.month, date.day):
                print("處於公告日，發出公告")
                if self.startTime <= now.time() <= endTime:  
                    self.sent_message_id, self.end_datetime = await self.setup_announcement(channel, date, identity_id)
                break
            # 如果不是公告日則發私訊提醒簽到 
            else:
                print("處於提醒日")
                if self.startTime <= now.time() <= endTime:
                    print("發出提醒")
                    await self.notify_users_after_deadline(channel, channel.guild, date, identity_id)
                    break
                else:
                    print("但時間未到")
                    break

    async def setup_announcement(self, channel, date, identity_id):
        special_role = discord.utils.get(channel.guild.roles, id=identity_id)

        send_datetime = datetime.now()
        end_datetime = date + timedelta(days=self.endRangeFromStart)

        end_date_str = end_datetime.strftime('%Y/%m/%d %H:%M')

        message_content = (
        f'<@&{special_role.id}>每半年一次的群組大掃除又來啦～\n'
        f'群組進來了不少小夥伴，與此同時增加了不少幽靈人口與殭屍(無主)帳號，因此為了清除：\n\n'

        f'1. 遺失帳號的小夥伴們創了新帳號入群，遺留在群組內的殭屍(無主)帳號\n'
        f'2. 過久沒使用但依然留在群組的小號\n'
        f'3. 進群後從未發聲、發言，也對群組"漠不關心"的號\n\n'
        f'請有看到此篇公告的各位，幫我按個「👍」來消除「未簽到」的紅色身分組，身分組會在按下讚的瞬間自動清除，待截止日期為止，沒有按「👍」的帳號將視為殭屍(無主)帳號統一清出群組！\n'
        f'統計到{end_date_str}截止，請沒有注意到公告的小夥伴們相互提醒並把握時間，謝謝大家！\n\n'

        f'※ 針對第 3 點進行補充，可以默默當個潛水員這是「沒有問題的」！！！但請先浮出水面幫我留下你的「👍」再潛回去吧{emoji.get_emoji("cute")}\n'
        f'※ 「不要」回應除了「👍」之外的其他符號，會不計入簽到 \n'

        )
        print(f"send_datetime：{send_datetime}")
        msg = await self.send_announcement(channel, message_content, "👍", send_datetime)
        print(f"公告已發布")
        return msg.id,end_datetime
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            # 獲取公告訊息的 ID
            announcement_message_id = 1172194995311214624

            # 確保反應是對我們的公告訊息
            if payload.message_id == announcement_message_id and str(payload.emoji) == "👍":
                guild = self.bot.get_guild(payload.guild_id)
                if guild is None:
                    return

                # 獲取反應和用戶
                channel = guild.get_channel(payload.channel_id)
                if channel is None:
                    return

                message = await channel.fetch_message(payload.message_id)
                user = guild.get_member(payload.user_id)

                if user is None or user.bot:
                    return

                # 檢查是否在截止時間前
                if datetime.now() > datetime(2023, 11, 29, 23, 0):#self.end_datetime:
                    return

                # 移除用戶角色
                role = discord.utils.get(guild.roles, name="未簽到")
                if role in user.roles:
                    await user.remove_roles(role)

                # 記錄成功操作
                print(f"已移除 {user.name} 的未簽到角色")

        except Exception as e:
            # 記錄錯誤
            print(f"在處理 on_raw_reaction_add 時發生錯誤: {e}")

    # 計算下一次公告的時間
    def calculate_next_announcement_time(self):
        now = datetime.now()
        next_time = None
        candidate_next_time = None

        # 檢查今天日期日否落在每個公告日期「區間」內，如果是，next_time 就會取得最靠近的公告日期，反之則為 None
        for idx, date in enumerate(sorted(self.announcement_dates)):
            if self.isInSpecificRange(now, date):
                next_time = date
                candidate_next_time = sorted(self.announcement_dates)[idx+1] if idx+1 < len(self.announcement_dates) else None
                break
        # 如果在任何區間內
        if next_time is not None:
            diff = now - date
            if diff.days < self.reminderDay:
                next_time = date + timedelta(days=self.reminderDay)
            elif self.reminderDay <= diff.days < self.reminderDay2:
                next_time = date + timedelta(days=self.reminderDay2)
            else:
                next_time = None
        else:
            next_time = candidate_next_time

        return next_time if next_time is not None else sorted(self.announcement_dates)[0].replace(year=sorted(self.announcement_dates)[0].year + 1)
            
    # 配合 calculate_next_announcement_time 看取得的日期是否在某次公告的時間區段內
    def isInSpecificRange(self, now, date):
        end_date = date + timedelta(days=20)
        return date <= now <= end_date

    # The rest of your methods go here
    async def notify_users_after_deadline(self, channel, guild, date, identity_id):
        now = datetime.now()
        if now.day == date.day:
            await channel.send("簽到已結束")
        else :
            role = discord.utils.get(guild.roles, id=identity_id)
            total_members = sum(1 for member in guild.members if role in member.roles)  # 總共需要發送消息的用戶數
            sent_count = 0  # 已經發送的消息數

            for member in guild.members:
                if role in member.roles:
                    sent_count += 1
                    try:
                        await member.send(f'您尚未完成簽到！請於指定時間內於特定公告中簽到，不然時間到了會把您先請出群組喔{emoji.get_emoji("cute")}')
                        print(f"{member.name}: {sent_count}/{total_members}")
                    except discord.errors.Forbidden:
                        print(f"無法發送消息給 {member.name}: 隱私設置或其他問題 {sent_count}/{total_members}")


async def setup(bot):
    await bot.add_cog(SignInCog(bot))