from enum import Enum
import discord
from discord import ButtonStyle as BS
import ipdb
import asyncio
#await channel_send.send("請輸入你的求生歷史最高段位：\n1 - 一階；2 - 二階；3 - 三階；4 - 四階\n5 - 五階；6 - 六階；7 - 七階；巔7 - 巔峰七階")
buttonTest = {
    '你好': {
        'type': 'message',
        'message': '這是按鈕1',
        'style': BS.green,
    },
    '連結': {
        'type': 'link',
        'url': 'https://www.google.com',
        'style': BS.green,
    },
    '關閉': {
        'type': 'close_view',
        'style': BS.danger,
    },
    # button:{
    #         'custom_id':None, # str
    #         'disabled':False,
    #         'emoji':None, # [Union[PartialEmoji, Emoji, str]]
    #         'label':'按鈕1', # str
    #         'style':BS.green,
    #         'url':None, # str
    #         'row':1
    # },
}
buttonRank = {
    '一階': {
        'type': 'message',
        'message': '一階',
        'style': BS.grey,
    },
    '二階': {
        'type': 'message',
        'message': '二階',
        'style': BS.grey,
    },
    '三階': {
        'type': 'message',
        'message': '三階',
        'style': BS.grey,
    },
    '四階': {
        'type': 'message',
        'message': '四階',
        'style': BS.grey,
    },
    '五階': {
        'type': 'message',
        'message': '五階',
        'style': BS.grey,
    },
    '六階': {
        'type': 'message',
        'message': '六階',
        'style': BS.grey,
    },
    '七階': {
        'type': 'message',
        'message': '七階',
        'style': BS.grey,
    },
    '巔峰七階': {
        'type': 'message',
        'message': '巔峰七階',
        'style': BS.grey,
    },
}
buttonYN = {
    'Yes': {
        'type': 'message',
        'message': 'Y',
        'style': BS.green,
    },
    'No': {
        'type': 'message',
        'message': 'N',
        'style': BS.red,
    },
}
buttonYNC = {
    'Yes': {
        'type': 'message',
        'message': 'Y',
        'style': BS.green,
    },
    'No': {
        'type': 'message',
        'message': 'N',
        'style': BS.red,
    },
    '取消': {
        'type': 'message',
        'message': 'C',
        'style': BS.red,
    },
}
buttonOpen = {
    '開': {
        'type': 'message',
        'message': True,
        'style': BS.green,
    },
    '不開': {
        'type': 'message',
        'message': False,
        'style': BS.red,
    },
}
buttonSide = {
    '求生': {
        'type': 'message',
        'message': '求生',
        'style': BS.gray,
    },
    '監管': {
        'type': 'message',
        'message': '監管',
        'style': BS.gray,
    },
    '雙陣營': {
        'type': 'message',
        'message': '雙陣營',
        'style': BS.gray,
    },
}
buttonConfirm = {
    '提交': {
        'type': 'message',
        'message': 'Y',
        'style': BS.green,
    },
    '繼續舉報': {
        'type': 'message',
        'message': 'N',
        'style': BS.gray,
    },
    '取消': {
        'type': 'message',
        'message': 'C',
        'style': BS.red,
    },
}
buttonSeg = {
    '一區': {
        'type': 'message',
        'message': '一區',
        'style': BS.grey,
    },
    '二區': {
        'type': 'message',
        'message': '二區',
        'style': BS.grey,
    },
    '三區': {
        'type': 'message',
        'message': '三區',
        'style': BS.grey,
    },
    '四區': {
        'type': 'message',
        'message': '四區',
        'style': BS.grey,
    },
    '五區': {
        'type': 'message',
        'message': '五區',
        'style': BS.grey,
    },
}
buttonPSS = {
    '剪刀': {
        'type': 'message',
        'message': '剪刀',
        'style': BS.grey,
    },
    '石頭': {
        'type': 'message',
        'message': '石頭',
        'style': BS.grey,
    },
    '布': {
        'type': 'message',
        'message': '布',
        'style': BS.grey,
    },
}

## 定義多種類型按鈕 ###############################################
class MessageButton(discord.ui.Button):
    def __init__(self, label, style, message):
        super().__init__(label=label, style=style)
        self.message = message
        self.label = label

    async def callback(self, interaction: discord.Interaction):
        try:

            await interaction.response.send_message(pressedAndCloseMessage(False, self.label))
            await interaction.message.delete()
            self.view.clicked_button_value = self.message
            self.view.button_clicked.set()
            self.view.stop()
                    
        except Exception as e:
            print('An error occurred:', e)

class LinkButton(discord.ui.Button):
    def __init__(self, label, style, url):
        super().__init__(label=label, style=style, url=url)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            self.view.stop()
            await interaction.message.delete()
        except Exception as e:
            print('An error occurred:', e)

class CloseViewButton(discord.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(pressedAndCloseMessage(False, self.label))
            await interaction.message.delete()
            self.view.clicked_button_value = self.message
            self.view.button_clicked.set()
            self.view.stop()
                        
        except Exception as e:
            print('An error occurred:', e)

def pressedAndCloseMessage(isDefaultText, label):
    if isDefaultText:
        return  f'{label} was pressed. The view has been closed.'   
    else:
        return  f'{label}'
##################################################################

#### 定義盛裝「按鈕」的 View ###############
class ModelButtons(discord.ui.View):
    def __init__(self, Buttons):
        super().__init__()
        self.clicked_button_value = None
        self.button_clicked = asyncio.Event()
        
        for _ in range(1):
            for j in range(len(Buttons)):
                self.add_item(Buttons[j])
                
    async def wait_for_click(self):
        await self.button_clicked.wait()
        return self.clicked_button_value
            
##########################################

# 創建單個按鈕
def create_button(label, settings):
    type = settings['type']
    style = settings['style']
    if type == 'message':
        return MessageButton(label, style, settings['message'])
    elif type == 'link':
        return LinkButton(label, style, settings['url'])
    elif type == 'close_view':
        return CloseViewButton(label, style)