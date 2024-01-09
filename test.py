from discord.ext import tasks, commands
import discord
from datetime import datetime, timedelta, time
import asyncio

class SignInCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.announcement_task = self.bot.loop.create_task(self.announcement_check())

    def cog_unload(self):
        self.announcement_task.cancel()

    async def announcement_check(self):
        while not self.bot.is_closed():
            try:
                await self.perform_announcement_actions()
                print(datetime.now())
                # Calculate the sleep duration until the next announcement period
                next_announcement = self.calculate_next_announcement_time()
                await discord.utils.sleep_until(next_announcement)
            except Exception as e:
                print(f"An error occurred: {e}")
                # If there's an error, wait a minute and try again
                await asyncio.sleep(60)

    async def perform_announcement_actions(self):
        channel_id = 1108401001003757568  # Replace with your channel ID
        channel = self.bot.get_channel(channel_id)
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        if (today.month, today.day) == (11, 1) or (today.month, today.day) == (5, 1) or (today.month, today.day) == (11, 6) :
            if time(21, 00) <= current_time <= time(21, 10):  # 在 9:00 到 9:05 的時間範圍內
                print("start")
                self.sent_message_id, self.end_datetime = await self.setup_announcement(channel)
        if (today.month, today.day) == (11, 22) or (today.month, today.day) == (5, 22) or (today.month, today.day) == (11, 6):
            if time(21, 15) <= current_time <= time(21, 20):  # 在 9:00 到 9:05 的時間範圍內
                await self.notify_users_after_deadline(channel, self.end_datetime, channel.guild)

    async def setup_announcement(self,channel):

        special_role = discord.utils.get(channel.guild.roles, name='未簽到')

        send_datetime = datetime.now()
        end_datetime = send_datetime + timedelta(minutes=10)

        end_date_str = end_datetime.strftime('%Y/%m/%d %H:%M')

        message_content = (
        f'<@&{special_role.id}>每半年一次的群組大掃除又來啦～\n'
        f'群組進來了不少小夥伴，與此同時增加了不少幽靈人口與殭屍(無主)帳號，因此為了清除：\n\n'

        f'1. 遺失帳號的小夥伴們創了新帳號入群，遺留在群組內的殭屍(無主)帳號\n'
        f'2. 過久沒使用但依然留在群組的小號\n'
        f'3. 進群後從未發聲、發言，也對群組"漠不關心"的號\n\n'
        f'請有看到此篇公告的各位，幫我按個「👍」，沒有按「👍」的帳號將視為殭屍(無主)帳號並清出群組，統計到{end_date_str}截止，謝謝大家！\n\n'

        f'※ 針對第 3 點進行補充，可以默默當個潛水員這是「沒有問題的」！！！但請先浮出水面幫我留下你的「👍」再潛回去吧{emoji.get_emoji("cute")}\n'
        f'※ 「不要」回應除了「👍」之外的其他符號，會不計入簽到 \n'

        )
        msg = await self.send_announcement(channel, message_content, "👍", send_datetime)
        return msg.id,end_datetime
    
    
    async def send_announcement(self, channel, message, reaction, send_datetime):
        role_name_to_assign = "未簽到"
        role_to_assign = discord.utils.get(channel.guild.roles, name=role_name_to_assign)

        for member in channel.guild.members:
            await member.add_roles(role_to_assign)
        print("member ready")

        while True:
            current_datetime = datetime.now()
            if current_datetime >= send_datetime:
                msg = await channel.send(message)
                await msg.add_reaction(reaction)
                break
        return msg
        
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if datetime.now() <= self.end_datetime and not user.bot:  # Checking if current time is before the end_datetime
            if reaction.message.id == self.sent_message_id and not user.bot:  # Checking if the reaction was on the announcement message and not from a bot
                guild = reaction.message.guild
                role = discord.utils.get(guild.roles, name="未簽到")  # Getting the role
                if role in user.roles:  # Checking if user has the role
                    await user.remove_roles(role)

    def calculate_next_announcement_time(self):
        # Logic to calculate the next announcement time based on your specific needs
        # For example, if you want to execute on May 1st and November 1st at 18:00:
        now = datetime.now()
        next_may = datetime(now.year if now.month < 5 or (now.month == 5 and now.day < 1) else now.year + 1, 5, 1, 18, 0)
        next_nov = datetime(now.year if now.month < 11 or (now.month == 11 and now.day < 1) else now.year + 1, 11, 1, 18, 0)
        test_time = datetime(now.year, now.month, now.day, 21, 0)
        #if now > test_time:
        #  test_time = test_time + timedelta(days=1)
        return test_time

        # Return the closest future date
        #return min(next_may, next_nov, key=lambda d: d if d > now else datetime.max)

    # The rest of your methods go here
    async def notify_users_after_deadline(self, channel, deadline, guild):
        while True:
            current_datetime = datetime.now()
            if current_datetime >= deadline:
                await channel.send("簽到已結束")
                role = discord.utils.get(guild.roles, name="未簽到")
                for member in guild.members:
                    if role in member.roles:
                        pass
                        #await member.send(f'測試版!!!!您未完成簽到！會把您先請出群組，若有緣再相見吧{emoji.get_emoji("cute")}')
                break
        print ("finish")

async def setup(bot):
    await bot.add_cog(SignInCog(bot))
