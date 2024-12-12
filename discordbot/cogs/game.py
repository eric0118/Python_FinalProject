import discord
from discord.ext import commands
import random

class Game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games = {}  # 存儲每個頻道的遊戲狀態

    # 前綴指令
    @commands.command(help="玩猜數字遊戲", brief="玩猜數字遊戲")
    async def game(self, ctx: commands.Context):
        # 生成 1000 到 9999 的隨機數，且不重複
        while True:
            random_number = random.randint(1000, 9999)
            random_number = str(random_number)
            if len(random_number) == len(set(random_number)):
                break

        # 儲存遊戲狀態
        self.active_games[ctx.channel.id] = random_number

        # 遊戲開始提示
        await ctx.send("讓我們開始玩猜數字遊戲吧！")
        await ctx.send("規則：我會想一個四位數字，且不包含重複數字。")
        await ctx.send("你需要根據提示的XAYB來猜測數字，其中X表示位置正確的數，Y表示數字正確但位置錯誤的數。")
        await ctx.send("隨時輸入數字來進行猜測，若要結束遊戲，輸入 `quit` 即可。")

    # 監聽訊息事件
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 忽略 Bot 自己的訊息
        if message.author.bot:
            return

        # 檢查是否有正在進行的遊戲
        channel_id = message.channel.id
        if channel_id not in self.active_games:
            return

        # 取得謎底數字
        random_number = self.active_games[channel_id]

        # 處理玩家的輸入
        guess = message.content.strip()

        # 玩家退出遊戲
        if guess.lower() == "quit":
            await message.channel.send(f"遊戲結束！謎底是：{random_number}")
            del self.active_games[channel_id]
            return

        # 驗證輸入是否為四位數字
        if ((len(guess) != 4) or (not guess.isdigit())) and (guess!="$game"):
            await message.channel.send("請輸入四位數字！")
            return
        
        if (len(guess) != len(set(guess))) and (guess!="$game"):
            await message.channel.send("謎底不會有重複數字喔!請輸入沒有重複數字的四位數")
            return


        # 計算XAYB
        A, B = 0, 0
        for i in range(4):
            if guess[i] == random_number[i]:
                A += 1
            elif guess[i] in random_number:
                B += 1

        # 回覆結果
        if guess!="$game":
            await message.channel.send(f"{A}A{B}B")

        # 玩家猜中
        if A == 4:
            await message.channel.send("恭喜你猜中了！遊戲結束！")
            del self.active_games[channel_id]

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))
