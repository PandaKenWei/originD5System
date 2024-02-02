from typing import Optional
import discord,asyncio

class Modal(discord.ui.Modal, title="讓我猜猜"):
    def __init__(self, title: str = "讓我猜猜", timeout: float = 60) -> None:
        super().__init__(title=title, timeout=timeout)
        self.choosed = asyncio.Event()

    name = discord.ui.TextInput(label="猜一個從一到一百內的數字")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            input_value = int(self.name.value)
            if not (1 <= input_value <= 100):
                raise ValueError("請輸入介於1和100之間的數字。")
        except (ValueError, TypeError):
            await interaction.response.send_message("請輸入有效的數字。", ephemeral=True)
            return
        else:
            await interaction.response.defer()
            self.choosed.set()

    async def wait_for_submit(self):
        await self.choosed.wait()
        return self.name.value

class View(discord.ui.View):
    def __init__(self, *, timeout: float = 60, target_user: discord.Member):
        super().__init__(timeout=timeout)
        self.click_value = None
        self.target_user = target_user
        self.click_event = asyncio.Event()

    @discord.ui.button(label="click", style=discord.ButtonStyle.green)
    async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.target_user != interaction.user:
            await interaction.response.send_message("現在是輪到你了是嗎", ephemeral=True)
            return
        modal = Modal()
        await interaction.response.send_modal(modal)
        self.click_value = await modal.wait_for_submit()
        self.click_event.set()

    async def wait_for_click(self):
        await self.click_event.wait()
        return self.click_value
    
class Check_start(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180, members, public):
        super().__init__(timeout=timeout)
        if not public:
            button = discord.ui.Button(label="不同意",style=discord.ButtonStyle.red)
            button.callback = self.disagree
            self.add_item(button)
        self.public = public
        self.members = members
        self.finished = asyncio.Event()
        self.agree_member = {}
        

    @discord.ui.button(label="同意",style=discord.ButtonStyle.green)
    async def agree(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user in self.members or self.public:
            await interaction.response.send_message("同意參加",ephemeral=True)
            self.agree_member[interaction.user] = True #用字典儲存以避免重複點擊
            if len(self.agree_member) == len(self.members) and not self.public:
                self.finished.set()

    async def disagree(self,interaction:discord.Interaction):
        self.agree_member[interaction.user] = False
        await interaction.response.send_message("不同意參加",ephemeral=True)
        if len(self.agree_member) == len(self.members):
            self.finished.set()

    async def wait_for_finish(self):
        await self.finished.wait()
        return

