import discord
from discord.ext import commands
from core.classes import cog_extension
import numpy as np
import asyncio
import random
import os
import sys
sys.path.insert(0, os.getcwd()+"/API")
import buttonConfig as BC
import emoji
from typing import Union

class play_function(cog_extension) :

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



    @commands.command()
    async def 運勢(self,ctx,*,fortune_type = None) :
        specific_channel_id = 1106479974975799317
        channel_link = f"https://discord.com/channels/953292249763053569/1106479974975799317"
        
        if ctx.channel.id == specific_channel_id :
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
        else :
            sent_message = await ctx.channel.send(content = f"親~要到這裡輸入指令喔~{channel_link}")
            await asyncio.sleep(1)
            await ctx.message.delete()
            await asyncio.sleep(5)
            await sent_message.delete()
            

async def setup(bot) :
    await bot.add_cog(play_function(bot))