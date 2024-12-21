import discord
from discord.ext import commands
import textwrap
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from IPython.display import display
from IPython.display import Markdown
from dotenv import load_dotenv
import os

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")

genai.configure(api_key=AI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command(help = "採用Gemini-1.5-flash模型，只要在指令後面加上你的問題，就可以問它任何問題", brief = "+ 你想問的問題，採用Gemini-1.5-flash模型，幫你解決問題")
    async def ai(self, ctx: commands.Context, question):
        response = model.generate_content(
            question,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
        await ctx.send(response.text)

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
