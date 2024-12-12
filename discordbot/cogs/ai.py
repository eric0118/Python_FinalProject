import discord
from discord.ext import commands
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

genai.configure(api_key="AIzaSyCb9z7BOQOIqxMj0zipyc3fUh8DBZGeo8g")
model = genai.GenerativeModel('gemini-1.5-flash')

class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command(help = "採用Gemini-1.5-flash模型，只要在指令後面加上你的問題，就可以問它任何問題", brief = "+ 你想問的問題，採用Gemini-1.5-flash模型，幫你解決問題")
    async def ai(self, ctx: commands.Context, question):
        response = model.generate_content(question)
        await ctx.send(response.text)

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
