from discord.ext import commands
from core.classes import *
from API.modal import *
import API.api as api
import API.emoji as emoji
import random,re,discord,json

with open('setting.json','r',encoding='utf8') as jfile :
  jdata = json.load(jfile)

class play_function(cog_extension) :
    @commands.Cog.listener
    async def on_member_join(self,member):
        dm_channel = await member.create_dm()
        await dm_channel.send(f'歡迎來到我們的粉絲群！請回答下列問題，讓我們協助你正確更改群組暱稱')
        await dm_channel.send('請告訴我你的youtube名稱，例如:奶茶貓')

        def check(message):
            return message.author == member and message.channel == dm_channel

        message = await self.bot.wait_for('message', check=check)
        name = message.content
        await dm_channel.send('請告訴我你的第五名字，例如:這是一隻熊')
        message = await self.bot.wait_for('message', check=check)
        idv_name = message.content
        nickname = f"{name} ({idv_name})"
        
        channel_link = f"<#953621940415922216>"

        await member.edit(nick=nickname)
        await dm_channel.send(f'我已經將你的暱稱設為 {nickname}')
        await dm_channel.send(f'請點擊連結{channel_link}並閱讀規則後，在 #粉絲群規則簽到 根據規則指定之固定格式簽到\n("我是xxx，已閱讀完群組規則並同意遵守"，xxx請填入您的暱稱)\n以獲取"彩色的熊貓小夥伴"身分組。')
    
    @commands.Cog.listener
    async def on_member_remove(self,member):
        DCidx = member.id
        #查詢 DCidx 是否存在於退出清單中
        _,result = api.isDCIdxInWithdrawList(member.id)
        if result :
            return
        else :
            #新增 DCidx 到退出歷史資料庫中
            _,result = api.addWithdrawListMember(DCidx)

    @commands.Cog.listener
    async def on_message(self,message):
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
        if len(message.mentions) == 1 and self.bot.user.mentioned_in(message) and message.reference is None:
            channel_send = await message.author.create_dm()
        response = random.choice(jdata["responses"])
        await message.delete()
        await channel_send.send(response)  
            
        await self.bot.process_commands(message)

async def setup(bot) :
    await bot.add_cog(play_function(bot))