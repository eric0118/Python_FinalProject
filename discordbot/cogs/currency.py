import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup

# 爬蟲初始化
url = "https://www.esunbank.com/zh-tw/personal/deposit/rate/forex/foreign-exchange-rates"
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'}
response = requests.get(url, headers = headers)
soup = BeautifulSoup(response.text, "html.parser")
datatime = soup.find_all("p", id="dataTime") # 找出所有符合條件的元素，回傳列表
coins_list = {'美金': 'USD', '人民幣': 'CNY', '港幣': 'HKD', '日圓': 'JPY', '歐元': 'EUR', 
              '澳幣': 'AUD', '加拿大幣': 'CAD', '英鎊': 'GBP', '南非幣': 'ZAR', '紐西蘭幣': 'NZD',
              '瑞士法郎': 'CHF', '瑞典幣': 'SEK', '新加坡幣': 'SGD', '墨西哥披索': 'MXN', '泰銖': 'THB'}

# 定義名為 Main 的 Cog
class Currency(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command(help = "顯示所有可供查詢匯率的外幣，包含中文與英文", brief = "顯示所有可供查詢匯率的外幣，包含中文與英文")
    async def currency(self, ctx: commands.Context):
        await ctx.send("以下是所有可供查詢匯率的外幣") # Bot 傳送訊息
        for key, value in coins_list.items():
            await ctx.send(f"{key}: {value}")

    # 前綴指令
    @commands.command(help = "在指令後面加上指定貨幣(需用英文)後，查詢對應的玉山銀行外幣匯率的資訊", brief = "+ 指定貨幣(需用英文)，查詢對應的玉山銀行外幣匯率的資訊")
    async def rate(self, ctx: commands.Context, coin):
        await ctx.send(f"以下匯率資料日期為: {datatime[0].text}") # Bot 傳送訊息
        currency = soup.find_all("tr", class_="px-3 py-2 p-lg-0 " + coin + " currency")
        for a in currency:
            in_rate = a.find("div", class_="BBoardRate")
            if in_rate:
                in_rate = in_rate.text
            else:
                in_rate = "N/A"
            out_rate = a.find("div", class_="SBoardRate")
            if out_rate:
                out_rate = out_rate.text
            else:
                out_rate = "N/A"
            result = [key for key, value in coins_list.items() if value == coin]
            await ctx.send(f"{result[0]}的銀行買入匯率為: {in_rate}, 銀行賣出匯率為: {out_rate}")

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(Currency(bot))