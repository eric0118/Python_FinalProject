import discord
import datetime
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

# 定義 GraphQL API URL 和授權碼
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_KEY_API")
WEATHER_URL = os.getenv("WEATHER_UPL")

#初始化discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)



# 定義可用的縣市清單
AVAILABLE_COUNTIES = [
    "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣", 
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣",
    "雲林縣", "嘉義縣", "嘉義市", "屏東縣"
]

aquire_info = ["T","PoP","MaxT","MinT","UVI","WeatherDescription"]

def getWeatherData(city):
    headers = {
        "Authorization" : WEATHER_API_KEY,
        "Content-Type": "application/json"
    }
    
    query = """
    query forecast {
      forecast(LocationName: \"%s\") {
        Locations {
          LocationName,
          Geocode,
          Latitude,
          Longitude,
          Temperature {
            ElementName,
            Time {
              StartTime,
              EndTime,
              Temperature
            }
          },
          MaxComfortIndex {
            ElementName,
            Time {
              StartTime,
              EndTime,
              MaxComfortIndex,
              MaxComfortIndexDescription
            }
          },
          MinComfortIndex {
            ElementName,
            Time {
              StartTime,
              EndTime,
              MinComfortIndex,
              MinComfortIndexDescription
            }
          },
          ProbabilityOfPrecipitation {
            ElementName,
            Time {
              StartTime,
              EndTime,
              ProbabilityOfPrecipitation
            }
          },
          WindSpeed {
            ElementName,
            Time {
              StartTime,
              EndTime,
              WindSpeed,
              BeaufortScale
            }
          },
          UVIndex {
            ElementName,
            Time {
              StartTime,
              EndTime,
              UVIndex,
              UVExposureLevel
            }
          },
          Weather {
            ElementName,
            Time {
              StartTime,
              EndTime,
              Weather,
              WeatherCode
            }
          },
        }
      }
    }
    """ % city

    response = requests.post(WEATHER_URL, json={"query": query}, headers = headers)
    #print("API Response:", response.json())

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Response text: {response.text}")
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

def fix_isoformat_string(date_string):
    """修正不符合 ISO 8601 的時間字串"""
    if date_string.endswith(':0'):
        return date_string + '0'
    return date_string

def get_lastest_data(time_periods):
    """根據當前時間抓取最新的時間區段資料"""
    current_time = datetime.datetime.now()
    for period in time_periods:
        corrected_start_time = fix_isoformat_string(period['StartTime'])
        start_time = datetime.datetime.strptime(corrected_start_time, "%Y-%m-%d %H:%M:%S")
        if start_time > current_time:
            return period
    return time_periods[-1]  # 回傳最近的時間區段

def get_weather_info(city):
    try:
        Data = getWeatherData(city)
        location_data = Data['data']['forecast']['Locations'][0]

        latest_temp = get_lastest_data(location_data['Temperature']['Time'])
        latest_pop = get_lastest_data(location_data['ProbabilityOfPrecipitation']['Time'])
        latest_max_temp = get_lastest_data(location_data['MaxComfortIndex']['Time'])
        latest_min_temp = get_lastest_data(location_data['MinComfortIndex']['Time'])
        latest_uvi = get_lastest_data(location_data['UVIndex']['Time'])

        print(f"{location_data}\n\n{latest_temp}\n\n{latest_pop}\n\n{latest_max_temp}\n\n{latest_min_temp}\n\n{latest_uvi}")

        weather_info = (
            f"地點: {location_data['LocationName']}\n"
            f"時間: {latest_temp['StartTime']} ~ {latest_temp['EndTime']}\n"
            f"🌡️ {location_data['Temperature']['ElementName']}: {latest_temp['Temperature']}°C\n"
            f"🌂 {location_data['ProbabilityOfPrecipitation']['ElementName']}: {latest_pop['ProbabilityOfPrecipitation']}%\n"
            f"🔥 {location_data['MaxComfortIndex']['ElementName']}: {latest_max_temp['MaxComfortIndex']}°C ({latest_max_temp['MaxComfortIndexDescription']})\n"
            f"❄️ {location_data['MinComfortIndex']['ElementName']}: {latest_min_temp['MinComfortIndex']}°C ({latest_min_temp['MinComfortIndexDescription']})\n"
            f"☀️ {location_data['UVIndex']['ElementName']}: {latest_uvi['UVIndex']} ({latest_uvi['UVExposureLevel']})"
        )

        return weather_info
    except KeyError as e:
        error_details = f"KeyError: {e}\n" + traceback.format_exc()
        print(error_details)
        return f"無法獲取天氣資訊，請稍後再試。缺少的欄位: {e}"
    except Exception as e:
        error_details = f"Exception: {e}\n" + traceback.format_exc()
        print(error_details)
        return f"無法獲取天氣資訊，請稍後再試。錯誤訊息: {e}"

#定義指令：顯示可查詢縣市
@bot.tree.command(name="counties", description="列出所有可查詢的縣市")
async def list_counties(interaction: discord.Interaction):
    counties_message = "以下是可以查詢天氣的縣市：\n" + "\n".join(AVAILABLE_COUNTIES)
    await interaction.response.send_message(counties_message)

# 定義指令：查詢天氣
@bot.tree.command(name="weather", description="查詢指定縣市的天氣")
@app_commands.describe(city="輸入縣市名稱")
async def weather(interaction: discord.Interaction, city: str = None):
    if city is None:
        await interaction.response.send_message(
            "請輸入縣市名稱！您可以使用 `/counties` 查看所有可用的縣市名稱。"
        )
    elif city not in AVAILABLE_COUNTIES:
        counties_message = "您輸入的縣市無效。以下是可以查詢天氣的縣市：\n" + "\n".join(AVAILABLE_COUNTIES)
        await interaction.response.send_message(counties_message)
    else:
      weather_info = get_weather_info(city)
      await interaction.response.send_message(weather_info)

@bot.event
async def on_ready():
    # 設定活動狀態
    activity = discord.Game("輸入 /counties 查看可查詢的縣市")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"{bot.user.name} 已成功上線！")
    # 同步應用指令到 Discord
    await bot.tree.sync()

# 啟動 Bot
bot.run(DISCORD_TOKEN)