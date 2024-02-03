import discord
from discord.ext import commands
from core.classes import cog_extension
import asyncio
import random
import API.api as api
import re


class test_fun(cog_extension):

    # 提取表單日期 - form_date:表單日期(M/D)；formatted_date:資料庫表單日期(Y/M/D)
    async def __formdate_info(self,channel_id,form_date = None):
        # "預約表單"頻道的最後一個訊息(.history(limit=1))內的日期 - 即為參與觀眾場的日期 (form_date)
        async for message in self.bot.get_channel(channel_id).history(limit=1):
            # 表單日期
            if form_date is None :
                form_date = re.search(r'\b\d{1,2}/\d{1,2}\b', message.content).group() 
            else :
                form_date = form_date
            # 報名月份
            date_month = form_date.split('/')[0]
            # 防止跨年度的錯誤 -> current_year : 若表單月份(ex.1月)比發出表單的月份(ex.12月)小，則 年分+1
            current_year = message.created_at.year + 1 if message.created_at.month > int(date_month) else message.created_at.year 
            # 報名日期 for 資料庫的格式
            formatted_date = f"{current_year}/{form_date}"
            return form_date,formatted_date


    # 將dc資料和google資料合併
    async def combined_data(self,formatted_date) :
        # dc報名資料
        _,data_dc = api.fetchAllThisData(formatted_date)

        dictRank = {
            '一階':'1', 
            '二階':'2',
            '三階':'3',
            '四階':'4',
            '五階':'5',
            '六階':'6',
            '七階':'7',
            '巔峰七階':'巔7',
            }
        
        data_dc[['highestHumanRank', 'highestHunterRank']] = data_dc[['highestHumanRank', 'highestHunterRank']].applymap(lambda x: dictRank.get(x, x))
        
        return data_dc

    # 求生資料輸出    
    async def data_survivor(self,df) :

        # 所需欄位
        survivor_col = ['D5name','highestHumanRank','humanSegment','availableTime']

        # 字串包含括號（"(" 和 ")"），在正則表達式中，它們用於定義組，所以在你的字串中添加一個反斜杠 \ 來轉義這些特殊字元，使其被視為文字字元。
        df_survivor = df.loc[df['isApplyHuman'] == True,survivor_col].reset_index(drop = True)
        
        # 新增區段排序欄位
        sort_dict = {"五區":1,"四區": 2, "三區": 3, "二區": 4,"一區":5}
        df_survivor['sort_order'] = df_survivor['humanSegment'].map(sort_dict)   
        
        # 根據區段跟時段排序
        df_survivor_seg = df_survivor.loc[df_survivor['humanSegment'].notnull()]
        df_survivor_seg.sort_values(by=['availableTime'], ascending=[True], inplace=True)
  
        # 初始化一個空字串來儲存結果
        output_str_seg = ""
        reverse_sort_dict = {v: k for k, v in sort_dict.items()}  # 用來反轉排序字典的新字典
        df_survivor_seg['seg_num'] = df_survivor_seg.groupby('sort_order')['sort_order'].transform('size')

        for order, group in df_survivor_seg.groupby('sort_order'):
            seg_num = df_survivor_seg.loc[df_survivor_seg['humanSegment'] == reverse_sort_dict[order],'seg_num'].reset_index(drop = True)[0]
            output_str_seg += f"---- {reverse_sort_dict[order]} ---- ({seg_num})\n"
            for _, row in group.iterrows():
                nickname,rank = row['D5name'],f'[{row["highestHumanRank"]}]'
                time_request = f'[{row["availableTime"]}]' if row['availableTime'] else ''
                output_str_seg += f'{nickname}{rank}{time_request}\n'
            output_str_seg += '\n'  # 新的段位區塊間的分隔符號

        return "求生：暱稱[段位]\n"+ output_str_seg

    # 監管資料輸出
    async def data_hunter(self,df) :
        
        # 所需欄位
        hunter_col = ['D5name',"highestHunterRank","hunterSegment",'isHallLevel','isReginalSelection','availableTime']

        # 依照 gameList 當日有填報屠夫的 userIdx 去調取 gameScheduleMember 的上次紀錄
        _, df_num = api.getHunterSortOrder()
        df_num['sort_order'] = df_num.index + 1
        df_hunter = df.loc[df['isApplyHunter'] == True,hunter_col].reset_index(drop = True)
        df_hunter = df_hunter.merge(df_num, on='D5name', how='left')

        # 隨機地圖函數:["軍工廠","紅教堂","聖心醫院","湖景村","里奧的回憶","月亮河公園","永眠鎮","唐人街"]
        async def map_choise():
            map_col = ["軍工廠","紅教堂","聖心醫院","湖景村","里奧的回憶","月亮河公園","永眠鎮","唐人街"]
            return map_col[random.randint(0, len(map_col)-1)]
        
        df_hunter["地圖"] = await asyncio.gather(*[map_choise() for _ in df_hunter.iterrows()])
        
        # 新增區段欄位
        sort_dict = {"五區":1,"四區": 2, "三區": 3, "二區": 4,"一區":5}
        df_hunter['sort_seg'] = df_hunter['hunterSegment'].map(sort_dict)   
        
        # 新增排序
        df_hunter_seg = df_hunter.loc[df_hunter['hunterSegment'].notnull()]
        df_hunter_seg.sort_values(by=['sort_order'], ascending=[True], inplace=True)
        df_hunter_seg = df_hunter_seg.reset_index(drop = True)
        df_hunter_seg['new_order'] = df_hunter_seg.index + 1

        # 初始化一個空字串來儲存結果
        output_str_seg= ""
        reverse_sort_dict = {v: k for k, v in sort_dict.items()}  # 用來反轉排序字典的新字典
        df_hunter_seg['seg_num'] = df_hunter_seg.groupby('sort_seg')['sort_seg'].transform('size')
        
        for order, group in df_hunter_seg.groupby('sort_seg'):
            seg_num = df_hunter_seg.loc[df_hunter_seg['hunterSegment'] == reverse_sort_dict[order],'seg_num'].reset_index(drop = True)[0]
            output_str_seg += f"---- {reverse_sort_dict[order]}---- ({seg_num})\n"
            for _, row in group.iterrows():
                nickname,rank,random_map = row['D5name'],f'[{row["highestHunterRank"]}',f'-{row["地圖"]}]'
                choose_1 = '-開' if row['isHallLevel'] else '-不開'
                choose_2 = '-開' if row['isReginalSelection'] else '-不開'
                time_request = f'[{row["availableTime"]}]' if row['availableTime'] else ''
                order = f' {row["new_order"]}'
                output_str_seg += f'{nickname}{rank}{choose_1}{choose_2}{random_map}{time_request} {order}\n'
                
            output_str_seg += '\n'  # 新的段位區塊間的分隔符號

        return "\n監管：暱稱[段位-殿堂-區選-地圖] 順序\n"+ output_str_seg 

    async def data_remark(self,df) :

        # 備註所需欄位
        remark_col = ['D5name','remark']

        # 字串包含括號（"(" 和 ")"），在正則表達式中，它們用於定義組，所以在你的字串中添加一個反斜杠 \ 來轉義這些特殊字元，使其被視為文字字元。
        df_remark = df.loc[df['remark'] != "",remark_col].reset_index(drop = True)
        
        # 設定輸出格式 : 暱稱-備註
        output_str = ""
        for _, row in df_remark.iterrows():
            nickname = row['D5name'] if row['D5name'] else ''
            remark= f'-{row["remark"]}' if row['remark'] else ''
            output_str += f'{nickname}{remark}\n'

        return "\n備註\n"+ output_str        

    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def 整理表單(self,ctx,form_date = None):

        if form_date is None :
            # "#預約表單"的頻道ID
            channel_id = 953324370355433562  
            # form_date,formatted_date: 表單日期(M/D),資料庫表單日期(Y/M/D)
            form_date,formatted_date = await self.__formdate_info(channel_id)
        else :
            # "#預約表單"的頻道ID
            channel_id = 953324370355433562  
            # form_date,formatted_date: 表單日期(M/D),資料庫表單日期(Y/M/D)
            form_date,formatted_date = await self.__formdate_info(channel_id,form_date)

        #data_google = await self.get_data_google(form_date)
        data_combined = await self.combined_data(formatted_date)
       
        # 資料輸出
        '''
        求生：
        第五暱稱[最高段位][時間區段]

        監管：
        第五暱稱[最高段位-是否開殿堂-是否開區選-地圖數字][時間區段]
        
        備註：
        第五暱稱-備註
        '''        
        df_survivor = await self.data_survivor(data_combined)
        df_hunter = await self.data_hunter(data_combined)
        df_remark = await self.data_remark(data_combined)
        
        #合併上面四個區塊的文字
        data_output = df_survivor+ "\n" + df_hunter+ "\n" +df_remark
        # 寫入到 txt 檔案
        with open("data_output.txt", "w", encoding = 'utf8') as f:
            f.write(data_output)
            
        #將txt上傳到dc上            
        with open('data_output.txt', 'rb') as fp:
            try:
                await ctx.send(file=discord.File(fp, 'data_output.txt'))
                await ctx.send(f"{form_date}表單已整理完成")
            except Exception as e:
                print("Error while uploading the file:", e)
       
        
async def setup(bot) :
    await bot.add_cog(test_fun(bot))