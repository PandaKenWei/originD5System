import discord
from discord.ext import commands
from core.classes import *
import numpy as np
import asyncio
import random
from API.modal import *
import API.buttonConfig as BC
import API.emoji as emoji
import re

class play_function(cog_extension) :

    @is_in_channel(1106479974975799317)
    @commands.command()
    async def 決鬥(self, ctx, *members: discord.Member):
                
        members = list(set(members))  # 移除重複的成員
        # 檢查是否至少有兩位玩家參與
        if len(members) < 2:
            await ctx.send("請至少輸入兩位有效的成員來玩猜拳遊戲！")
            return
        
        # 保存每個玩家的選擇
        member_choices = {}
        choices = {
            '石頭': 1,
            '剪刀': 2,
            '布': 3
        }

        for member in members:
            # 若是機器人，隨機選擇
            if member.bot:
                member_choices[member] = random.choice(['石頭', '剪刀', '布'])
                continue

            dm_channel = await member.create_dm()
            buttons = [BC.create_button(label, settings) for label, settings in BC.buttonPSS.items()]
            view = BC.ModelButtons(buttons)
            await dm_channel.send(f'請選擇石頭、剪刀或布！', view=view)

            try:
                user_choice = await asyncio.wait_for(view.wait_for_click(), timeout=60)
                member_choices[member] = choices[user_choice]
            except asyncio.TimeoutError:
                await ctx.send(f"{member.mention} 沒有在時間內做出選擇，已失去遊戲資格 {emoji.get_emoji('funny')}。")
                members = [m for m in members if m != member]

        # 判斷獲勝者，這裡先考慮平局狀況，如果不是平局就看誰獲勝
        unique_choices = list(set(member_choices.values()))

        if len(unique_choices) == 1 or len(unique_choices) == 3:  # 所有人選擇都相同，平局
            draw_mentions = ", ".join([member.mention for member in members])
            await ctx.send(f"{draw_mentions} 平手！")
        else:
            # 判斷勝者。這裡只是為了演示，可能需要更複雜的邏輯來處理多人遊戲的勝負
            # 例如，當有人選擇石頭，有人選擇剪刀，其他人選擇布，該如何判定勝負？
            winners = []
            if 1 in unique_choices and 2 in unique_choices and 3 not in unique_choices:
                winners = [m for m, choice in member_choices.items() if choice == 1]
            elif 2 in unique_choices and 3 in unique_choices and 1 not in unique_choices:
                winners = [m for m, choice in member_choices.items() if choice == 2]
            elif 3 in unique_choices and 1 in unique_choices and 2 not in unique_choices:
                winners = [m for m, choice in member_choices.items() if choice == 3]

            winners_mentions = ", ".join([winner.mention for winner in winners])
            await ctx.send(f"{winners_mentions} 獲勝！")


    @is_in_channel(1106479974975799317)
    @commands.command()
    async def 運勢(self,ctx,*,fortune_type = None) :
        fortunes_ans = {"大吉":0.08,"中吉":0.11,"小吉":0.16,"吉":0.3,"小凶":0.16,"凶":0.11,"大凶":0.08}
        fortunes_reply = {"大吉":"一定會順順利利","中吉":"大膽衝一波!!","小吉":"感覺可以試試喔","吉":"小小猶豫一下!!然後上吧!!",
                            "凶":"啊啊啊啊啊看來可能會遇到點困難呢","大凶":"如果是一定要做的事，儘管前路道阻且長也不能逃避!勇敢面對吧!"}
        if fortune_type is None :
            fortunes_idx = {"大吉":0,"中吉":1,"小吉":2,"吉":3,"小凶":4,"凶":5,"大凶":6}
            fortunes = {
                "錢財" : fortunes_ans,
                "感情" : fortunes_ans,
                "事業" : fortunes_ans,
                "排位" : fortunes_ans
            }
            response = ""
            probs = [0,0,0,0,0,0]
            for category, fortune_probs in fortunes.items():
                fortune = np.random.choice(list(fortune_probs.keys()), p=list(fortune_probs.values()))
                response += f"{category}: {fortune}\n"
                probs[fortunes_idx[fortune]] += 1

            if sum(probs[0:4]) > sum(probs[4:6]) :
                reply_list = ["你身上散發了光芒！看來今天會心想事成","今天是個好日子，看來你要出好運咯","方方祝你今天大吉大利！"]
            else :
                reply_list = ["今天運勢不是很好，但是多笑就可以變好咯","雖然運勢可能不好，但也別虧待自己，買杯奶茶喝吧","方方為你加油！"]            
            response_txt = np.random.choice(reply_list)
            await ctx.send(f'本日四大運勢如下：\n{response}小總結：{response_txt}')
        else :
            fortune = np.random.choice(list(fortunes_ans.keys()), p=list(fortunes_ans.values()))
            await ctx.send(f"{fortune_type}-{fortune}:{fortunes_reply[fortune]}")
    
    
    @commands.command()
    async def 猜數字(self, ctx: commands.Context, *members: discord.Member):
        def get_yt_name(name):
            print(name)
            name_parts = re.split(r'\(|（', name)
            yt_name = name_parts[0].strip()  # yt暱稱
            return yt_name
        view = Check_start(members=members,public=not bool(len(members)))
        msg = await ctx.send("猜數字遊戲準備開始，進入確認階段，若要參加，請於90秒內點擊同意按鈕",view=view)
        try:
            await asyncio.wait_for(view.wait_for_finish(),timeout=90)
            members:list = []
            for i in view.agree_member:
                if view.agree_member[i]:
                    members.append(i)
        except asyncio.TimeoutError:
            members:list = []
            for i in view.agree_member:
                if view.agree_member[i]:
                    members.append(i)

        members = set(members) or {ctx.author}
        member_ids = {}
        for i in members:
            member_ids[i.id] = get_yt_name(i.nick)
        big, small = 100, 1
        number = random.randint(1, 100)
        turn_to = 0
        record = []
        winner = None
        await msg.delete()
        msg = await ctx.send("猜數字遊戲開始")
        while not winner:
            view = View(target_user=list(members)[turn_to])
            await msg.edit(content=f"輪到{list(members)[turn_to].mention}了，請點擊下方按鈕，在60秒內選擇", view=view)

            try:
                value = await asyncio.wait_for(view.wait_for_click(),timeout=60)
                value = int(value)
                record.append([list(members)[turn_to],value])
                await ctx.send(f"{member_ids[list(members)[turn_to].id]} 選擇了{value}")
            except asyncio.TimeoutError:
                await ctx.send(f"{member_ids[list(members)[turn_to].id]} 未在時間內選擇")
                turn_to = (turn_to + 1) % len(members)
                record.append([list(members)[turn_to],value])
                
                continue

            if value == number:
                winner = list(members)[turn_to]
            else:
                if number > value:
                    small = value
                elif number < value:
                    big = value
                await ctx.send(f"在{small}~{big}之間")
                turn_to = (turn_to + 1) % len(members)
        embed = discord.Embed()
        
        for i in range(len(record)):
            embed.add_field(name=f"第{i+1}輪 {member_ids[record[i][0].id]}", value=record[i][1], inline=False)

        await ctx.send(f"恭喜 {winner.mention}!，答案是 {number}",embed=embed)

async def setup(bot) :
    await bot.add_cog(play_function(bot))