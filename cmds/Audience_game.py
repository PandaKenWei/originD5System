import re
import asyncio
import discord
from discord.ext import commands
from datetime import datetime

import API.api as api
import API.emoji as emoji
import API.buttonConfig as BC
from core.classes import *


on_going_commands = {}

class Audience_game(cog_extension):
     
    # 基本資料提取 - ['第五暱稱','yt暱稱'] = self.__get_name(nick name)
    async def __get_name(self,full_name):

        # 切割暱稱
        name_parts = re.split(r'\(|（', full_name)
        yt_name = name_parts[0].strip()  #yt暱稱

        if len(name_parts) > 1:
            V_name = re.split(r'\)|）', name_parts[1])[0]  #第五暱稱
        else:
            V_name = ''

        return V_name, yt_name

    # 基本訊息 - ['帳號','密碼']
    async def __userInfo(self,ctx,channel_send):
        def check(msg):
            #return msg.author == ctx.author
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author
        

        while True:
            await channel_send.send("創建您的報名帳號： (名稱由4-20個中文、英文、數字組成)\n此帳號用途如下 : \n1.使用其他dc帳號報名\n2.使用其他dc帳號修改資料")
            msg = await self.bot.wait_for("message", check=check)
            count_name = msg.content
            # 檢查 count_name 是否只包含中文、英文、數字
            if re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]{4,20}$', count_name):
                break
            else:
                await channel_send.send(f"帳號名稱格式有誤，請重新輸入 {emoji.get_emoji('sad')}")

        while True:
            await channel_send.send("創建您的報名密碼： (密碼需由6-12字英數組成)\n此密碼用途如下 : \n1.使用其他dc帳號報名\n2.修改資料")
            msg = await self.bot.wait_for("message", check=check)
            count_key = msg.content
            # 檢查 count_name 是否只包含英文、數字
            if re.match(r'^[a-zA-Z0-9]{6,12}$', count_key):
                break
            else:
                await channel_send.send(f"密碼只能包含英文、數字，請重新輸入 {emoji.get_emoji('funny')}")

        return count_name,count_key

    # 基本訊息 - ['求生段位', '監管段位','求生區段','監管區段','第五暱稱','YT暱稱']
    async def __basic_info(self,userIdx,channel_send,full_name):

        V_name,yt_name = await self.__get_name(full_name)
    
        segment_dic =  {'一階':'一區','二階':'二區','三階':'二區','四階':'三區','五階':'三區','六階':'四區','七階':'四區','巔峰七階':'五區'}

        buttons = [BC.create_button(label,settings) for label, settings in BC.buttonRank.items()]
        view = BC.ModelButtons(buttons)
        asyncio.create_task(channel_send.send('請點選你的求生歷史最高段位', view=view))
        survivor_rank = await view.wait_for_click()
        survivor_seg = segment_dic[survivor_rank]

        buttons = [BC.create_button(label,settings) for label, settings in BC.buttonRank.items()]
        view = BC.ModelButtons(buttons)
        asyncio.create_task(channel_send.send('請點選你的監管歷史最高段位', view=view))
        hunter_rank = await view.wait_for_click()
        hunter_seg = segment_dic[hunter_rank]


        # userIdx,求生段位,監管段位,求生區段,監管區段,第五暱稱,yt暱稱
        data_dic = {
            'userIdx':userIdx,
            'highestHumanRank':survivor_rank,
            'highestHunterRank':hunter_rank,
            'humanSegment': survivor_seg,
            'hunterSegment':hunter_seg,
            'D5name':V_name,
            'YTname':yt_name
        }
        return data_dic

    # 觀眾場訊息 - [ '殿堂', '區選', '時段','備註','求生報名','監管報名']
    async def __regist_info(self,ctx,userIdx,form_date,channel_send):
        def check(msg):
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author

        CurrentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        
        buttons = [BC.create_button(label,settings) for label, settings in BC.buttonSide.items()]
        view = BC.ModelButtons(buttons)
        asyncio.create_task(channel_send.send('報名陣營：', view=view))
        reg_side = await view.wait_for_click()

        if reg_side == '求生' :
            reg_sur,reg_hun = True,False
        elif reg_side == '監管' :
            reg_sur,reg_hun = False,True
        elif reg_side == '雙陣營' :
            reg_sur,reg_hun = True,True
        

        if reg_hun :
            
            #是否開殿堂
            buttons = [BC.create_button(label,settings) for label, settings in BC.buttonOpen.items()]
            view = BC.ModelButtons(buttons)
            asyncio.create_task(channel_send.send(f'是否開殿堂：', view=view))
            choose_1 = await view.wait_for_click()
            
            #是否開區域選擇    
            buttons = [BC.create_button(label,settings) for label, settings in BC.buttonOpen.items()]
            view = BC.ModelButtons(buttons)
            asyncio.create_task(channel_send.send(f'是否開區域選擇：', view=view))
            choose_2 = await view.wait_for_click()

        else :
            choose_1,choose_2 =False,False

        await channel_send.send("特殊時段要求：(若無時段要求，回傳'無'即可)\n 格式：2125-2200，請依照格式填寫喔，若無依照格式填寫則忽略不記")
        msg = await self.bot.wait_for("message", check=check)
        reg_time = msg.content

        regex = r"\b\d{4}-\d{4}\b"
        matches = re.findall(regex, reg_time)

        if matches:
            reg_time = ';'.join(matches)
        else:
            reg_time = ''
    
        await channel_send.send("備註：(若無備註，回傳'無'即可)")
        msg = await self.bot.wait_for("message", check=check)
        reg_others = msg.content

        if reg_others == "無" or reg_others == "无":
            reg_others = ''
        else:
            reg_others = reg_others

        data = {
            'userIdx': userIdx,
            'isHallLevel': choose_1, #殿堂
            'isReginalSelection': choose_2, #區選
            'availableTime' : reg_time, #時段
            'isApplyHuman' : reg_sur, # 監管
            'isApplyHunter' : reg_hun, #求生
            'date' : form_date, #表單日期
            'remark' : reg_others, #備註
            'applyCurrentTime' : CurrentTime, #報名時間(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }

        return data
    
    # 報名資料輸出 - ['第五暱稱','求生-段位','監管-段位-殿堂-區選','時段','備註','報名日期']
    async def __print_outcome(self,data,date,V_name) :
        change = '\n'
    
        HallLevel = '；殿堂-開' if data['isHallLevel'] and data['isApplyHunter'] else '' if not data['isApplyHunter'] else '；殿堂-不開' #殿堂
        ReginalSelection = '；區選-開' if data['isReginalSelection'] and data['isApplyHunter'] else '' if not data['isApplyHunter'] else '；區選-不開' #殿堂
        TimeRemark = '' if data['availableTime'] == '' else f'（{data["availableTime"]}）' #時間
        Remark = '' if data['remark'] == '' else f'{change}備註：{data["remark"]}' #備註

        #判斷陣營
        if data['isApplyHuman'] and data['isApplyHunter'] :
            play_side = '\n陣營：雙陣營'
        elif data['isApplyHuman'] :
            play_side = '\n陣營：求生'
        elif data['isApplyHunter'] :
            play_side = '\n陣營：監管'
        else : 
            play_side = '無資料'

        data_output = {
          'name':V_name,
          'date':date,
          'playside' :play_side,
          'isHallLevel':HallLevel,
          'isReginalSelection':ReginalSelection,
          'availableTime' :TimeRemark,
          'remark': Remark
          }
        outcome = f"\n{data_output['name']} {data_output['date']}觀眾場{data_output['availableTime']}{data_output['playside']}{data_output['isHallLevel']}{data_output['isReginalSelection']}{data_output['remark']}"
        return outcome

    # 提取表單日期 - form_date:表單日期(M/D)；formatted_date:資料庫表單日期(Y/M/D)
    async def __formdate_info(self,channel_id):
        # "預約表單"頻道的最後一個訊息(.history(limit=1))內的日期 - 即為參與觀眾場的日期 (form_date)
        async for message in self.bot.get_channel(channel_id).history(limit=1):
            # 表單日期
            form_date = re.search(r'\b\d{1,2}/\d{1,2}\b', message.content).group() 
            # 報名月份
            date_month = form_date.split('/')[0]
            # 防止跨年度的錯誤 -> current_year : 若表單月份(ex.1月)比發出表單的月份(ex.12月)小，則 年分+1
            current_year = message.created_at.year + 1 if message.created_at.month > int(date_month) else message.created_at.year 
            # 報名日期 for 資料庫的格式
            formatted_date = f"{current_year}/{form_date}"
            return form_date,formatted_date

    # 已有完整帳號的報名流程 : 確認是否有前次報名資料 -> 有 => 確認本次是否報名 -> 是：修改/不修改；否：沿用上次/不沿用上次；沒有 => 填寫報名資料
    async def __exist_user_applygame(self,ctx,dc_id,V_name,form_date,formatted_date,channel_send):
        
        # getUserIdx - dc_id 抓取 UserIdx
        _, UserIdx = api.getUserIdx(dc_id)

        # checkSameD5name - UserIdx 抓取 資料庫第五暱稱
        _, D5name = api.checkSameD5name(UserIdx) # 資料庫內第五暱稱
        
        # 比對第五名稱是否相同(群組暱稱-V_name vs 資料庫-D5name)，如果不相同，修改資料庫第五暱稱
        if V_name != D5name :
            # updateD5name (UserIdx,目前第五暱稱) -> 修改資料庫第五暱稱為目前第五暱稱
            _, _ = api.updateD5name(UserIdx, V_name)
        
        # isAnyGameListFromUserIdx(UserIdx)-確認是否存在對局資料
        _,AnyGameList = api.isAnyGameListFromUserIdx(UserIdx) 
        
        # 若有對局資料 -> 確認本次是否有報名；若沒有對局資料 -> 填寫對局資料
        if AnyGameList :

            # 提取最近一次的觀眾場資料 ('殿堂', '區選', '時段','備註','求生報名','監管報名')
            _,ex_data = api.getLastApplyInfo(UserIdx)

            # isApply - date_isApply -> None or updateIdx
            _,date_isApply = api.isApply(UserIdx, formatted_date)

            # not date_isApply is None : 當次已有報名資料 -> 是否修改本次報名資料
            if not date_isApply is None: 
                # 輸出本次報名資料供確定
                output_str = await self.__print_outcome(ex_data,form_date,V_name)
                await channel_send.send(f'本次報名資料：{output_str}')

                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonYN.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send(f'是否修改本次報名資料?', view=view))
                ans = await view.wait_for_click()

                # 不改本次資料(ans == "N"):break
                # 修改本次資料(ans == "Y"):填寫觀眾場資料(__regist_info)
                if ans == "N" :
                    await channel_send.send(f"謝謝你的熱情參與，已為你報名{form_date}觀眾場 {emoji.get_emoji('cute')}")
                elif ans == "Y" :
                    # 觀眾場資訊 - 'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
                    data_reg = await self.__regist_info(ctx,UserIdx,formatted_date,channel_send)
                    # 修改觀眾場資料及報名日期：updateApply(update_apply_info_dict, updateIdx)
                    _, _ = api.updateApply(data_reg, date_isApply)
                    await channel_send.send(f"謝謝你的熱情參與，已為你報名觀眾場 {emoji.get_emoji('cute')}")
                    # 輸出本次報名資料供確定
                    output_str = await self.__print_outcome(data_reg,form_date,V_name)
                    await channel_send.send(output_str)

            # 當次尚未有報名資料
            else:
                # 如果dc_id已存在，使用存在的基本資料数据(basic_info)
                # 輸出前次報名資料供參考
                ex_date = datetime.strptime(ex_data['date'],'%a, %d %b %Y %H:%M:%S %Z')
                ex_formatted_date = ex_date.strftime('%m/%d')
                output_str = await self.__print_outcome(ex_data,ex_formatted_date,V_name)
                await channel_send.send(f'前次報名資料如下:{output_str}')

                # 選擇是否沿用上次資料 (Y - 是；N - 否)
                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonYNC.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send(f'是否沿用報名資料?', view=view))
                ans = await view.wait_for_click()

                # Y (沿用上次資料) -> 修改報名日期
                # N (不沿用上次資料) -> 重新填寫觀眾場報名資料(regist_info -> applyGame)
                if ans == 'Y' :
                    CurrentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # 修改報名日期
                    data_reg = {
                        'userIdx': UserIdx,
                        'isHallLevel': ex_data['isHallLevel'], #殿堂
                        'isReginalSelection': ex_data['isReginalSelection'], #區選
                        'availableTime' : ex_data['availableTime'], #時段
                        'isApplyHuman' : ex_data['isApplyHuman'], # 監管
                        'isApplyHunter' : ex_data['isApplyHunter'], #求生
                        'date' : formatted_date, #表單日期
                        'remark' : ex_data['remark'], #備註
                        'applyCurrentTime' : CurrentTime, #報名時間(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                    # 新增本次報名資料 applyGame：'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
                    _, _ = api.applyGame(data_reg)
                    await channel_send.send(f"謝謝你的熱情參與，已為你報名{form_date}觀眾場 {emoji.get_emoji('cute')}")

                    # 輸出本次報名資料供確定
                    output_str = await self.__print_outcome(data_reg,form_date,V_name)
                    await channel_send.send(output_str)

                elif ans == 'N' :
                    # 填寫觀眾場報名資料
                    data_reg = await self.__regist_info(ctx,UserIdx,formatted_date,channel_send)
                    # 新增本次報名資料 applyGame：'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
                    _, _ = api.applyGame(data_reg)
                    # 修改觀眾場資料及報名日期
                    await channel_send.send(f"謝謝你的熱情參與，已為你報名{form_date}觀眾場 {emoji.get_emoji('cute')}")
                    # 輸出本次報名資料供確定
                    output_str = await self.__print_outcome(data_reg,form_date,V_name)
                    await channel_send.send(output_str)
                elif ans == "C":
                    await channel_send.send(f"已為你取消本次報名 {emoji.get_emoji('cute')}")

        else :
            # 填寫觀眾場報名資料
            data_reg = await self.__regist_info(ctx,UserIdx,formatted_date,channel_send)
            # 新增本次報名資料 applyGame：'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
            _, _ = api.applyGame(data_reg)
            # 修改觀眾場資料及報名日期
            await channel_send.send(f"謝謝你的熱情參與，已為你報名{form_date}觀眾場 {emoji.get_emoji('cute')}")
            # 輸出本次報名資料供確定
            output_str = await self.__print_outcome(data_reg,form_date,V_name)
            await channel_send.send(output_str)
            
    # 修改區段
    async def __updateSeg(self,ctx,side,dc_id,userIdx,channel_send):

        buttons = [BC.create_button(label,settings) for label, settings in BC.buttonSeg.items()]
        view = BC.ModelButtons(buttons)
        asyncio.create_task(channel_send.send(f'請輸入{side}變更後之區段', view=view))
        seg = await view.wait_for_click()
        side_dic = {"求生":"human","監管":"hunter"}
        _,_ = api.updateSegment(userIdx,side_dic[side],seg)
        # 成功修改區段後，將成功訊息傳入"#議事堂"
        # '#議事堂'頻道ID
        output_channel_id = 981528237438038068
        output_channel = self.bot.get_channel(output_channel_id)
        # 被修改人之訊息
        member = ctx.guild.get_member(int(dc_id))
        # 成功修改訊息 - 更改者
        await channel_send.send(f"已成功將 {member.nick} 之{side}區段改為{seg} {emoji.get_emoji('cute')}")
        # 成功修改訊息 - 群組
        await output_channel.send(f'{ctx.author.nick} 已將 {member.nick} 之{side}區段改為{seg}')

    @is_in_channel(1131497952918110299)
    @commands.command()
    async def 報名(self,ctx, member: discord.Member = None):
        def check(msg):
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author

        dc_commands = ctx.author.id
        channel_send = await ctx.author.create_dm()

        # 如果已有執行中的 "!報名" 則不執行
        if dc_commands in on_going_commands:
            await channel_send.send(f"還有正在進行中的{on_going_commands[dc_commands]}要先完成喔{emoji.get_emoji('cute')}")
            return 

        try :
            # 標記此用戶有一個進行中的命令 -> 防止重複運行此指令
            on_going_commands[dc_commands] = "報名"

            # 如果 member沒有覆值，則抓取發出指令人的dc_id、使用命令者的暱稱
            if member is None: 
                dc_id = ctx.author.id
                nick_name = ctx.author.nick if ctx.author.nick else ctx.author.name

            # 如果用戶有標記別人
            else:   
                # dc_id為member(被@的人)的id
                dc_id = member.id
                # nick_name 為member(被@的人)的暱稱
                nick_name = member.nick if member.nick else member.name

                # 詢問指令發送者要查詢的帳號和密碼
                await channel_send.send(f"請輸入 {member.mention} 的帳號：")
                account_message = await self.bot.wait_for('message', check=check)
                account = account_message.content

                await channel_send.send(f"請輸入 {member.mention} 的密碼：")
                password_message = await self.bot.wait_for('message', check=check)
                password = password_message.content

                # 在這裡，你可以使用帳號和密碼去查詢你的資料庫並進行操作
                # isDCIdxTheSameACPW(data)，並且它會返回是否成功
                queryData = {
                    'account':account,
                    'password':password,
                    'DCidx':str(dc_id),
                }
                state, result = api.isDCIdxTheSameACPW(queryData)

                # 如果成功，你可以讓機器人發送一條消息
                if result:
                    await channel_send.send(f"{member.mention} 身分確認成功 {emoji.get_emoji('cute')}")
                else:
                    await channel_send.send(f"{member.mention} 的帳號密碼確認失敗，若有需要請重新於群組輸入'!報名'  {emoji.get_emoji('sad')}")
                    return

            # 檢查資料庫內是否已存在同id之dc資料 - return api狀態,id是否存在
            state, result = api.isUserExist(dc_id)

            # 如果api正常運行(state == True)，則返回 id是否存在
            check_dc_exist = result if state  else print("api 問題")
            #check_dc_exist = False

            # 目前第五暱稱,目前yt暱稱 = await self.__get_name(ctx) 
            V_name,_ = await self.__get_name(nick_name)

            # "#預約表單"的頻道ID
            channel_id = 953324370355433562  
            #小群頻道ID
            #channel_id =1062284819846934618

            # form_date,formatted_date: 表單日期(M/D),資料庫表單日期(Y/M/D)
            form_date,formatted_date = await self.__formdate_info(channel_id)

            # if dc_id存在(check_dc_exist == True)
            if check_dc_exist : 
                # 本次已有報名資料：修改/不修改
                # 本次尚無報名資料：沿用/不沿用 
                await self.__exist_user_applygame(ctx,dc_id,V_name,form_date,formatted_date,channel_send)

            else:
                # 如果 dc_id不存在，進行註冊過程
                await channel_send.send(f"歡迎新朋友報名觀眾場!!\n第一次報名前需要為你建立一個報名觀眾場的帳戶，請耐心填寫喔 {emoji.get_emoji('cute')}")

                # 規則同意聲明
                #規則連結
                channel_link = "<#1106157183734911026>"
                #小群規則
                #channel_link = "<#1004279805094666253>" 
                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonYN.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send(f'請先點擊連結{channel_link}並詳閱規則，未來若透過dc機器人報名觀眾場視同報名者同意遵守相關規則。', view=view))
                correct_message = await view.wait_for_click()

                if correct_message == "Y" :  
                    # 基本資訊 - 帳號密碼
                    user_account, user_password = await self.__userInfo(ctx,channel_send)
                    # createUser(account, password, DCidx) -> 將帳號密碼加進資料庫
                    _, _ = api.createUser(user_account, user_password,dc_id)
                    # 取得 userIdx
                    _, UserIdx = api.getUserIdx(dc_id)
                    # 基本資料 - 段位、區間、暱稱
                    data_basic = await self.__basic_info(UserIdx,channel_send,nick_name)
                    #createUserInfo(userIdx, highestHumanRank, highestHunterRank, humanSegment, hunterSegment, D5name, YTname) -> 將第五基本資料加進資料庫
                    _, _ = api.createUserInfo(data_basic)
                    await channel_send.send(f"恭喜你!帳戶成功建立啦，接著是觀眾場報名資料～gogo！ {emoji.get_emoji('gogo')}\np.s.未來報名可選擇沿用之前的報名資料喔 {emoji.get_emoji('cute')}")

                    # 觀眾場資訊
                    data_reg = await self.__regist_info(ctx,UserIdx,formatted_date,channel_send)
                    # 'userIdx',殿堂,區選,時段,監管,求生,表單日期,備註,報名時間
                    _, _ = api.applyGame(data_reg)

                    await channel_send.send(f"謝謝你的熱情參與，已為你報名{form_date}觀眾場 {emoji.get_emoji('cute')}")
                    # 輸出本次報名資料供確定
                    output_str = await self.__print_outcome(data_reg,form_date,V_name)
                    await channel_send.send(output_str)

                elif correct_message == "N" :
                    await channel_send.send(f'若日後同意遵守規則歡迎再次報名 {emoji.get_emoji("cute")}')

        finally:
            del on_going_commands[dc_commands]  # 無論命令是否成功完成，都確保移除此條目
            
    @commands.command()
    async def 區段(self,ctx:commands.Context):

        def check(msg:discord.Message):
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author

        await ctx.message.delete()
        # 私訊使用指令者
        channel_send = await ctx.author.create_dm()

        #允許使用此指令的身分組
        allowed_role = ['YT管理員','房管-主播級']
        user_roles = [role.name for role in ctx.author.roles]

        if any (role in user_roles for role in allowed_role):
            while True :
                await channel_send.send(f'請輸入更改帳戶之dc_id')
                dc_id_message = await self.bot.wait_for('message', check=check)
                dc_id = re.search(r'\d+', dc_id_message.content)
                if dc_id is not None :
                    dc_id = dc_id.group()
                    # 取得 userIdx
                    _, UserIdx = api.getUserIdx(dc_id)
                    if type(UserIdx) == int :
                        break
                    else :
                        await channel_send.send(f"此dc_id無對應資料")
                else :
                    await channel_send.send(f'請輸入正確id')

            buttons = [BC.create_button(label,settings) for label, settings in BC.buttonSide.items()]
            view = BC.ModelButtons(buttons)
            asyncio.create_task(channel_send.send('更改區段之陣營：', view=view))
            side = await view.wait_for_click()
    
            if side == "雙陣營" : 
                await self.__updateSeg(ctx,'求生',dc_id,UserIdx,channel_send)
                await self.__updateSeg(ctx,'監管',dc_id,UserIdx,channel_send)

            else : 
                await self.__updateSeg(ctx,side,dc_id,UserIdx,channel_send)

        else :
            sent_message = await ctx.send(f"非YT管理員不得修改區段喔 {emoji.get_emoji('cute')}",delete_after=5)
    @is_in_channel(1131497952918110299)
    @commands.command()
    async def 取消報名(self,ctx:commands.Context, member: discord.Member = None):
        def check(msg:discord.Message):
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author

        dc_commands = ctx.author.id
        channel_send = await ctx.author.create_dm()

        # 如果已有執行中的 "!取消報名" 則不執行
        if dc_commands in on_going_commands:
            await channel_send.send(f"還有正在進行中的{on_going_commands[dc_commands]}要先完成喔{emoji.get_emoji('cute')}")
            return 
    
        try :
            # 標記此用戶有一個進行中的命令 -> 防止重複運行此指令
            on_going_commands[dc_commands] = "取消報名"

            # 如果 member沒有覆值，則抓取發出指令人的dc_id、使用命令者的暱稱
            if member is None: 
                dc_id = ctx.author.id
                nick_name = ctx.author.nick if ctx.author.nick else ctx.author.name

            # 如果用戶有標記別人
            else:   
                # dc_id為member(被@的人)的id
                dc_id = member.id
                # nick_name 為member(被@的人)的暱稱
                nick_name = member.nick if member.nick else member.name

                # 詢問指令發送者要查詢的帳號和密碼
                await channel_send.send(f"請輸入 {member.mention} 的帳號：")
                account_message = await self.bot.wait_for('message', check=check)
                account = account_message.content

                await channel_send.send(f"請輸入 {member.mention} 的密碼：")
                password_message = await self.bot.wait_for('message', check=check)
                password = password_message.content

                # 在這裡，你可以使用帳號和密碼去查詢你的資料庫並進行操作
                # isDCIdxTheSameACPW(data)，並且它會返回是否成功
                queryData = {
                    'account':account,
                    'password':password,
                    'DCidx':str(dc_id),
                }
                state, result = api.isDCIdxTheSameACPW(queryData)

                # 如果成功，你可以讓機器人發送一條消息
                if result:
                    await channel_send.send(f"{member.mention} 身分確認成功 {emoji.get_emoji('cute')}")
                else:
                    await channel_send.send(f"{member.mention} 的帳號密碼確認失敗，若有需要請重新於群組輸入'!取消報名'  {emoji.get_emoji('sad')}")
                    return

            # 檢查資料庫內是否已存在同id之dc資料 - return api狀態,id是否存在
            state, result = api.isUserExist(dc_id)
            # 如果api正常運行(state == True)，則返回 id是否存在
            check_dc_exist = result if state  else print("api 問題")
            #check_dc_exist = False

            # 目前第五暱稱,目前yt暱稱 = await self.__get_name(ctx) 
            V_name,_ = await self.__get_name(nick_name)

            # "#預約表單"的頻道ID
            channel_id = 953324370355433562  
            #小群頻道ID
            #channel_id =1062284819846934618

            # form_date,formatted_date: 表單日期(M/D),資料庫表單日期(Y/M/D)
            form_date,formatted_date = await self.__formdate_info(channel_id)

            # if dc_id存在(check_dc_exist == True)
            if check_dc_exist : 
                # getUserIdx - dc_id 抓取 UserIdx
                _, UserIdx = api.getUserIdx(dc_id)
                # checkSameD5name - UserIdx 抓取 資料庫第五暱稱
                _, D5name = api.checkSameD5name(UserIdx) # 資料庫內第五暱稱

                # 比對第五名稱是否相同(群組暱稱-V_name vs 資料庫-D5name)，如果不相同，修改資料庫第五暱稱
                if V_name != D5name :
                    # updateD5name (UserIdx,目前第五暱稱) -> 修改資料庫第五暱稱為目前第五暱稱
                    _, _ = api.updateD5name(UserIdx, V_name) 

                # 提取最近一次的觀眾場資料 ('殿堂', '區選', '時段','備註','求生報名','監管報名')
                _,ex_data = api.getLastApplyInfo(UserIdx)

                # isApply - date_isApply -> None or updateIdx
                _,date_isApply = api.isApply(UserIdx, formatted_date)

                # not date_isApply is None : 當次已有報名資料 -> 是否修改本次報名資料
                if not date_isApply is None: 
                    # 輸出本次報名資料供確定
                    output_str = await self.__print_outcome(ex_data,form_date,V_name)
                    await channel_send.send(f'本次報名資料：{output_str}')

                    buttons = [BC.create_button(label,settings) for label, settings in BC.buttonYN.items()]
                    view = BC.ModelButtons(buttons)
                    asyncio.create_task(channel_send.send(f'是否刪除本次報名資料?', view=view))
                    ans = await view.wait_for_click()

                    # 不刪除本次資料(ans == "N"):break
                    # 刪除本次資料(ans == "Y"):deleteApply(UserIdx, formatted_date)
                    if ans == "N" :
                        await channel_send.send(f"謝謝你的熱情參與，已為你保留{form_date}觀眾場之報名 {emoji.get_emoji('cute')}")
                    elif ans == "Y" :
                        # 刪除觀眾場資訊 - deleteApply(UserIdx, formatted_date)
                        _,_ = api.deleteApply(UserIdx, formatted_date)
                        await channel_send.send(f"已為你刪除{form_date}觀眾場之報名 {emoji.get_emoji('sad')}")

                # 當次尚未有報名資料
                else:
                    await channel_send.send(f"你還沒有報名{form_date}觀眾場喔 {emoji.get_emoji('cute')}")
            else :
                await channel_send.send(f"你尚未創立觀眾場帳號喔 {emoji.get_emoji('cute')}")

        finally:
            del on_going_commands[dc_commands]  # 無論命令是否成功完成，都確保移除此條目

    @commands.command()
    async def 修改(self,ctx:commands.Context, member: discord.Member = None):
        def check(msg:discord.Message):
            return msg.channel.type == discord.ChannelType.private and msg.author == ctx.author

        dc_commands = ctx.author.id
        channel_send = await ctx.author.create_dm()

        # 如果已有執行中的 "!報名" 則不執行
        if dc_commands in on_going_commands:
            await channel_send.send(f"還有正在進行中的{on_going_commands[dc_commands]}要先完成喔{emoji.get_emoji('cute')}")
            return 

        try :
            # 標記此用戶有一個進行中的命令 -> 防止重複運行此指令
            on_going_commands[dc_commands] = "修改"

            # 如果 member沒有覆值，則抓取發出指令人的dc_id、使用命令者的暱稱
            if member is None: 
                dc_id = ctx.author.id
                nick_name = ctx.author.nick if ctx.author.nick else ctx.author.name
                _,account = api.getAccountFromDCidx(dc_id)                

            # 如果用戶有標記別人
            else:   
                # dc_id為member(被@的人)的id
                dc_id = member.id
                # nick_name 為member(被@的人)的暱稱
                nick_name = member.nick if member.nick else member.name

                # 詢問指令發送者要查詢的帳號和密碼
                await channel_send.send(f"請輸入 {nick_name} 的帳號：")
                account_message = await self.bot.wait_for('message', check=check)
                account = account_message.content

            await channel_send.send(f"請輸入 {nick_name} 的密碼：")
            password_message = await self.bot.wait_for('message', check=check)
            password = password_message.content

            # 在這裡，你可以使用帳號和密碼去查詢你的資料庫並進行操作
            # isDCIdxTheSameACPW(data)，並且它會返回是否成功
            queryData = {
                'account':account,
                'password':password,
                'DCidx':str(dc_id),
            }
            state, result = api.isDCIdxTheSameACPW(queryData)

            # 如果成功，你可以讓機器人發送一條消息
            if result:
                await channel_send.send(f"{nick_name} 身分確認成功 {emoji.get_emoji('cute')}")
            else:
                await channel_send.send(f"{nick_name} 的帳號密碼確認失敗，若有需要請重新於群組輸入'!修改'  {emoji.get_emoji('sad')}")
                return

            # 檢查資料庫內是否已存在同id之dc資料 - return api狀態,id是否存在
            state, result = api.isUserExist(dc_id)
            # 如果api正常運行(state == True)，則返回 id是否存在
            check_dc_exist = result if state  else print("api 問題")
            #check_dc_exist = False

            # 目前第五暱稱,目前yt暱稱 = await self.__get_name(ctx) 
            V_name,_ = await self.__get_name(nick_name)


            # if dc_id存在(check_dc_exist == True)
            if check_dc_exist : 
                # getUserIdx - dc_id 抓取 UserIdx
                _, UserIdx = api.getUserIdx(dc_id)
                # checkSameD5name - UserIdx 抓取 資料庫第五暱稱
                _, D5name = api.checkSameD5name(UserIdx) # 資料庫內第五暱稱

                # 比對第五名稱是否相同(群組暱稱-V_name vs 資料庫-D5name)，如果不相同，修改資料庫第五暱稱
                if V_name != D5name :
                    # updateD5name (UserIdx,目前第五暱稱) -> 修改資料庫第五暱稱為目前第五暱稱
                    _, _ = api.updateD5name(UserIdx, V_name) 

                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonRank.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send('請點選你的求生歷史最高段位', view=view))
                survivor_rank = await view.wait_for_click()

                _,_ = api.updateRank(UserIdx,'human', survivor_rank)

                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonRank.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send('請點選你的監管歷史最高段位', view=view))
                hunter_rank = await view.wait_for_click()

                _,_ = api.updateRank(UserIdx,'hunter', hunter_rank)

                await channel_send.send(f"已將你的段位修改為：\n求生-{survivor_rank}；監管-{hunter_rank}\n恭喜恭喜～繼續加油喔　{emoji.get_emoji('gogo')}")

            else :
                await channel_send.send(f"你尚未創立觀眾場帳號喔 {emoji.get_emoji('cute')}")

        finally:
            del on_going_commands[dc_commands]  # 無論命令是否成功完成，都確保移除此條目

    @is_in_channel(1131497952918110299)
    @commands.command()
    async def 幾區(self,ctx:commands.Context):

        dc_commands = ctx.author.id
        channel_send = await ctx.author.create_dm()

        # 如果已有執行中的 "!報名" 則不執行
        if dc_commands in on_going_commands:
            await channel_send.send(f"還有正在進行中的{on_going_commands[dc_commands]}要先完成喔 {emoji.get_emoji('cute')}")
            return 

        try :
            # 標記此用戶有一個進行中的命令 -> 防止重複運行此指令
            on_going_commands[dc_commands] = "幾區"

            dc_id = ctx.author.id
            nick_name = ctx.author.nick if ctx.author.nick else ctx.author.name

            # 檢查資料庫內是否已存在同id之dc資料 - return api狀態,id是否存在
            state, result = api.isUserExist(dc_id)
            # 如果api正常運行(state == True)，則返回 id是否存在
            check_dc_exist = result if state  else print("api 問題")
            #check_dc_exist = False

            # 目前第五暱稱,目前yt暱稱 = await self.__get_name(ctx) 
            V_name,_ = await self.__get_name(nick_name)

            # if dc_id存在(check_dc_exist == True)
            if check_dc_exist : 
                # getUserIdx - dc_id 抓取 UserIdx
                _, UserIdx = api.getUserIdx(dc_id)
                # checkSameD5name - UserIdx 抓取 資料庫第五暱稱
                _, D5name = api.checkSameD5name(UserIdx) # 資料庫內第五暱稱

                # 比對第五名稱是否相同(群組暱稱-V_name vs 資料庫-D5name)，如果不相同，修改資料庫第五暱稱
                if V_name != D5name :
                    # updateD5name (UserIdx,目前第五暱稱) -> 修改資料庫第五暱稱為目前第五暱稱
                    _, _ = api.updateD5name(UserIdx, V_name) 

                _, result = api.getSegmentFromUserIdx(UserIdx)

                buttons = [BC.create_button(label,settings) for label, settings in BC.buttonSide.items()]
                view = BC.ModelButtons(buttons)
                asyncio.create_task(channel_send.send('查詢區段之陣營：', view=view))
                reg_side = await view.wait_for_click()

                if reg_side == '求生' :
                    await channel_send.send(f"{D5name}的求生區段為：{result['humanSegment']} {emoji.get_emoji('gogo')}")
                elif reg_side == '監管' :
                    await channel_send.send(f"{D5name}的監管區段為：{result['hunterSegment']} {emoji.get_emoji('gogo')}")
                elif reg_side == '雙陣營' :
                    await channel_send.send(f"{D5name}的求生區段為：{result['humanSegment']}\n{D5name}的監管區段為：{result['hunterSegment']}")                

            else :
                await channel_send.send(f"你尚未創立觀眾場帳號喔 {emoji.get_emoji('cute')}")

        finally:
            del on_going_commands[dc_commands]  # 無論命令是否成功完成，都確保移除此條目
            
    @commands.command()
    async def 救救我啊我救我(self,ctx:commands.Context):
        dc_commands = ctx.author.id
        channel_send = await ctx.author.create_dm()

        # 如果已有執行中的 "!報名" 則不執行
        if dc_commands in on_going_commands:
            del on_going_commands[dc_commands]
            await channel_send.send(f"可以使用其他指令了喔 {emoji.get_emoji('cute')}") 

        else :
            await channel_send.send(f"沒有進行中的指令喔 {emoji.get_emoji('cute')}")
                                    
async def setup(bot:commands.Bot) :
    await bot.add_cog(Audience_game(bot))

