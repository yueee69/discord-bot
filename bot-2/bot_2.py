import json
import discord
from discord.ext import commands,tasks
from discord import app_commands
from datetime import datetime, timedelta
import random
from discord.ui import Button, View
import re
import asyncio
import pytz
import math
import yt_dlp as youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import subprocess
import os 
import fitz
import requests

save = ''
queue = {}

YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/')
SPOTIFY_TRACK_REGEX = re.compile(r'https://open\.spotify\.com/track/(\w+)')
SPOTIFY_PLAYLIST_REGEX = re.compile(r'https://open\.spotify\.com/playlist/(\w+)')
MBPLAYER_REGEX = re.compile(r'(https?://)?(www\.)?mbplayer\.com/list/\d+')

youtube_dl.utils.bug_reports_message = lambda: ''
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='1e5248d8ffbf4327a2142198e1b04418', client_secret='fd73b546815442d382b9ab1f02198f79'))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)

number_word={
    1:"𝟙",
    2:"𝟚",
    3:"𝟛"
    }

shop_item = {
    "3陽壽":[10500,35,42],#原價 優惠max 出現機率
    "5陽壽":[17500,35,18],
    "7陽壽":[24500,40,12],
    "10陽壽":[35000,50,5],
    "5萬眾神幣":[5000,5,10],
    "10萬眾神幣":[10000,10,5],
    "50萬眾神幣":[45000,100,5],
    "100萬眾神幣":[60000,100,1],
    "舞者之書":[40000,50,1],
    "魔法戰士之書":[70000,50,1],
    }

prime={
   579618807237312512 #我
}

Prize_pools = {
    "普通": {
            "空氣": 35,
            "鮭魚幣+10000": 1,
            "鮭魚幣+1000": 10,
            "鮭魚幣+500": 20,
            "鮭魚幣+2000": 5,
            "鮭魚幣+5000": 4,
            "5萬眾神幣": 20,
            "10萬眾神幣":5
            },

    "一般": {
            "100萬眾神幣": 10,
            "舞者之書": 15,
            "魔法戰士之書": 45,
            "空氣": 20,
            "50萬眾神幣":10,
            "75萬眾神幣":10
            },

    "大獎": {
            "500萬眾神幣:star:": 15,
            "免費附魔一次:star:": 35,
            "暗黑之書/徒手書/詩人書/忍書 四選一:star:": 35,
            "紅色王石任選:star:":2,
            "綠色王石任選:star:":5,
            "王石任選:star:":1,
            "紫色王石任選:star:":2,
            "黃色王石任選:star:":5
            }
}

percent = {"普通": 92, "一般": 8, "大獎": 0}

item_pools = {
    "鮭魚幣+1750":35,
    "鮭魚幣+2000":25,
    "鮭魚幣+2500":15,
    "鮭魚幣+3000":8,
    "鮭魚幣+5000":3,
    "迴轉卡":2,
    "增加身分組卡":4,
    "指定身分組卡":4,
    "指定暱稱卡":4
}

item_pools_trans ={
    "迴轉卡":"trans",
    "增加身分組卡":"add_role",
    "指定身分組卡":"role",
    "指定暱稱卡":"nick"    
    }

do_not_role={
    "頭等鮭魚腹",
    "次等鮭魚腹",
    "鮭魚幹部",
    "食物鏈頂端",
    "花椰菜",
    "狗子",
    "鮭魚卵",
    "鮭魚們",
    "會外鮭魚",
    "特戰鮭",
    "會內鮭魚",
    "鮭姬",
    "鮭魚乾爹"
}

sell = {
  "trans":2000,
  "add_role":750,
  "role":1000,
  "nick":1000
  }

def randcolor():
    color_list = [
        discord.Color.blue(),
        discord.Color.blurple(),
        discord.Color.gold(),
        discord.Color.greyple(),
        discord.Color.magenta(),
        discord.Color.og_blurple(),
        discord.Color.orange(),
        discord.Color.purple(),
        discord.Color.teal(),
        discord.Color.darker_gray(),
        discord.Color.darker_grey(),
        discord.Color.dark_blue(),
        discord.Color.dark_embed(),
        discord.Color.dark_gold(),
        discord.Color.dark_grey(),
        discord.Color.dark_magenta(),
        discord.Color.dark_orange(),
        discord.Color.dark_purple(),
        discord.Color.dark_theme(),
        discord.Color.yellow(),
        discord.Color.lighter_gray(),
        discord.Color.lighter_grey(),
        discord.Color.light_embed(),
        discord.Color.light_gray(),
        discord.Color.light_grey()
    ]
    color = color_list[random.randint(0,len(color_list)-1)]
    return color

taipei_timezone = pytz.timezone('Asia/Taipei')
taipei_time = datetime.now(taipei_timezone)

def time():
    taipei_time = datetime.now(taipei_timezone)
    hour = taipei_time.hour
    minute = "0" + str(taipei_time.minute) if len(str(taipei_time.minute)) == 1 else taipei_time.minute
    period = "上午" if hour < 12 else "下午"
    return hour,minute,period

async def check_voice_channels():
    time_clock = 0
    while True:
        time_clock += 1
        with open('user.json', 'r') as user_file, open('date.json', 'r') as date_file, open('item.json', 'r') as item_file, open('shop.json', 'r', encoding='utf-8') as file, open('product.json', 'r', encoding='utf-8') as file1, open('afk.json', 'r', encoding='utf-8-sig') as file2, open('rpg_data.json', 'r', encoding='utf-8') as file3, open('recipe.json', 'r', encoding='utf-8') as file4, open('job.json', 'r', encoding='utf-8') as file5, open('sign_in.json', 'r') as file6,open('xtal_lottery.json', 'r',encoding='utf-8-sig') as file7:
            data = json.load(user_file)
            Data = json.load(date_file)
            item = json.load(item_file)
            shop = json.load(file)
            goods = json.load(file1)
            afk = json.load(file2)
            rpg_data = json.load(file3)
            recipe = json.load(file4)
            job = json.load(file5)
            sign = json.load(file6)
            xtal = json.load(file7)

        if job:
            for user_id,jober in job.items():
                if jober["time"] > 0:
                    if jober["time"] % 20 == 0:
                        if jober["job"] == "礦工":
                            if rpg_data[user_id]["energy"]-4 >= -100:
                                rpg_data[user_id]["energy"] -= 4
                            pt = ["金屬","獸品"]
                            per = 1
                            if rpg_data[user_id]["energy"] > 0:
                                per = 1+rpg_data[user_id]["energy"]/200
                            elif rpg_data[user_id]["energy"] < -30:
                                per = (100+rpg_data[user_id]["energy"])/100
                            pt_data = {
                                "name":random.choice(pt),
                                "kind":"pt",
                                "per":int(random.randint(10,random.choice(recipe["礦工"]["pts"]))*per),
                                "des":"",
                                }
                            check = False
                            for r in job[str(user_id)]["gain"]:
                                if r["name"] == pt_data["name"]:
                                    r["per"] += pt_data["per"]
                                    check = True
                                    break
                            if not check:
                                jober["gain"].append(pt_data)

                            if rpg_data[user_id]["energy"] > 0:
                                if random.randint(1,100) <= jober["fortune"]*10:
                                    mana_or_coin = random.randint(1,100)
                                    if mana_or_coin <= 50:
                                        coin_data = {
                                        "name":"金幣",
                                        "kind":"coin",
                                        "per":int(random.randint(10,random.choice(recipe["礦工"]["coin"]))*per),
                                        "des":"",
                                        }
                                        check = False
                                        for r in job[str(user_id)]["gain"]:
                                            if r["name"] == coin_data["name"]:
                                                r["per"] += coin_data["per"]
                                                check = True
                                                break
                                        if not check:
                                            jober["gain"].append(coin_data)
                                    else:
                                        mana_data = {
                                            "name":"魔素",
                                            "kind":"pt",
                                            "per":random.randint(10,random.choice(recipe["礦工"]["魔素"])),
                                            "des":"",
                                            }
                                        check = False
                                        for r in job[str(user_id)]["gain"]:
                                            if r["name"] == mana_data["name"]:
                                                r["per"] += mana_data["per"]
                                                check = True
                                                break
                                        if not check:
                                            jober["gain"].append(mana_data)

                                if random.randint(1,100) <= max(0,int(jober["fortune"]/2.5)-1):
                                    xtal1 = None
                                    xtal2 = None
                                    xtal_lottery = random.randint(0,100)
                                    if xtal_lottery == 0:
                                        xtal1 = {
                                            "name":"-",
                                            "kind":"xtal",
                                            "per":1,
                                            "des":None,
                                            "effect":None
                                            }
                                        xtal2 = {
                                            "name":"-",
                                            "kind":"xtal",
                                            "per":1,
                                            "des":None,
                                            "effect":None
                                            }
                                    elif xtal_lottery <= 10:
                                        xtal1 = {
                                            "name":"-",
                                            "kind":"xtal",
                                            "per":1,
                                            "des":None,
                                            "effect":None
                                            }
                                    s_1 = 0
                                    for inde in range(10):
                                        s_1 += random.uniform(0,0.01)
                                    equip = random.choice(recipe["礦工"]["equip"])
                                    equip_data = {
                                        "name": equip["name"],
                                        "per": 1,
                                        "des": equip["des"],
                                        "kind": "equip",
                                        "slot": equip["slot"],
                                        "xtal1": xtal1,
                                        "xtal2": xtal2,
                                        "stated": 0,
                                        "category": equip["category"],
                                        "refine": 0,
                                        "refine_pts": 0,
                                        "def":int(equip["f_def"]*(1+s_1)+int(s_1)),
                                        "f_def": equip["f_def"],
                                        "effect": equip["effect"]
                                    }
                                    jober["gain"].append(equip_data)

                                if random.randint(1,100) <= min(jober["luk"]/50,5):
                                    jober["gain"].append(random.choice(recipe["礦工"]["mana_reward"]))

                        if jober["job"] == "喜歡伐木的獵人":
                            if rpg_data[user_id]["energy"]-4 >= -100:
                                rpg_data[user_id]["energy"] -= 4
                            pt = ["藥品","木材","布料"]
                            per = 1
                            if rpg_data[user_id]["energy"] > 0:
                                per = 1+rpg_data[user_id]["energy"]/200
                            elif rpg_data[user_id]["energy"] < -30:
                                per = (100+rpg_data[user_id]["energy"])/100
                            pt_data = {
                                "name":random.choice(pt),
                                "kind":"pt",
                                "per":int(random.randint(10,random.choice(recipe["獵人"]["pts"]))*per),
                                "des":"",
                                }
                            check = False
                            for r in job[str(user_id)]["gain"]:
                                if r["name"] == pt_data["name"]:
                                    r["per"] += pt_data["per"]
                                    check = True
                                    break
                            if not check:
                                jober["gain"].append(pt_data)

                            if random.randint(1,100) <= jober["fortune"]*10:
                                    coin_data = {
                                    "name":"金幣",
                                    "kind":"coin",
                                    "per":int(random.randint(10,random.choice(recipe["獵人"]["coin"]))*per),
                                    "des":"",
                                    }
                                    check = False
                                    for r in job[str(user_id)]["gain"]:
                                        if r["name"] == coin_data["name"]:
                                            r["per"] += coin_data["per"]
                                            check = True
                                            break
                                    if not check:
                                        jober["gain"].append(coin_data)

                            if random.randint(1,100) <= 16:#15%
                                meat = random.choice(recipe["獵人"]["meat"])
                                check = False
                                for i in jober["gain"]:
                                    if i["name"] == meat["name"]:
                                        i["per"] += 1
                                        check = True
                                        break
                                if not check:
                                    jober["gain"].append(meat)
                            
                            if rpg_data[user_id]["energy"] > 0:
                                m = 0
                                if jober["luk"] > 0:
                                    m = math.log10(jober["luk"])
                                if random.randint(1,100) <= max(0,m):
                                    xtal1 = None
                                    xtal2 = None
                                    xtal_lottery = random.randint(0,100)
                                    if xtal_lottery == 0:
                                        xtal1 = {
                                            "name":"-",
                                            "kind":"xtal",
                                            "per":1,
                                            "des":None,
                                            "effect":None
                                            }
                                        xtal2 = {
                                            "name":"-",
                                            "kind":"xtal",
                                            "per":1,
                                            "des":None,
                                            "effect":None
                                            }
                                    elif xtal_lottery <= 10:
                                        xtal1 = {
                                            "name":"-",
                                            "kind":"xtal",
                                            "per":1,
                                            "des":None,
                                            "effect":None
                                            }
                                    s_1 = 0
                                    for inde in range(10):
                                        s_1 += random.uniform(0,0.01)
                                    equip = random.choice(recipe["獵人"]["equip"])
                                    equip_data = {
                                        "name": equip["name"],
                                        "per": 1,
                                        "des": equip["des"],
                                        "kind": "equip",
                                        "slot": equip["slot"],
                                        "xtal1": xtal1,
                                        "xtal2": xtal2,
                                        "stated": 0,
                                        "category": equip["category"],
                                        "refine": 0,
                                        "refine_pts": 0,
                                        "def":int(equip["f_def"]*(1+s_1)+int(s_1)),
                                        "f_def": equip["f_def"],
                                        "effect": equip["effect"]
                                    }
                                    jober["gain"].append(equip_data)

                        if jober["job"] == "other":
                            if rpg_data[user_id]["energy"]-5 >= -100:
                                rpg_data[user_id]["energy"] -= 5
                            pt = ["藥品","木材","布料","金屬","獸品"]
                            per = 1
                            if rpg_data[user_id]["energy"] > 0:
                                per = 1+rpg_data[user_id]["energy"]/200
                            elif rpg_data[user_id]["energy"] < -30:
                                per = (100+rpg_data[user_id]["energy"])/100
                            pt_data = {
                                "name":random.choice(pt),
                                "kind":"pt",
                                "per":int(random.randint(10,random.choice(recipe["other"]["pts"]))*per),
                                "des":"",
                                }
                            check = False
                            for r in job[str(user_id)]["gain"]:
                                if r["name"] == pt_data["name"]:
                                    r["per"] += pt_data["per"]
                                    check = True
                                    break
                            if not check:
                                jober["gain"].append(pt_data)

                            if random.randint(1,100) <= jober["fortune"]*10:
                                if job[str(user_id)]["sex"] == "扶他":
                                    i = random.randint(10,random.choice(recipe["other"]["futa_coin"]))
                                else:
                                    i = random.randint(10,random.choice(recipe["other"]["coin"]))

                                coin_data = {
                                "name":"金幣",
                                "kind":"coin",
                                "per":int(i*per),
                                "des":"",
                                }
                                check = False
                                for r in job[str(user_id)]["gain"]:
                                    if r["name"] == coin_data["name"]:
                                        r["per"] += coin_data["per"]
                                        check = True
                                        break
                                if not check:
                                    jober["gain"].append(coin_data)

                            if jober["work_time"] >= 300:
                                if random.randint(1,100) <= int(jober["work_time"]/60):
                                    for d in jober["gain"]:
                                        if d["kind"] == "pt":
                                            d["per"] = int(d["per"]*0.95)
                                    jober["overwork"] += 1
                            jober["work_time"] += 20

                    jober["time"] -= 1

        if time_clock >= 60:
            time_clock = 0
            for user in rpg_data:
                recover = 20
                if user not in job:
                    if rpg_data[user]["merry"] is not None:
                        recover = 30
                    rpg_data[user]["energy"] = min(100, rpg_data[user]["energy"] + recover)
                elif user in job:
                    if job[user]["time"] == 0:
                        if rpg_data[user]["merry"] is not None:
                            recover = 30
                        recover = int(recover / 2)
                        rpg_data[user]["energy"] = min(100, rpg_data[user]["energy"] + recover)
                            
        if xtal[1]["date"] == 7:
            if xtal[1]["item"] is not None:
                xtal[0][xtal[1]["item"]] /= 5
				
            buffed = []
            for i,j in xtal[0].items():
                if j == 0.05424455617289966:
                    buffed.append(i)
            item_z = random.choice(buffed)
            xtal[0][item_z] *= 5
            xtal[1]["item"] = item_z 
            xtal[1]["date"] = 0 
            
        if datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei')).day != Data[0]["today"]:
            xtal[1]["date"] += 1
            for user in sign:
                if sign[user]["state"] == True:
                    sign[user]["continue"] = True
                    sign[user]["state"] = False
                else:
                    sign[user]["state"] = False
                    sign[user]["day"] = 0

            for entry in data:
                entry["voice"] = 0
                entry["stream"] = 0
                entry["chat"] = 0
                entry["buy"] = 0

            weighted_choices = [(item, item_info[2]) for item, item_info in shop_item.items()]
            for i in range(1, 4):
                selected_item = random.choices(weighted_choices, weights=[w for _, w in weighted_choices])[0][0]
                weighted_choices = [(item, weight) for item, weight in weighted_choices if item != selected_item]
                shop[f"slot{i}"]["item"] = selected_item
                shop[f"slot{i}"]["price"] = shop_item.get(selected_item)[0] - random.randint(0, 100) * shop_item.get(selected_item)[1]

            for user_id, user_data in item.items():
                item[str(user_id)][0]["lottery"] = False

            for user_id, products in goods.items():
                to_remove = []
                for product in products:
                    product["date"] += 1
                    if product["date"] == 10:
                        to_remove.append(product)
                for product in to_remove:
                    products.remove(product)

            Data[0]["today"] = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei')).day

        for guild in bot.guilds:
            for channel in guild.voice_channels:
                members_in_channel = [member for member in channel.members if not member.bot]
                if len(members_in_channel) > 1:
                    for member in members_in_channel:
                        for user_id, dat in afk.items():
                            if user_id == str(member.id):
                                dat["afk_time"] = 0

                        if any(entry["user_id"] == str(member.id) for entry in data):
                            for entry in data:
                                if entry["user_id"] == str(member.id):
                                    if entry["stream"] < 5000 and (member.voice.self_stream or member.voice.self_video) and member.voice.self_deaf == False:
                                        entry["gain"] += 50
                                        entry["stream"] += 50
                                        entry["coin"] += 50
                                        if entry["voice"] < 3000:
                                            entry["gain"] += 30
                                            entry["voice"] += 30
                                            entry["coin"] += 30
                                        entry["lvl"] = int(entry["gain"] / 1500)
                                    elif entry["voice"] < 3000 and member.voice.self_deaf == False:
                                        entry["gain"] += 30
                                        entry["voice"] += 30
                                        entry["coin"] += 30
                                        entry["lvl"] = int(entry["gain"] / 1500)

            for user_id, d in afk.items():
                d["afk_time"] += 1

            with open('user.json', 'w') as user_file, open('date.json', 'w') as date_file, open('item.json', 'w') as item_file, open('shop.json', 'w', encoding='utf-8') as file, open('product.json', 'w', encoding='utf-8') as file1, open('afk.json', 'w', encoding='utf-8') as file2, open('rpg_data.json', 'w', encoding='utf-8') as file3, open('job.json', 'w', encoding='utf-8') as file5, open('sign_in.json', 'w') as file6, open('xtal_lottery.json','w',encoding='utf-8-sig') as file7:
                json.dump(xtal, file7, indent=4, ensure_ascii=False)
                json.dump(data, user_file, indent=4)
                json.dump(Data, date_file, indent=4)
                json.dump(item, item_file, indent=4)
                json.dump(shop, file, indent=4, ensure_ascii=False)
                json.dump(goods, file1, indent=4, ensure_ascii=False)
                json.dump(afk, file2, indent=4, ensure_ascii=False)
                json.dump(rpg_data, file3, indent=4, ensure_ascii=False)
                json.dump(job, file5, indent=4, ensure_ascii=False)
                json.dump(sign, file6, indent=4)


        await asyncio.sleep(60)

@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"載入 {len(slash)} 個 slash")
    activity = discord.Activity(
        type=discord.ActivityType.streaming,
        url = 'https://www.youtube.com/watch?v=FoO7Pmx0bE4',
        name="✨ 漂漂釀釀",
        state="ヾ(⌒(ﾉｼ'ω')ﾉｼ",
    )
    
    await bot.change_presence(
        status=discord.Status.idle,
        activity=activity
    )
    await check_voice_channels()
    

@bot.tree.command(name='抗性', description='計算物理或魔法抗性')
@app_commands.describe(atk="面板物理/魔法攻擊力",playerlvl="角色等級",monsterlvl="怪物等級",rate="技能倍率(血淚1.9)",dmg="傷害",dtelight="是否對屬")
@app_commands.choices(dtelight=[
        app_commands.Choice(name="是", value="T"),
        app_commands.Choice(name="否", value="F"),
        ])
async def phyresis(interaction: discord.Interaction, atk: int, playerlvl: int, monsterlvl: int, rate: float, dmg: int, dtelight: app_commands.Choice[str] ):
  if dmg==0 or rate==0:
    embed = discord.Embed(title="錯誤！ 常數或傷害不能為0")
    embed.color=embed.color = discord.Colour.red()
    embed.add_field(name="不會測不要測 耖",value="")
    await interaction.response.send_message(embed=embed)
  elif dtelight.value == "T":
   result = int(100-(dmg/1.25/(atk + playerlvl - monsterlvl) * rate)*100)
  else:
   result = int(100-(dmg/(atk + playerlvl - monsterlvl) * rate)*100)
  if result>=99:result=100
  embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"**目標物理/魔法抗性: {result}**")
  embed.color = discord.Colour.blurple()
  embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/831036102243647519.gif")
  embed.add_field(name="物理攻擊面板:", value=atk)
  embed.add_field(name="角色等級:", value=playerlvl,inline=False)
  embed.add_field(name="怪物等級:", value=monsterlvl,inline=False)
  embed.add_field(name="技能倍率:", value=rate,inline=False)
  embed.add_field(name="對屬:", value=dtelight.name,inline=False)
  embed.add_field(name="最終傷害:", value=dmg,inline=False)
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name='物理防禦',description='計算物理防禦(魔防要用燃燒/毒測)')
@app_commands.describe(atk="面板攻擊力",playerlvl="角色等級",monsterlvl="怪物等級",resistance="物理抗性",pierce="物理貫穿",rate="技能倍率(血淚1.9)",dmg="傷害",dtelight="是否對屬")
@app_commands.choices(dtelight=[
  app_commands.Choice(name="是", value="T"),
  app_commands.Choice(name="否", value="F"),
  ])
async def phydef(interaction: discord.Interaction, atk: int, playerlvl: int, monsterlvl: int,resistance:int,pierce:int, rate: float, dmg: int, dtelight: app_commands.Choice[str]):
  if dmg==0 or rate==0:
    embed = discord.Embed(title="錯誤！ 常數或傷害不能為0")
    embed.color=embed.color = discord.Colour.red()
    embed.add_field(name="不會測不要測 耖",value="")
    await interaction.response.send_message(embed=embed)
  else:
    if dtelight.value == "T":
     defense=int(((atk+playerlvl-monsterlvl)*((100-resistance)/100)*rate*1.25-dmg)/rate/((100-pierce)/100))
    else:
      defense=int(((atk+playerlvl-monsterlvl)*((100-resistance)/100)*rate-dmg)/rate/((100-pierce)/100))
    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"**目標物理防禦: {defense}**")
    embed.color = discord.Colour.blurple()
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/831036102243647519.gif")
    embed.add_field(name="物理攻擊面板:", value=atk)
    embed.add_field(name="角色等級:", value=playerlvl,inline=False)
    embed.add_field(name="怪物等級:", value=monsterlvl,inline=False)
    embed.add_field(name="物理抗性:", value=resistance,inline=False)
    embed.add_field(name="物理貫穿:", value=pierce,inline=False)
    embed.add_field(name="技能倍率:", value=rate,inline=False)
    embed.add_field(name="對屬:", value=dtelight.name,inline=False)
    embed.add_field(name="最終傷害:", value=dmg,inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='兌換陽壽', description='3500鮭魚幣=1陽壽')
@app_commands.describe(陽壽="要兌換多少陽壽")
async def exchange(interaction: discord.Interaction, 陽壽:int):
 with open('user.json', 'r') as file:
  data = json.load(file)
 if any(entry["user_id"] == str(interaction.user.id) for entry in data):
  for entry in data:
   if entry["user_id"] == str(interaction.user.id):
    check = interaction.user.id
    if entry["coin"] < 陽壽*3500:
      embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
      embed.add_field(name=f'• 鮭魚幣不足(缺少{ 陽壽*3500-entry["coin"] }鮭魚幣)', value='',inline=False)
      embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
      embed.color = discord.Colour.red()
      await interaction.response.send_message(embed=embed,ephemeral=True)
      break
    elif 陽壽<1:
      embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
      embed.add_field(name="• 兌換的陽壽不能小於1", value='',inline=False)
      embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
      embed.color = discord.Colour.red()
      await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
      button=Button(label="確認",custom_id="yes",style = discord.ButtonStyle.green)
      button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
      async def button_callback(interaction):
       custom = interaction.data['custom_id']
       if custom == "yes" and interaction.user.id == check:
        if any(entry["user_id"] == str(interaction.user.id) for entry in data):
          for entry in data:
           if entry["user_id"] == str(interaction.user.id):
            await interaction.message.delete()
            entry["coin"] -= 陽壽*3500
            entry["fortune"] += 陽壽
            embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="兌換成功！")
            embed.add_field(name=f"{interaction.user.name}", value=f' 使用 {陽壽*3500} 鮭魚幣兌換了 {陽壽} 陽壽',inline=True)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/957718579887894558.webp")
            embed.color = discord.Colour.green()
            await interaction.channel.send(embed=embed)
            with open('user.json', 'w') as file:
                json.dump(data, file, indent=4)

       elif custom == "no" and interaction.user.id == check:
        await interaction.message.delete()

      button.callback = button_callback
      button2.callback = button_callback
      view=View()
      view.add_item(button)
      view.add_item(button2)
      embed = discord.Embed(title="付款確認", description=f"是否要消耗 {陽壽*3500} 鮭魚幣兌換 {陽壽} 陽壽?")
      embed.color = discord.Colour.dark_blue()
      await interaction.response.send_message(embed=embed , view=view)
 else:
      embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
      embed.add_field(name="• 您尚未登記", value='',inline=False)
      embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
      embed.color = discord.Colour.red()
      await interaction.response.send_message(embed=embed)

@bot.tree.command(name='用戶資訊',description='確認你的資訊')
async def coint(interaction: discord.Interaction):
 with open('user.json', 'r') as file , open('history.json', 'r', encoding='utf-8') as file1:
    data = json.load(file)
    history = json.load(file1)
 if any(entry["user_id"] == str(interaction.user.id) for entry in data):
   for entry in data:
     if entry["user_id"] == str(interaction.user.id):
        embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}你的資訊如下:")
        embed.add_field(name="鮭魚幣", value=entry["coin"],inline=False)
        embed.add_field(name="陽壽(?)", value=entry["fortune"],inline=False)
        embed.add_field(name="總共取得的鮭魚幣", value=entry["gain"],inline=False)
        embed.add_field(name="存活年數", value=entry["lvl"],inline=False)
        embed.add_field(name="今日講話取得的鮭魚幣\n", value=entry["chat"],inline=False)
        embed.add_field(name="今日通話取得的鮭魚幣\n", value=f'{entry["voice"]} / 3000\n',inline=False)
        embed.add_field(name="今日直播取得的鮭魚幣\n", value=f'{entry["stream"]} / 5000',inline=False)
        embed.add_field(name="今日購買的道具數量\n", value=f'{entry["buy"]} / 1',inline=False)
        embed.color = discord.Colour.gold()
        embed.set_thumbnail(url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
 else:
    new_data = {
       "user_id": str(interaction.user.id),
       "coin": 0,
       "fortune":0,
       "voice":0,
       "stream":0,
       "gain":0,
       "lvl":0,
       "chat":0,
       "buy":0
     }
    data.append(new_data)
    if str(interaction.user.id) not in history:
        history[str(interaction.user.id)] = []
        for i in range(1, 101):
            history[str(interaction.user.id)].append({f"prize{i}": None})
    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}已完成登記！")
    await interaction.response.send_message(embed=embed)
    with open('user.json', 'w') as file , open('history.json', 'w') as file1:
     json.dump(data, file, indent=4)
     json.dump(history, file1, indent=4)

@bot.tree.command(name='增加金幣', description='增加鮭魚幣數量(沒權限沒有用uwu)')
@app_commands.describe(user="用戶名",coin=("要設定的鮭魚幣(可正可負)"))
async def sett(interaction: discord.Interaction,user:str,coin:int):
 with open('user.json', 'r') as file:
    data = json.load(file)
 tf=False
 User = discord.utils.get(bot.users, name=user)
 if(User!=None):
     User = str(discord.utils.get(bot.users, name=user).id)
     if any(entry["user_id"] == User for entry in data):
       for entry in data:
         if entry["user_id"] == User:
           for user_id in prime:
             if interaction.user.id == user_id:
              entry["coin"] += int(coin*1.75)
              tf=True
              embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{bot.get_user(int(User)).name}的資訊如下:")
              embed.add_field(name="鮭魚幣", value=entry["coin"],inline=False)
              embed.add_field(name="陽壽(?)", value=entry["fortune"],inline=False)
              embed.add_field(name="總共取得的鮭魚幣", value=entry["gain"],inline=False)
              embed.add_field(name="存活年數", value=entry["lvl"],inline=False)
              embed.add_field(name="今日講話取得的鮭魚幣\n", value=entry["chat"],inline=False)
              embed.add_field(name="今日通話取得的鮭魚幣 ", value=f'{entry["voice"]} / 3000',inline=False)
              embed.add_field(name="今日直播取得的鮭魚幣 ", value=f'{entry["stream"]} / 5000',inline=False)
              embed.color = discord.Colour.gold()
              embed.set_thumbnail(url=bot.get_user(int(User)).avatar.url)
              await interaction.response.send_message(embed=embed)
     if not tf:
        embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
        embed.add_field(name="• 您沒有足夠權限", value='',inline=False)
        embed.add_field(name="• 對象尚未登記", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.color = discord.Colour.red()
        await interaction.response.send_message(embed=embed,ephemeral=True)     
 else:
    embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
    embed.add_field(name="• 輸入的玩家id有誤", value='',inline=False)
    embed.color = discord.Colour.red()
    await interaction.response.send_message(embed=embed,ephemeral=True)
 with open('user.json', 'w') as file:
    json.dump(data, file, indent=4)

class CustomModal(discord.ui.Modal):
    def __init__(self, title, fields, on_submit_callback):
        super().__init__(title=title)
        self.on_submit_callback = on_submit_callback
        for field_name, field_params in fields.items():
            text_input = discord.ui.TextInput(
                label=field_params.get("label", ""),
                placeholder=field_params.get("placeholder", ""),
                required=field_params.get("required", True),
                max_length=field_params.get("max_length"),
                min_length=field_params.get("min_length"),
                default=field_params.get("default"),
                style=field_params.get("style", discord.TextStyle.short)
            )
            self.add_item(text_input)
            setattr(self, field_name, text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.on_submit_callback(interaction, self)

def create_modal(title, fields, on_submit_callback):
    return CustomModal(title, fields, on_submit_callback)

@bot.tree.command(name='抽獎',description='消耗陽壽抽獎')
@app_commands.choices(選擇獎池=[
  app_commands.Choice(name="一般獎池", value="norm_p"),
  app_commands.Choice(name="道具卡10連抽(5陽壽)", value="item_p"),
  #app_commands.Choice(name="王石抽獎", value="xtal_p")
  ])
async def lottery(interaction: discord.Interaction,選擇獎池:app_commands.Choice[str]):
 with open('user.json', 'r') as file , open('history.json', 'r', encoding='utf-8') as file1 , open('air.json', 'r') as file2 , open('item.json', 'r', encoding='utf-8') as file3,open('lottery.json', 'r') as file4,open("xtal_lottery.json", "r", encoding="utf-8-sig") as file5:
  xtal = json.load(file5)
  data = json.load(file)
  history = json.load(file1)
  air = json.load(file2)
  item = json.load(file3)
  lottery = json.load(file4)

 if str(interaction.user.id) not in item:
  item[str(interaction.user.id)] = [{"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]

 if any(entry["user_id"] == str(interaction.user.id) for entry in data):
    if 選擇獎池.value == "norm_p":
     async def on_submit_callback(self, interaction):
         prize = None
         gold = False
         input_count = interaction.children[0].value
         try:
            input_count = int(input_count)
         except ValueError:
             embed = discord.Embed(title=':x:請輸入一個有效整數',description=f'"{input_count}" 不是一個整數',color=discord.Color.red())
             await self.response.send_message(embed=embed,ephemeral=True)
             return
         for entry in data:
             if entry["user_id"] == str(self.user.id):
                 if input_count < 1:
                     embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
                     embed.add_field(name="• 投入的陽壽<1", value='',inline=False)
                     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                     embed.color = discord.Colour.red()
                     await self.response.send_message(embed=embed,ephemeral=True)
                     return

                 elif input_count > 10:
                    embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
                    embed.add_field(name="• 投入的陽壽>10", value='',inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                    embed.color = discord.Colour.red()
                    await self.response.send_message(embed=embed,ephemeral=True)
                    return

                 elif entry["fortune"] < input_count:
                    embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
                    embed.add_field(name="• 陽壽不足", value='',inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                    embed.color = discord.Colour.red()
                    await self.response.send_message(embed=embed,ephemeral=True)
                    return

                 embed1 = discord.Embed(title=f"{self.user.display_name}抽到了：", description=prize)
                 embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{self.user.mention}你得到了：")
                 embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/747551295489179778.gif")
                 embed.color = discord.Colour.dark_gray()
                 entry["fortune"] -= input_count

                 for i in range(0, input_count):
                     lottery[str(self.user.id)][0]["lot"] += 1
                     lottery[str(self.user.id)][0]["total"] += 1
                     pool = random.choices(["一般", "普通", "大獎"], weights=[percent["一般"], percent["普通"], percent["大獎"]])[0]
                     if lottery[str(self.user.id)][0]["lot"] == 50:#65小保
                         extra_percent = {
                            "一般": 0,
                            "大獎": 15,
                            "普通": 85
                        }
                         pool = random.choices(["一般", "普通", "大獎"], weights=[extra_percent["一般"], extra_percent["普通"], extra_percent["大獎"]])[0]
                         if pool == "大獎":
                             lottery[str(self.user.id)][0]["lot"] = 0
                     if lottery[str(self.user.id)][0]["lot"] > 90:#91開始提升機率 100必中大獎
                         extra_percent = {
                            "一般": percent["一般"] - 9.2*(lottery[str(self.user.id)][0]["lot"]-90),
                            "大獎": percent["普通"] + 10*(lottery[str(self.user.id)][0]["lot"]-90),
                            "普通": percent["大獎"] - 0.8*(75-lottery[str(self.user.id)][0]["lot"]-90)
                        }
                         pool = random.choices(["一般", "普通", "大獎"], weights=[extra_percent["一般"], extra_percent["普通"], extra_percent["大獎"]])[0]
                         if pool == "大獎":
                             lottery[str(self.user.id)][0]["lot"] = 0
                             gold = True

                     prize = random.choices(list(Prize_pools[pool].keys()), weights=list(Prize_pools[pool].values()))[0]
                     embed.add_field(name=f':gift:{prize}', value='----------',inline=False)
                     if any(entry["user_id"] == str(self.user.id) for entry in air):
                      for entry in air:
                       if entry["user_id"] == str(self.user.id):
                        if prize == "空氣":
                          entry["air"] +=1
                     else:
                      new_data={
                       "user_id" : str(self.user.id),
                       "air" : 0
                      }
                      air.append(new_data)
                      if prize == "空氣" and any(entry["user_id"] == str(self.user.id) for entry in air):
                        for entry in air:
                         if entry["user_id"] == str(self.user.id):
                          entry["air"] +=1

                     if str(self.user.id) not in history:
                         history[str(self.user.id)] = []
                         for i in range(1, 101):
                             history[str(self.user.id)].append({f"prize{i}": None})

                     if history[str(self.user.id)][99]["prize100"] is not None:
                        for i in range(2, 101):
                            history[str(self.user.id)][i-2][f"prize{i-1}"] = history[str(self.user.id)][i-1][f"prize{i}"]
                        history[str(self.user.id)][99]["prize100"] = prize

                     for i in range(1, 101):
                        if  history[str(self.user.id)][i-1][f"prize{i}"] is None:
                            history[str(self.user.id)][i-1][f"prize{i}"] = prize
                            break

                     if prize.startswith("鮭魚幣"):
                       if any(entry["user_id"] == str(self.user.id) for entry in data):
                         for entry in data:
                          if entry["user_id"] == str(self.user.id):
                            coins = int(prize.split("鮭魚幣")[1])
                            entry["coin"] += coins
                            entry["gain"] += coins
                     elif prize != "空氣":
                       embed1.add_field(name=prize, value='',inline=False)

                 if len(embed1.fields) > 0:
                    await bot.get_channel(1183431186161340466).send(embed=embed1)
                 if gold == True:
                     with open('user.json', 'w') as file , open('history.json', 'w' ,encoding='utf-8') as file1 , open('air.json', 'w') as file2 , open('item.json', 'w' ,encoding='utf-8') as file3,open('lottery.json', 'w') as file4 :
                          json.dump(data, file, indent=4)
                          json.dump(history, file1, indent=4, ensure_ascii=False)
                          json.dump(air, file2, indent=4)
                          json.dump(item, file3, indent=4)
                          json.dump(lottery, file4, indent=4)
                     if input_count>1:
                        await self.response.send_message('https://cdn.discordapp.com/attachments/815780487708540990/1198602167448244274/hqzyh-7kjbx.gif')
                     else:
                        await self.response.send_message('https://cdn.discordapp.com/attachments/815780487708540990/1198602203569590332/4dmly-jeaoz.gif')
                     await asyncio.sleep(5.7)
                     await self.edit_original_response(embed=embed,content='')
                 else:
                     await self.response.send_message(embed=embed)

                 with open('user.json', 'w') as file , open('history.json', 'w' ,encoding='utf-8') as file1 , open('air.json', 'w') as file2 , open('item.json', 'w' ,encoding='utf-8') as file3,open('lottery.json', 'w') as file4 :
                  json.dump(data, file, indent=4)
                  json.dump(history, file1, indent=4, ensure_ascii=False)
                  json.dump(air, file2, indent=4)
                  json.dump(item, file3, indent=4)
                  json.dump(lottery, file4, indent=4)

     fields = {
        "input": {
            "label": "陽壽",
            "placeholder": "輸入要投入的陽壽！(1~10)",
            "required": True
        }
    }
     modal = create_modal("陽壽人陽壽魂(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", fields, on_submit_callback)
     if str(interaction.user.id) not in lottery:
         lottery[str(interaction.user.id)] = [{"lot":0,"total":0}]
     await interaction.response.send_modal(modal)

    elif 選擇獎池.value == "item_p":
        for entry in data:
             if entry["user_id"] == str(interaction.user.id):
                if entry["fortune"] < 5:
                    embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
                    embed.add_field(name="• 陽壽不足", value='',inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                    embed.color = discord.Colour.red()
                    await interaction.response.send_message(embed=embed,ephemeral=True)
                elif item[str(interaction.user.id)][0]["lottery"] == True:
                    embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
                    embed.add_field(name="• 你今天已經10連抽過了！", value='',inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                    embed.color = discord.Colour.red()
                    await interaction.response.send_message(embed=embed,ephemeral=True)

                else:
                    prize = random.choices(list(item_pools.keys()), weights=list(item_pools.values()), k=10)
                    entry["fortune"]-= 5
                    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}你得到了：")
                    for prizes in prize:
                     embed.add_field(name="", value=prizes, inline=False)
                     if prizes.startswith("鮭魚幣"):
                       if any(entry["user_id"] == str(interaction.user.id) for entry in data):
                         for entry in data:
                          if entry["user_id"] == str(interaction.user.id):
                            coins = int(prizes.split("鮭魚幣")[1])
                            entry["coin"] += coins
                            entry["gain"] += coins
                     else:
                         item[str(interaction.user.id)][0][item_pools_trans[prizes]]+=1
                    item[str(interaction.user.id)][0]["lottery"] = True
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/747551295489179778.gif")
                    embed.add_field(name=" ", value="迴轉卡數量是完全保密的\n不要輕易自爆喔owo", inline=False)
                    embed.color = discord.Colour.dark_gray()
                    await interaction.user.send(embed=embed)
                    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}已完成十連抽！")
                    embed.add_field(name="私訊可查看十連結果。", value='', inline=False)
                    embed.color = discord.Colour.dark_gray()
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                    await interaction.response.send_message(embed=embed)

    elif 選擇獎池.value == "xtal_p":
        async def xtal_1(interaction):
            async def xtal_2(interaction):
                with open ('user_xtaldata.json','r',encoding='utf-8-sig') as xt:
                    xtal_data = json.load(xt)

                    values = sorted(select.values, key=lambda x: int(x.split('/')[0]), reverse=True)
                    check = False

                    for i in values:
                        index, item_name = i.split('/')
                        index = int(index)

                        if index >= len(xtal_data[str(interaction.user.id)]['mail']):
                            check = True
                            break
        
                        if xtal_data[str(interaction.user.id)]['mail'][index]['name'] != item_name:
                            check = True
                            break

                    if check:
                        embed = discord.Embed(title=':x: 領取錯誤 請嘗試打開一個新頁面', color=discord.Color.red())
                        await interaction.response.edit_message(embed=embed,view=None)

                    else:
                        embed = discord.Embed(title='兌換成功！', description=f'換取了一次的免費抽獎機會', color=randcolor())
                        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1075897670029287455.gif')
                        xtal_data[str(interaction.user.id)]["free"] += 1
                        await interaction.response.edit_message(embed=embed,view=None)
        
                        for i in sorted([int(v.split('/')[0]) for v in values], reverse=True):
                            del xtal_data[str(interaction.user.id)]["mail"][i]

                        with open('user_xtaldata.json', 'w', encoding='utf-8-sig') as xt:
                            json.dump(xtal_data, xt, ensure_ascii=False, indent=4)

            async def xtal_3(interaction):
                with open('user_xtaldata.json', 'r', encoding='utf-8-sig') as xt:
                    xtal_data = json.load(xt)

                values = sorted(select.values, key=lambda x: int(x.split('/')[0]), reverse=True)
                check = False
                embed1 = discord.Embed(title=f'{interaction.user.display_name}抽到了：')

                for i in values:
                    index, item_name = i.split('/')
                    index = int(index)
                    embed1.add_field(name=item_name, value='', inline=False)

                    if index >= len(xtal_data[str(interaction.user.id)]['mail']):
                        check = True
                        break
        
                    if xtal_data[str(interaction.user.id)]['mail'][index]['name'] != item_name:
                        check = True
                        break

                if check:
                    embed = discord.Embed(title=':x: 領取錯誤 請嘗試打開一個新頁面', color=discord.Color.red())
                    await interaction.response.edit_message(embed=embed,view=None)

                else:
                    embed = discord.Embed(title='領取成功！', description=f'共領取了 {len(values)} 個獎勵', color=randcolor())
                    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1075897670029287455.gif')
                    await interaction.response.edit_message(embed=embed,view=None)
                    await bot.get_channel(1183431186161340466).send(embed=embed1)
        
                    for i in sorted([int(v.split('/')[0]) for v in values], reverse=True):
                        del xtal_data[str(interaction.user.id)]["mail"][i]

                    with open('user_xtaldata.json', 'w', encoding='utf-8-sig') as xt:
                        json.dump(xtal_data, xt, ensure_ascii=False, indent=4)


            cus = interaction.data['custom_id']
            with open('user_xtaldata.json', 'r', encoding='utf-8-sig') as xt:
                xtal_data = json.load(xt)
            if 'lot' in cus:
                if len(xtal_data[str(interaction.user.id)]['mail']) == 0:
                    embed = discord.Embed(title=f'{interaction.user.display_name}目前的臨時背包',description='空空如也',color=randcolor())
                    await interaction.response.send_message(embed=embed,ephemeral=True)
                    return

                if len(xtal_data[str(interaction.user.id)]['mail']) < 25:
                    embed = discord.Embed(title=f'{interaction.user.display_name}目前的臨時背包',color=randcolor())
                else:
                    embed = discord.Embed(title=f'{interaction.user.display_name}目前的臨時背包',description=f'共{len(xtal_data[str(interaction.user.id)]["mail"])}個道具(只顯示前25項)',color=randcolor())

                view = View()
                xtals = []
                for i in range(min(len(xtal_data[str(interaction.user.id)]['mail']), 25)):
                    embed.add_field(name=xtal_data[str(interaction.user.id)]["mail"][i]['name'],value=xtal_data[str(interaction.user.id)]["mail"][i]['time'].split(' ')[0] + ' --' + xtal_data[str(interaction.user.id)]["mail"][i]['time'].split(' ')[1] + '--',inline=False)
                    xtals.append(discord.SelectOption(label=xtal_data[str(interaction.user.id)]["mail"][i]['name'],value=f"{i}/{xtal_data[str(interaction.user.id)]['mail'][i]['name']}"))

                if cus == 'lot_1':#分解5:1
                    if len(xtal_data[str(interaction.user.id)]["mail"]) < 5:
                        embed = discord.Embed(title=':x: 你的王石總數不足5 無法兌換！',color=discord.Color.red())
                        await interaction.response.send_message(embed=embed,ephemeral=True)
                    else:
                        select = discord.ui.Select(placeholder='點我兌換免費抽取！', options=xtals,max_values=5,min_values=5)
                        select.callback = xtal_2
                        view.add_item(select)
                        await interaction.response.send_message(embed=embed,view=view,ephemeral=True)

                elif cus == 'lot_2':#領取
                    select = discord.ui.Select(placeholder='點我兌換獎品！', options=xtals,max_values=min(len(xtal_data[str(interaction.user.id)]['mail']), 25))
                    select.callback = xtal_3
                    view.add_item(select)
                    await interaction.response.send_message(embed=embed,view=view,ephemeral=True)

                else:
                    await interaction.response.send_message(embed=embed,ephemeral=True)

            else:
                cus = int(cus)
                for entry in data:
                    if entry["user_id"] == str(interaction.user.id):
                        total = cus * 3
                        cost = max(0,total - (min(cus,xtal_data[str(interaction.user.id)]["free"]) * 3))
                        if entry["fortune"] < cost:
                            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
                            embed.add_field(name="• 陽壽不足", value='',inline=False)
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                            embed.color = discord.Colour.red()
                            await interaction.response.send_message(embed=embed,ephemeral=True)
                            
                        else:
                            entry["fortune"] -= cost
                            xtal_data[str(interaction.user.id)]["free"] -= min(cus,xtal_data[str(interaction.user.id)]["free"])
                            weight = list(xtal[0].values())
                            embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}你得到了：")
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1250623119169945722.gif")
                            embed.color = discord.Colour.dark_gray()
                            t = datetime.now(taipei_timezone)
                            time
                            for num in range(0, cus):
                                lott = random.choices(list(xtal[0].keys()), weights=weight)[0]
                                embed.add_field(name=lott,value='',inline=False)
                                d = {
                                    "name":lott,
                                    "time":f'{t.year}/{t.month}/{t.day} {t.hour}:{"0" + str(t.minute) if len(str(t.minute)) == 1 else t.minute}:{"0" + str(t.second) if len(str(t.second)) == 1 else t.second}'
                                    }
                                xtal_data[str(interaction.user.id)]['mail'].append(d)

                            embed.add_field(name=f'抽獎成功 消耗了{cost}陽壽',value=f'共{cus}個道具已進入臨時背包！')
                            await interaction.response.send_message(embed=embed)

                            with open('user.json', 'w') as file,open('user_xtaldata.json', 'w',encoding='utf-8-sig') as xt:
                                 json.dump(data, file, indent=4)
                                 json.dump(xtal_data,xt,indent=4,ensure_ascii=False)

        with open ('user_xtaldata.json','r',encoding='utf-8-sig') as xt:
            xtal_data = json.load(xt)

        t = datetime.now(taipei_timezone)
        if str(interaction.user.id) not in xtal_data:
            xtal_data[str(interaction.user.id)] = {
                "free":3 if (t.month < 8 or (t.month == 8 and t.day <= 31)) else 0,
                "mail":[]
                }
        with open('user_xtaldata.json', 'w',encoding='utf-8-sig') as xt:
            json.dump(xtal_data,xt,indent=4,ensure_ascii=False)

        one_button = Button(label='1抽',custom_id='1',style=discord.ButtonStyle.success,emoji=bot.get_emoji(1272223956228767854))
        five_button = Button(label='5抽',custom_id='5',style=discord.ButtonStyle.success,emoji=bot.get_emoji(1272223954261512314))
        ten_button = Button(label='10抽',custom_id='10',style=discord.ButtonStyle.success,emoji=bot.get_emoji(1272223938772074517))
        lottery_button_1 = Button(label='兌換王石',custom_id='lot_2',style=discord.ButtonStyle.blurple,emoji=bot.get_emoji(1272545890967617658),row=1)
        lottery_button_2 = Button(label='兌換免費抽取',custom_id='lot_1',style=discord.ButtonStyle.blurple,emoji=bot.get_emoji(1272545900681498705),row=1)
        lottery_button_3 = Button(label='查看臨時背包',custom_id='lot_3',style=discord.ButtonStyle.blurple,emoji=bot.get_emoji(1206825617912504380),row=2)
        view = View()
        for i in [one_button,five_button,ten_button,lottery_button_1,lottery_button_2,lottery_button_3]:
            i.callback = xtal_1
            view.add_item(i)
        embed = discord.Embed(title='王石抽獎',description=f'{interaction.user.mention} 你目前有 {xtal_data[str(interaction.user.id)]["free"]} 次免費抽取的機會',color=randcolor())
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1206653152795959388.webp')
        embed.add_field(name='抽獎價格：',value='**--------------------**',inline=False)
        embed.add_field(name=f'{bot.get_emoji(1272223956228767854)} 1抽',value='3陽壽',inline=False)
        embed.add_field(name=f'{bot.get_emoji(1272223954261512314)} 5抽',value='15陽壽',inline=False)
        embed.add_field(name=f'{bot.get_emoji(1272223938772074517)} 10抽',value='30陽壽',inline=False)
        embed.add_field(name='--------------------',value='**__限時加倍__**：',inline=False)
        embed.add_field(name=f'{xtal[1]["item"]} 機率限時提升！',value=f'(剩餘{7-xtal[1]["date"]}天)',inline=False)
        embed.add_field(name='抽獎規則：',value='3陽壽一抽，價格不定時改變\n(優先使用免費抽取次數)\n抽獎後，王石會進入**__臨時背包__**\n需要用戶點選按鈕自行領出\n或是使用五個獎品**__兌換一次免費抽獎__**',inline=False)
        await interaction.response.send_message(embed=embed,view=view)


 else:
  embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
  embed.add_field(name="• 對象尚未登記", value='',inline=False)
  embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
  embed.color = discord.Colour.red()
  await interaction.response.send_message(embed=embed)     

 with open('user.json', 'w') as file , open('history.json', 'w' ,encoding='utf-8') as file1 , open('air.json', 'w') as file2 , open('item.json', 'w' ,encoding='utf-8') as file3,open('lottery.json', 'w') as file4 :
  json.dump(data, file, indent=4)
  json.dump(history, file1, indent=4, ensure_ascii=False)
  json.dump(air, file2, indent=4)
  json.dump(item, file3, indent=4)
  json.dump(lottery, file4, indent=4)

@bot.tree.command(name='歷史紀錄', description='抽獎歷史紀錄')
async def history(interaction: discord.Interaction):
    with open('history.json', 'r', encoding='utf-8') as file:
        history = json.load(file)

    if str(interaction.user.id) in history:
        if history[str(interaction.user.id)][0]["prize1"] is None:
            embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention} 你的抽獎歷史紀錄如下：")
            embed.add_field(name="無紀錄", value='', inline=False)
            embed.color = discord.Colour.gold()
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053886138990997664.webp")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention} 你的抽獎歷史紀錄如下：")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053886138990997664.webp")
            embed.color = discord.Colour.gold()
            prizes = [list(entry.values())[0] for entry in history.get(str(interaction.user.id), []) if list(entry.values())[0] is not None]
            formatted_prizes = [f"{prize}\n" for prize in prizes]
            formatted_prizes_text = "".join(formatted_prizes)
            prizes_per_page = 10
            formatted_prizes_pages = [formatted_prizes[i:i+prizes_per_page] for i in range(0, len(formatted_prizes), prizes_per_page)]

            for index, page in enumerate(formatted_prizes_pages, start=1):
                formatted_page_text = "".join(page)
                embed.add_field(name=formatted_page_text, value='', inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)


    else:
        embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
        embed.add_field(name="• 對象尚未登記(請先使用**/用戶資訊**)", value='', inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.color = discord.Colour.red()
        await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name='排行', description='查看已獲得鮭魚幣的排行')
async def rank(interaction: discord.Interaction):
  with open('user.json', 'r') as file:
      data = json.load(file)
  rank = sorted(data, key=lambda x: x["gain"], reverse=True)
  top_five = [entry for entry in rank if bot.get_guild(interaction.guild_id).get_member(int(entry["user_id"]))][:5]

  embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="排行榜")
  embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1168906560626495488.webp")
  embed.color = discord.Colour.dark_purple()

  for i, entry in enumerate(top_five, 1):
      user = bot.get_guild(interaction.guild_id).get_member(int(entry["user_id"]))
      embed.add_field(name=f'{user.display_name}', value=f' {entry["gain"]}\n', inline=False)
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name='空氣排行', description='查看誰抽到的空氣最多')
async def air(interaction: discord.Interaction):
  with open('air.json', 'r') as file:
     air = json.load(file)
  rank = sorted(air, key=lambda x: x["air"], reverse=True)
  embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="到底誰最非")
  embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1096429766439092255.webp")
  embed.color = discord.Colour.dark_purple()
  for i in rank[:5]:
   user = bot.get_guild(interaction.guild_id).get_member(int(i["user_id"]))
   if user == None:
       continue
   embed.add_field(name=f'{user.display_name}', value=f' {i["air"]}\n',inline=False)
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name='迴轉卡設定',description='開啟/關閉迴轉')
@app_commands.choices(開關=[
  app_commands.Choice(name="開", value="T"),
  app_commands.Choice(name="關", value="F"),
  ])
@app_commands.describe(開關="設定是否自動使用迴轉")
async def trans(interaction: discord.Interaction,開關: app_commands.Choice[str]):
 with open('item.json', 'r') as file:
     item = json.load(file)
 if str(interaction.user.id) not in item:
  item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
  embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
  embed.add_field(name="• 迴傳卡不足", value='',inline=False)
  embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
  embed.color = discord.Colour.red()
  await interaction.response.send_message(embed=embed,ephemeral=True)

 elif item[str(interaction.user.id)][0]["trans"]>0:
   if 開關.value == "T":
       item[str(interaction.user.id)][0]["protect"] = True
       embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"**你把自動迴轉設定成 {開關.name}**")
       embed.color = discord.Colour.blurple()
       embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
       await interaction.response.send_message(embed=embed,ephemeral=True)
   else:
       item[str(interaction.user.id)][0]["protect"] = False
       embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"**你把自動迴轉設定成 {開關.name}**")
       embed.color = discord.Colour.blurple()
       embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
       await interaction.response.send_message(embed=embed,ephemeral=True)
 else:
      embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
      embed.add_field(name="• 迴傳卡不足", value='',inline=False)
      embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
      embed.color = discord.Colour.red()
      await interaction.response.send_message(embed=embed,ephemeral=True)


 with open('item.json', 'w') as file:
    json.dump(item, file, indent=4)

@bot.tree.command(name='創建身分組',description='創造一個身分組')
@app_commands.describe(r="rgb中的'r'",g="rgb中的'g'",b="rgb中的'b'",身分組名="名字")
async def add_role(interaction: discord.Interaction,r:int,g:int,b:int,身分組名:str):
  test = discord.utils.get(interaction.user.guild.roles, name=身分組名)
  if test != None:
      test = test.name
  with open('item.json', 'r') as file:
     item = json.load(file)
  if str(interaction.user.id) not in item or item[str(interaction.user.id)][0]["add_role"]<1:
   item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
   embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
   embed.add_field(name="• 創建身分組卡不足", value='',inline=False)
   embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
   embed.color = discord.Colour.red()
   await interaction.response.send_message(embed=embed,ephemeral=True)

  elif item[str(interaction.user.id)][0]["add_role"]>0:
   if (身分組名 == test) or r>255 or r<0 or g>255 or g<0 or b>255 or b<0:
    embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
    embed.add_field(name="• 這個身分組名稱已經存在！", value='',inline=False)
    embed.add_field(name="• RGB超過範圍！(0~255)", value='',inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
    embed.color = discord.Colour.red()
    await interaction.response.send_message(embed=embed,ephemeral=True)

   else:
       await interaction.guild.create_role(name=身分組名,color=discord.Color.from_rgb(r, g, b))
       item[str(interaction.user.id)][0]["add_role"] -=1
       embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="")
       embed.add_field(name=f"{interaction.user.display_name} 創建了一個身分組", value=f'{discord.utils.get(interaction.user.guild.roles, name=身分組名).mention}',inline=True)
       embed.color = discord.Colour.blurple()
       embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
       await interaction.response.send_message(embed=embed)
  with open('item.json', 'w') as file:
    json.dump(item, file, indent=4)

@bot.tree.command(name='指定身分組',description='增加一個人的身分組')
@app_commands.choices(顯示身分組顏色=[
  app_commands.Choice(name="是", value="T"),
  app_commands.Choice(name="否", value="F"),
  ],啟用必中=[
  app_commands.Choice(name="是", value="T"),
  app_commands.Choice(name="否", value="F"),
  ])
@app_commands.describe(用戶名="要增加的人的名字",欲加的身分組="要增加的身分組",顯示身分組顏色="是否要顯示身分組顏色",啟用必中="額外消耗兩張迴轉卡")
async def role(interaction: discord.Interaction,用戶名:discord.Member,欲加的身分組:discord.Role,顯示身分組顏色: app_commands.Choice[str], 啟用必中: app_commands.Choice[str]):
 with open('item.json', 'r') as file:
  item = json.load(file)
 test = 欲加的身分組
 test1 = None
 if test != None:
     test1 = test.name
     if str(test.id) not in item:
        item[str(test.id)] = [{"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 if str(interaction.user.id) not in item:
     item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 if item[str(test.id)][0]["protect"] == False:
    User = discord.utils.get(interaction.guild.members, name=用戶名.name)
    roles = User.roles
    u = [member for member in interaction.guild.members if discord.utils.get(member.roles, name=test1) is not None]
    if u:
        h = max(u, key=lambda member: max(member.roles, default=None, key=lambda r: r.position).position)
        highest1 = max(h.roles, default=None, key=lambda r: r.position)
        highest2 = max(roles, key=lambda r: r.position)
        highest = min(highest1, highest2)
    else:
        highest = max(roles, key=lambda r: r.position)

 elif item[str(test.id)][0]["protect"] == True and 用戶名 != str(interaction.user.name):
    User = discord.utils.get(interaction.guild.members, name=用戶名)
    roles = interaction.user.roles
    u = [member for member in interaction.guild.members if discord.utils.get(member.roles, name=test1) is not None]
    if u:
        h = max(u, key=lambda member: max(member.roles, default=None, key=lambda r: r.position).position)
        highest1 = max(h.roles, default=None, key=lambda r: r.position)
        highest2 = max(roles, key=lambda r: r.position)
        highest = min(highest1, highest2)
    elif 顯示身分組顏色.value == "T":
        highest = max(discord.utils.get(interaction.guild.members, name=用戶名).roles, key=lambda r: r.position)
    else:
        highest = max(roles, key=lambda r: r.position)


 if 欲加的身分組.name == test1 and test1 not in do_not_role:
  role = 欲加的身分組
  if item[str(interaction.user.id)][0]["role"]<1:
   embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
   embed.add_field(name="• 指定身分組卡不足", value='',inline=False)
   embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
   embed.color = discord.Colour.red()
   await interaction.response.send_message(embed=embed,ephemeral=True)

  elif item[str(interaction.user.id)][0]["role"]>0:
   if 顯示身分組顏色.value == "T":
       await test.edit(position=highest.position)
   if str(User.id) not in item:
       item[str(User.id)] = [{"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
   if(item[str(User.id)][0]["protect"])==True and User.id != interaction.user.id and 啟用必中.value == "F":
       await interaction.user.add_roles(role)
       embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="")
       embed.add_field(name=f"{User.display_name} 開啟了迴轉卡保護！", value='',inline=False)
       embed.add_field(name=f"{interaction.user.display_name} 你被加了 {role.mention} 身分組", value='',inline=False)
       embed.add_field(name="", value='||可憐 笑死||',inline=False)
       embed.color = discord.Colour.dark_gray()
       embed.set_thumbnail(url="https://media3.giphy.com/media/PlKJlK0gwKOzUa771g/giphy.gif")
       item[str(User.id)][0]["trans"]-=1
       if item[str(User.id)][0]["trans"] == 0:
           item[str(User.id)][0]["protect"] = False
       item[str(interaction.user.id)][0]["role"]-=1
       await interaction.response.send_message(embed=embed)
       embed = discord.Embed(title="__通知__", description=f"\n你迴轉了 {interaction.user.display_name} 加的 {role.name} 身分組")
       embed.add_field(name=f'你的迴轉卡剩下 {item[str(User.id)][0]["trans"]} 張', value='\n**注意 迴轉卡歸0會自動關閉迴轉**',inline=False)
       await User.send(embed=embed)

   elif item[str(interaction.user.id)][0]["trans"]<2 and 啟用必中.value=="T":
      embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
      embed.add_field(name="• 迴轉卡不足", value='',inline=False)
      embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
      embed.color = discord.Colour.red()
      await interaction.response.send_message(embed=embed)

   else:
    await User.add_roles(role)
    if 啟用必中.value == "T" and User.id != interaction.user.id:
        item[str(interaction.user.id)][0]["trans"]-=2
        if item[str(interaction.user.id)][0]["trans"] == 0:
         item[str(interaction.user.id)][0]["protect"] = False
    item[str(interaction.user.id)][0]["role"]-=1
    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="")
    embed.add_field(name=f"{interaction.user.display_name} 對 {User.display_name}", value=f'加了 {role.mention} 身分組！',inline=False)
    embed.color = discord.Colour.blurple()
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/854293535171280898.webp")
    await interaction.response.send_message(embed=embed)
    embed = discord.Embed(title="__通知__", description=f"\n你被 {interaction.user.display_name} 加了 {role.name} 身分組")
    await User.send(embed=embed)

 else:
   embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
   embed.add_field(name="• 找不到身分組名字", value='',inline=False)
   embed.add_field(name="• 不可以增加這個身分組", value='',inline=False)
   embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
   embed.color = discord.Colour.red()
   await interaction.response.send_message(embed=embed,ephemeral=True)

 with open('item.json', 'w') as file:
    json.dump(item, file, indent=4)

@bot.tree.command(name='指定暱稱',description='指定一個人的暱稱')
@app_commands.choices(啟用必中=[
  app_commands.Choice(name="是", value="T"),
  app_commands.Choice(name="否", value="F"),
  ])
@app_commands.describe(用戶名="要改的人的名字",暱稱="要修改的暱稱",啟用必中="額外消耗兩張迴轉卡")
async def nick(interaction:discord.Interaction,用戶名:discord.Member,暱稱:str, 啟用必中: app_commands.Choice[str]):
 with open('item.json', 'r') as file:
  item = json.load(file)
 if str(interaction.user.id) not in item:
  item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 test = discord.utils.get(interaction.user.guild.members, name=用戶名.name)
 if test!= None and str(test.id) not in item:
   item[str(test.id)] = [{"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 if test != None and item[str(interaction.user.id)][0]["nick"]>0:
     if item[str(test.id)][0]["protect"] == True and 啟用必中.value == "F" and interaction.user.id != test.id:
         item[str(interaction.user.id)][0]["nick"]-=1
         item[str(test.id)][0]["trans"] -=1
         await interaction.user.edit(nick=暱稱)
         if item[str(test.id)][0]["trans"] == 0:
           item[str(test.id)][0]["protect"] = False
         embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="")
         embed.add_field(name=f"{test.display_name} ", value=f'開啟了迴轉卡保護！',inline=False)
         embed.add_field(name=f"{interaction.user.name} 你現在叫 {暱稱}", value='',inline=False)
         embed.add_field(name="", value='||可憐 笑死||',inline=False)
         embed.color = discord.Colour.dark_gray()
         embed.set_thumbnail(url="https://media3.giphy.com/media/PlKJlK0gwKOzUa771g/giphy.gif")
         await interaction.response.send_message(embed=embed)
         embed = discord.Embed(title="__通知__", description=f"\n你迴轉了 {interaction.user.display_name} 改的 {暱稱} 暱稱")
         embed.add_field(name=f'你的迴轉卡剩下 {item[str(test.id)][0]["trans"]} 張', value='\n**注意 迴轉卡歸0會自動關閉迴轉**',inline=False)
         await test.send(embed=embed)

     elif item[str(interaction.user.id)][0]["trans"]<2 and 啟用必中.value=="T" :
        embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
        embed.add_field(name="• 迴轉卡不足", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.color = discord.Colour.red()
        await interaction.response.send_message(embed=embed,ephemeral=True)

     else:
         if 啟用必中.value == "T" and test.id != interaction.user.id:
          item[str(interaction.user.id)][0]["trans"]-=2
          if item[str(interaction.user.id)][0]["trans"] == 0:
             item[str(interaction.user.id)][0]["protect"] = False
         item[str(interaction.user.id)][0]["nick"]-=1
         await test.edit(nick=暱稱)
         embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="")
         embed.add_field(name=f"{interaction.user.display_name} 把 {test.name} 的名字改成了 {暱稱}", value=f'',inline=False)
         embed.color = discord.Colour.blurple()
         embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/854293535171280898.webp")
         await interaction.response.send_message(embed=embed)
         embed = discord.Embed(title="__通知__", description=f"\n你被 {interaction.user.display_name} 改了 {暱稱} 暱稱")
         await test.send(embed=embed)

 else:
     embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
     embed.add_field(name="• 命名卡不足", value='',inline=False)
     embed.add_field(name="• 找不到用戶名", value='',inline=False)
     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
     embed.color = discord.Colour.red()
     await interaction.response.send_message(embed=embed,ephemeral=True)
 with open('item.json', 'w') as file:
    json.dump(item, file, indent=4)

@bot.tree.command(name='道具卡背包',description='檢視道具卡背包')
async def itembag(interaction:discord.Interaction):
 with open('item.json', 'r') as file:
  item = json.load(file)
 if str(interaction.user.id) not in item:
  item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}你的道具卡背包:")
 embed.add_field(name="迴轉卡:", value=item[str(interaction.user.id)][0]["trans"],inline=False)
 embed.add_field(name="指定暱稱卡:", value=item[str(interaction.user.id)][0]["nick"],inline=False)
 embed.add_field(name="增加身分組卡:", value=item[str(interaction.user.id)][0]["add_role"],inline=False)
 embed.add_field(name="指定身分組卡:", value=item[str(interaction.user.id)][0]["role"],inline=False)
 embed.add_field(name="迴轉卡保護:", value='關' if item[str(interaction.user.id)][0]["protect"] == False else '開',inline=False)
 embed.set_thumbnail(url=interaction.user.avatar.url)
 embed.color = discord.Colour.gold()
 await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name='列出身分組', description='列出可指定的身分組')
async def role_list(interaction: discord.Interaction):
    roles = interaction.user.guild.roles
    role = [
        f"{role.mention}"
        for role in roles
        if role.name not in do_not_role and role.name != "@everyone" and not role.is_bot_managed()
    ]
    embed = discord.Embed(title="可指定的身分組有：\n", description="\n".join(role))
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name='道具賣出', description='賣出自己的道具')
@app_commands.describe(數量="要賣出的數量")
async def down_item(interaction: discord.Interaction,數量:int):
    with open ('item.json','r') as file1,open ('user.json','r') as file2:
        item = json.load(file1)
        user = json.load(file2)

    if 數量 < 1:
        embed = discord.Embed(title="市場上架結果", description="")
        embed.add_field(name="• 數量不能小於1", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.color = discord.Colour.red()
        await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        async def on_select_option(interaction):
            val = select.values[0]
            name = [key for key, value in item_pools_trans.items() if value == val]
            for info in user:
                if info["user_id"] == str(interaction.user.id):
                    info["coin"] += sell.get(val)*數量
                    break
            item[str(interaction.user.id)][0][val] -= 數量
            if item[str(interaction.user.id)][0]["trans"]==0:
                item[str(interaction.user.id)][0]["protect"] = False

            embed = discord.Embed(title="賣出結果", description="")
            embed.add_field(name="賣出成功！", value='你賣掉了：',inline=False)
            embed.add_field(name="道具名稱", value=name[0],inline=False)
            embed.add_field(name="鮭魚幣", value=f':coin: **{sell.get(val)*數量}** 鮭魚幣',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
            embed.color = discord.Colour.green()
            await interaction.response.edit_message(content="",embed=embed,view=None)
            with open ('user.json','w') as file2,open ('item.json','w') as file1:
                    json.dump(user, file2, indent=4)
                    json.dump(item, file1, indent=4)


        options = []
        if 數量 <= item[str(interaction.user.id)][0]["trans"]:
          options.append(discord.SelectOption(label=f'迴轉卡({item[str(interaction.user.id)][0]["trans"]})(售價:{2000*數量})', value='trans'))
        if 數量 <= item[str(interaction.user.id)][0]["nick"]:
          options.append(discord.SelectOption(label=f'指定暱稱卡({item[str(interaction.user.id)][0]["nick"]})(售價:{1000*數量})', value='nick'))
        if 數量 <= item[str(interaction.user.id)][0]["role"]:
          options.append(discord.SelectOption(label=f'指定身分組卡({item[str(interaction.user.id)][0]["role"]})(售價:{1000*數量})', value='role'))
        if 數量 <= item[str(interaction.user.id)][0]["add_role"]:
          options.append(discord.SelectOption(label=f'增加身分組卡({item[str(interaction.user.id)][0]["add_role"]})(售價:{750*數量})', value='add_role'))
        if len(options)==0:
           embed = discord.Embed(title="市場上架結果", description="")
           embed.add_field(name="• 沒有合適數量的道具", value='',inline=False)
           embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
           embed.color = discord.Colour.red()
           await interaction.response.send_message(embed=embed,ephemeral=True)  

        else:
            select = discord.ui.Select(placeholder='點我！', options=options)
            select.callback = on_select_option
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message("選擇賣出的物品",view=view,ephemeral=True)

@bot.tree.command(name="每日商店", description="每日商店")
async def shop(interaction: discord.Interaction):
    with open('shop.json', 'r', encoding='utf-8') as file:
        shop = json.load(file)
    with open('user.json', 'r', encoding='utf-8') as file1:
        data = json.load(file1)

    async def button_callback(interaction):
        with open('shop.json', 'r', encoding='utf-8') as file:
            shop = json.load(file)
        with open('user.json', 'r', encoding='utf-8') as file1:
            data = json.load(file1)

        custom = interaction.data['custom_id']
        find = False

        for entry in data:
            if entry["user_id"] == str(interaction.user.id):
                find = True
                break

        if not find:
            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
            embed.add_field(name="• 用戶尚未登記(請先使用**/用戶資訊**)", value='', inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if entry['buy'] > 0:
            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
            embed.add_field(name="• 一天只能買一次商品", value='', inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if entry["coin"] < shop[f"slot{int(custom)}"]["price"]:
            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
            embed.add_field(name="• 鮭魚幣不足", value='', inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        entry["buy"] += 1
        item = shop[f"slot{int(custom)}"]["item"]
        price = shop[f"slot{int(custom)}"]["price"]

        if '陽壽' in item:
            fort = int(item.split('陽壽')[0])
            entry["fortune"] += fort
        else:
            embed1 = discord.Embed(title=f"{interaction.user.display_name}買了：", description=item)
            await bot.get_channel(1183431186161340466).send(embed=embed1)
        entry["coin"] -= price

        with open('user.json', 'w', encoding='utf-8') as file1:
            json.dump(data, file1, indent=4, ensure_ascii=False)

        embed = discord.Embed(title="購買結果", description="")
        embed.add_field(name="購買成功！", value="你購買了", inline=False)
        embed.add_field(name="商品", value=item, inline=False)
        embed.add_field(name="價格", value=price, inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
        embed.color = discord.Colour.green()
        await interaction.response.send_message(embed=embed)

    embed = discord.Embed(title="每日商店", description=f"{interaction.user.mention}今天的商品如下:")
    embed.color = discord.Colour.dark_blue()
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/980979727324053536.webp")
    button = []
    view = View()
    for i in range(1, 4):
        embed.add_field(name="----------", value=f'欄位{number_word.get(i)}:\n**道具名:** {shop[f"slot{i}"]["item"]}\n**價格:** {shop[f"slot{i}"]["price"]}', inline=False)
        button.append(Button(label=f"欄位{number_word.get(i)}", custom_id=str(i), style=discord.ButtonStyle.blurple))

    for j in button:
        j.callback = button_callback
        view.add_item(j)
    embed.add_field(name="----------\n\n請選擇要購買的欄位", value='', inline=True)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="上架商品", description="添加商品信息")
@app_commands.describe(商品名="上架的商品名稱",數量='單位可以輸入"組"，數字請避免使用中文，單個道具請輸入"1"',價格="可以打縮寫(例:3000w)",描述="不要超過1000字就好",類別="商品種類(請確實分類)")
@app_commands.choices(類別=[
        app_commands.Choice(name="單手劍", value="ohs"),
        app_commands.Choice(name="弓", value="bow"),
        app_commands.Choice(name="法杖", value="staff"),
        app_commands.Choice(name="大劍", value="ths"),
        app_commands.Choice(name="拔刀劍", value="ktn"),
        app_commands.Choice(name="拳套", value="kun"),
        app_commands.Choice(name="魔導具", value="md"),
        app_commands.Choice(name="弩", value="bg"),
        app_commands.Choice(name="旋風槍", value="hb"),
        app_commands.Choice(name="盾(染/外觀)", value="shield"),
        app_commands.Choice(name="星石", value="star"),
        app_commands.Choice(name="衣服", value="arm"),
        app_commands.Choice(name="追加裝備(帽子)", value="hat"),
        app_commands.Choice(name="追加裝備(戒指)", value="ring"),
        app_commands.Choice(name="消耗品(全類)", value="y"),
        app_commands.Choice(name="素材(全類)", value="pts"),
        app_commands.Choice(name="王石(全類)", value="xtal"),
        app_commands.Choice(name="託管任務", value="quest"),
        ])
async def add_product(interaction:discord.Interaction, 商品名: str, 數量: str, 價格: str,描述:str,類別:app_commands.Choice[str]):
    with open('product.json','r',encoding='utf-8') as file:
        goods = json.load(file)
    if len(描述) >= 1000:
        embed = discord.Embed(title="你是在念經嗎!?", color=0x00FFFF)
        embed.add_field(name=f"{bot.get_emoji(1206832204928389180)}你的描述太長了({len(描述)} / 1000)", value="",inline=False)
        await interaction.response.send_message(embed=embed ,ephemeral=True )
        return

    if interaction.channel.type != discord.ChannelType.private:
        embed = discord.Embed(title="如何使用", color=0x00FFFF)
        embed.add_field(name="I.這個指令只能在與機器人的私訊中使用", value="",inline=False)
        embed.add_field(name="II.在私訊使用後，依機器人提示上傳圖片，或是其他操作(教學圖如下⬇️)", value="",inline=False)
        embed.add_field(name="III.上架完成！", value="",inline=False)
        embed.set_image(url='https://cdn.discordapp.com/attachments/1186910678188036188/1206829413245653003/Screenshot_2024-02-13-13-08-51-072_com.discord-edit.jpg?ex=65dd6e79&is=65caf979&hm=90c0093ce5ca85c7f6d0a981bb0d30beda57885266d664d40f4bc07393e84deb&')
        await interaction.response.send_message(embed=embed ,ephemeral=True )
        return
    
    if len(goods[str(interaction.user.id)]) >= 25:
        embed = discord.Embed(title=f"上架結果", description="")
        embed.add_field(name="您的欄位已滿！(至多25)", value='', inline=True)
        embed.color = discord.Colour.dark_blue()
        await interaction.response.send_message(embed=embed,ephemeral=True)
        return

    await interaction.response.send_message(f'請傳送關於此商品的圖片(一個商品最多一張圖)\n如果無，請輸入"完成"\n輸入"取消"可以取消本次上架\n\n亂上傳會被星玥打屁屁{bot.get_emoji(1206826888081707099)}\n此訊息3分鐘後會過期。')
    def check(message):
        return message.channel.type == discord.ChannelType.private

    image_url = []

    while True:
        try:
            message = await bot.wait_for("message", check=check, timeout=180)
        except asyncio.TimeoutError:
            await interaction.edit_original_response(content="-此操作已超時，請重新使用指令-")
            return

        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith("image/"):
                    if len(image_url) == 0:
                        image_url.append(attachment.url)
                    else:
                        await interaction.channel.send("您只能上傳一張圖片，請重新上傳。")
                        image_url.clear()
                        break

        elif message.content == "完成":
            break

        elif message.author.bot or message.content == "取消":
            return

        else:
            await interaction.channel.send("未收到圖片，請重新發送")
            continue
    
        if image_url:
            break

    button=Button(label="是",custom_id="yes",style = discord.ButtonStyle.green)
    button2=Button(label="否",custom_id="no",style = discord.ButtonStyle.red)
    async def button_callback(interaction):
        custom = interaction.data['custom_id']
        if custom == "yes":
          time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
          if str(interaction.user.id) not in goods:
            goods[str(interaction.user.id)] = [{
                "name": 商品名,
                "quantity": 數量,
                "price": 價格,
                "user": interaction.user.display_name,
                "user_id": interaction.user.id,
                "url": image_url[0],
                "describe":描述,
                "type":類別.value,
                "type_name":類別.name,
                "date":1,
                "update":f"{time.year}/{time.month}/{time.day} {time.hour}:{time.minute}:{time.second}"
            }]
          else:
              data ={
                "name": 商品名,
                "quantity": 數量,
                "price": 價格,
                "user": interaction.user.display_name,
                "user_id": interaction.user.id,
                "url": image_url[0],
                "describe":描述,
                "type":類別.value,
                "type_name":類別.name,
                "date":1,
                "update":f"{time.year}/{time.month}/{time.day} {time.hour}:{time.minute}:{time.second}"
            }
              goods[str(interaction.user.id)].append(data)
          embed = discord.Embed(title="上架結果", description="")
          embed.add_field(name="上架成功！", value="",inline=False)
          embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
          embed.color = discord.Colour.dark_blue()
          await interaction.message.edit(embed=embed , view=None)
          with open('product.json', 'w',encoding='utf-8') as file:
              json.dump(goods, file, indent=4,ensure_ascii=False)

        elif custom == "no":
            embed = discord.Embed(title="上架結果", description="")
            embed.add_field(name="上架取消", value="",inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
            embed.color = discord.Colour.dark_blue()
            await interaction.message.edit(embed=embed , view=None)

    button.callback = button_callback
    button2.callback = button_callback
    view=View()
    view.add_item(button)
    view.add_item(button2)
    time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
    embed = discord.Embed(title="上架確認", description=f"{interaction.user.mention}請確認商品是否正確：")
    embed.add_field(name="商品名稱", value=商品名,inline=False)
    embed.add_field(name="商品價格", value=價格,inline=False)
    embed.add_field(name="商品數量", value=數量,inline=False)
    embed.add_field(name="上架日期", value=f"{time.year}/{time.month}/{time.day} {time.hour}:{time.minute}:{time.second}",inline=False)
    embed.add_field(name="類別", value=類別.name,inline=False)
    embed.add_field(name=f"商品描述", value=描述, inline=False)
    if len(image_url) != 0:
        embed.set_image(url=image_url[0])
        embed.add_field(name="商品圖片", value="",inline=False)
    else:
         image_url.append(None)
         embed.add_field(name="商品圖片", value="無",inline=False)
    embed.color = discord.Colour.dark_blue()
    await interaction.user.send(embed=embed , view=view)

@bot.tree.command(name="下架商品", description="添加商品信息")
async def add_product(interaction:discord.Interaction):
    with open('product.json','r',encoding='utf-8') as file:
        goods = json.load(file)
    if str(interaction.user.id) not in goods:
        goods[str(interaction.user.id)] = []

    if len(goods[str(interaction.user.id)]) == 0:
        embed = discord.Embed(title="下架結果", description="")
        embed.add_field(name="空空如也", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1188741347826483270.gif")
        embed.color = discord.Colour.blue()
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        product = []
        async def on_select_option(interaction):
            num = int(select.values[0])

            button=Button(label="對啦 快點下架 廢話很多欸==",custom_id="yes",style = discord.ButtonStyle.green)
            button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
            async def button_callback(interaction):
                if interaction.data['custom_id'] == "yes":
                    embed = discord.Embed(title="下架結果", description="")
                    embed.add_field(name="下架成功！", value='\n',inline=False)
                    embed.add_field(name="商品名稱", value=goods[str(interaction.user.id)][num]["name"],inline=False)
                    embed.add_field(name="商品數量", value=goods[str(interaction.user.id)][num]["quantity"],inline=False)
                    embed.add_field(name="商品價格", value=goods[str(interaction.user.id)][num]["price"],inline=False)
                    embed.add_field(name="上架日期", value=goods[str(interaction.user.id)][num]["update"],inline=False)
                    embed.add_field(name="類別", value=goods[str(interaction.user.id)][num]["type_name"],inline=False)
                    embed.add_field(name=f"商品描述", value=goods[str(interaction.user.id)][num]['describe'], inline=False)
                    if goods[str(interaction.user.id)][num]["url"] == None:
                        embed.add_field(name="商品圖片", value="無",inline=False)
                    else:
                        embed.add_field(name="商品圖片", value="",inline=False)
                        embed.set_image(url=goods[str(interaction.user.id)][num]["url"])
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                    embed.color = discord.Colour.green()
                    await interaction.response.edit_message(content="",embed=embed,view=None)
                    del goods[str(interaction.user.id)][num]
                    with open('product.json', 'w',encoding='utf-8') as file:
                        json.dump(goods, file, indent=4,ensure_ascii=False)

                elif interaction.data['custom_id'] == "no":
                    view.stop()
                    embed = discord.Embed(title="下架結果", description="")
                    embed.add_field(name="你取消了下架", value='\n',inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                    embed.color = discord.Colour.green()
                    await interaction.response.edit_message(content="",embed=embed,view=None)

            button.callback = button_callback
            button2.callback = button_callback
            view=View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title="下架確認", description="")
            embed.add_field(name="你真的要下架這個商品嗎", value='\n',inline=False)
            embed.add_field(name="商品名稱", value=goods[str(interaction.user.id)][num]["name"],inline=False)
            embed.add_field(name="商品數量", value=goods[str(interaction.user.id)][num]["quantity"],inline=False)
            embed.add_field(name="商品價格", value=goods[str(interaction.user.id)][num]["price"],inline=False)
            embed.add_field(name="上架日期", value=goods[str(interaction.user.id)][num]["update"],inline=False)
            embed.add_field(name="類別", value=goods[str(interaction.user.id)][num]["type_name"],inline=False)
            embed.add_field(name=f"商品描述", value=goods[str(interaction.user.id)][num]['describe'], inline=False)
            if goods[str(interaction.user.id)][num]["url"] == None:
                embed.add_field(name="商品圖片", value="無",inline=False)
            else:
                embed.add_field(name="商品圖片", value="",inline=False)
                embed.set_image(url=goods[str(interaction.user.id)][num]["url"])

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1163840167006720011.webp")
            embed.color = discord.Colour.red()
            await interaction.response.edit_message(embed=embed,view=view)

        for i,p in enumerate(goods[str(interaction.user.id)],start=0):
            product.append(discord.SelectOption(label=f'道具名:{p["name"]}', value=f'{i}',description=f'數量:{p["quantity"]}  價格:{p["price"]}'))

        select = discord.ui.Select(placeholder='點我選擇下架的商品！', options=product)          
        select.callback = on_select_option           
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)

@bot.tree.command(name="板子",description="/")
async def board(interaction:discord.Interaction):
    if interaction.user.id != 579618807237312512:
        return

    buttonss=[
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='單手劍',custom_id="ohs",emoji=bot.get_emoji(1206653135506898954)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='弓',custom_id="bow",emoji=bot.get_emoji(1206653122781650954)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='法杖',custom_id="staff",emoji=bot.get_emoji(1206653105886728284)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='大劍',custom_id="ths",emoji=bot.get_emoji(1206653090510540891)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='拔刀劍',custom_id="ktn",emoji=bot.get_emoji(1206653072856719361)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='拳套',custom_id="kun",emoji=bot.get_emoji(1206653056683610153)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='魔導具',custom_id="md",emoji=bot.get_emoji(1206653033975644180)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='弩',custom_id="bg",emoji=bot.get_emoji(1206652997430673528)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='旋風槍',custom_id="hb",emoji=bot.get_emoji(1206652986001199127)),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='盾(染/外觀)',custom_id="shield",emoji=bot.get_emoji(1206653010252533800)),   
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='衣服',custom_id="arm",emoji=bot.get_emoji(1206825596001194075),row=2),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='追加裝備(帽子)',custom_id="hat",emoji=bot.get_emoji(1206653184173670471),row=2),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='特殊裝備(戒指)',custom_id="ring",emoji=bot.get_emoji(1206653198182649866),row=2),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='星石',custom_id="star",emoji=bot.get_emoji(1206652973279871066),row=2),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='素材(全類)',custom_id="pts",emoji=bot.get_emoji(1206653212136964118),row=3),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='消耗品(全類)',custom_id="y",emoji=bot.get_emoji(1206825607741046814),row=3),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='王石(全類)',custom_id="xtal",emoji=bot.get_emoji(1206653152795959388),row=3),
        discord.ui.Button(style=discord.ButtonStyle.secondary,label='託管任務',custom_id="quest",emoji=bot.get_emoji(1206825617912504380),row=3),
        discord.ui.Button(style=discord.ButtonStyle.primary,label='點我快速查看所有商品數量！',custom_id="find",emoji=bot.get_emoji(1206666281017802853),row=4)
        ]
    async def button_callback(interaction):
        with open('product.json','r',encoding='utf-8') as file:
            goods = json.load(file)
        if interaction.data['custom_id'] == "find":
            embed = discord.Embed(title=f"查詢結果", color=0xF0FFFF)
            for button in buttonss:
                custom_id = button.custom_id
                if custom_id == "find":
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                quantity = 0
                for user_id, user_products in goods.items():
                    for product in user_products:
                        if product["type"] == custom_id:
                            quantity += 1
                if quantity != 0:
                    embed.add_field(name=f'{button.emoji} {button.label}', value=f'數量 : {quantity}',inline=False)
            
        all_products = []
        for user_id, user_products in goods.items():
            for product in user_products:
                if product["type"] == interaction.data['custom_id']:
                    all_products.append(product)
        if len(all_products) == 0:
            embed = discord.Embed(title=f"查詢結果(共0項)", description="")
            embed.add_field(name="無搜尋結果！", value='', inline=True)
            embed.color = discord.Colour.dark_blue()
            await interaction.response.send_message(embed=embed,ephemeral=True)
            return

        page_number = 0
        total_pages = len(all_products)
        embed = create_embed(all_products, page_number)
        buttons = [
    discord.ui.Button(style=discord.ButtonStyle.primary, label='上一頁', disabled=True, custom_id="prev"),
    discord.ui.Button(style=discord.ButtonStyle.primary, label='下一頁', disabled=len(all_products) <= 1, custom_id="next")
]

        view = discord.ui.View(timeout=None)
        for button in buttons:
            view.add_item(button)

        message = await interaction.response.send_message(embed=embed, view=view,ephemeral=True)

        async def button_callback(interaction: discord.Interaction):
            nonlocal page_number
            custom = interaction.data['custom_id']
            if custom == 'next' and page_number < total_pages - 1:
                page_number += 1
            elif custom == 'prev' and page_number > 0:
                page_number -= 1

            new_embed = create_embed(all_products, page_number)
    
            for button in view.children:
                if button.label == '上一頁':
                    button.disabled = page_number == 0
                elif button.label == '下一頁':
                    button.disabled = page_number == total_pages - 1
    
            await interaction.response.edit_message(embed=new_embed, view=view)

        for button in buttons:
            button.callback = button_callback

    for button in buttonss:
            button.callback = button_callback
    view=View(timeout=None)
    for button in buttonss:
            view.add_item(button)
    await interaction.channel.send("🛒點類別查看商品",view=view)

@bot.tree.command(name='付款',description='付款幣給其他玩家')
@app_commands.choices(幣別=[
    app_commands.Choice(name="鮭魚幣", value="鮭魚幣"),
    app_commands.Choice(name="RPG金幣", value="RPG金幣"),
    ])
@app_commands.describe(幣別='選擇一種幣別',數量="要給予的數量",用戶="收款人ID(可簡短輸入)")
async def trade(interaction: discord.Interaction,幣別:app_commands.Choice[str], 數量: int, 用戶: str):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file,open('user.json','r') as file1:
        rpg_data = json.load(file)
        user = json.load(file1)
    coin_type = 幣別.value
    check = False
    for e in user:
        if e["user_id"] == str(interaction.user.id):
            coin = e["coin"]
            check = True
            break

    if coin_type == "RPG金幣" and str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的RPG資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif coin_type == "鮭魚幣" and not check:
        embed = discord.Embed(title="噢噢...好像找不到你的用戶資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </用戶資訊:1220558554226888864> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif 數量 <= 0:
        embed = discord.Embed(title="付款的數量不可為0！", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif coin < 數量 and coin_type == "鮭魚幣":
        embed = discord.Embed(title="你的鮭魚幣不夠", description=f"",color=discord.Color.red())
        embed.add_field(name='缺少了',value=f'{數量-coin} s',inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["coin"] < 數量 and coin_type == "RPG金幣":
        embed = discord.Embed(title="你的金幣不夠", description=f"",color=discord.Color.red())
        embed.add_field(name='缺少了',value=f'{數量-rpg_data[str(interaction.user.id)]["coin"]}s',inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        async def give_1(interaction):
            async def give_2(interaction):
                custom = interaction.data["custom_id"]
                if custom == "yes":
                    embed = discord.Embed(title=':white_check_mark: 付款成功',description='',color=randcolor())
                    if coin_type == '鮭魚幣':
                        for e in user:
                            if e["user_id"] == select.values[0]:
                                e["coin"] += 數量
                                break
                        for e in user:
                            if e["user_id"] == str(interaction.user.id):
                                e["coin"] -= 數量
                                break
                    else:
                        rpg_data[select.values[0]]["coin"] += 數量
                        rpg_data[str(interaction.user.id)]["coin"] -= 數量

                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    await interaction.response.edit_message(view=None,embed=embed)
                    
                    embed = discord.Embed(title=':partying_face: 收到一筆款項',description=f'來自 {interaction.user.global_name} ({interaction.user.name})',color=randcolor())
                    embed.add_field(name='幣別',value=coin_type,inline=False)
                    embed.add_field(name='數量',value=數量,inline=False)
                    try:
                        await bot.get_user(int(select.values[0])).send(embed=embed)
                    except:
                        pass

                    with open('rpg_data.json','w',encoding='utf-8') as file,open('user.json','w') as file1:
                        json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                        json.dump(user,file1, indent=4)

                elif custom == 'no':
                    embed = discord.Embed(title=':white_check_mark: 付款取消',description='',color=randcolor())
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    await interaction.response.edit_message(view=None,embed=embed)
                

            user_ = bot.get_user(int(select.values[0]))
            embed = discord.Embed(title='付款確認',description='',color=randcolor())
            embed.add_field(name='用戶',value=f'{user_.global_name} ({user_.name})',inline=False)
            embed.add_field(name='幣種',value=coin_type,inline=False)
            embed.add_field(name='數量',value=數量,inline=False)
            button=Button(label="確認付款",custom_id="yes",style = discord.ButtonStyle.green)
            button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
            button.callback = give_2
            button2.callback = give_2
            view=View()
            view.add_item(button)
            view.add_item(button2)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.edit_message(view=view,embed=embed)

        user_can_give = []
        if coin_type == "RPG金幣":
            for u in rpg_data:
                if 用戶 in bot.get_user(int(u)).name:
                    user_can_give.append(discord.SelectOption(label=bot.get_user(int(u)).global_name,description=bot.get_user(int(u)).name,value=u))
        else:
            for u in user:
                if bot.get_user(int(u["user_id"])) and 用戶 in bot.get_user(int(u["user_id"])).name:
                    user_can_give.append(discord.SelectOption(label=bot.get_user(int(u["user_id"])).global_name,description=bot.get_user(int(u["user_id"])).name,value=u["user_id"]))
        if len(user_can_give) == 0:
            embed = discord.Embed(title=":x: 無搜尋到的用戶", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name="請確認用戶是否正確喔", value="可能是該用戶尚未註冊",inline=False)
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif len(user_can_give) > 25:
            embed = discord.Embed(title=":x: 可以付款的用戶太多", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name="請提升的ID的精度", value="",inline=False)
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            select = discord.ui.Select(placeholder='選擇要付款的用戶',options=user_can_give)      
            select.callback = give_1
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

@bot.tree.command(name="rpg個人資料",description="查看你的rpg個人資料")
async def pic(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json',encoding='utf-8') as file,open('user.json','r') as file1,open('sign_in.json','r') as file2:
        rpg_data = json.load(file)
        user = json.load(file1)
        sign = json.load(file2)
    bouns_lvl = 0
    check = False
    for entry_ in user:
        if entry_["user_id"] == str(interaction.user.id):
            check = True
            if entry_["lvl"] >= 2:
                bouns_lvl = int(math.log2(entry_["lvl"]))
            break
    if str(interaction.user.id) not in rpg_data:
        check = interaction.user.id
        button=Button(label="4 我是新手",custom_id="yes",style = discord.ButtonStyle.green)
        button2=Button(label="閉嘴 跳過教學",custom_id="no",style = discord.ButtonStyle.red)
        rpg={
            "ephemeral":True,
            "coin":0,
            "equip":{
                "主手":None,
                "副手":None,
                "頭部":None,
                "胸甲":None,
                "護腿":None,
                "靴子":None,
                "首飾":None,
                "戒指":None
            },
            "pt":{
                "金屬":0,
                "布料":0,
                "獸品":0,
                "藥品":0,
                "木材":0,
                "魔素":0
                },
            "ab_value":{
                "STR":0,
                "DEX":0,
                "INT":0,
                "VIT":0,
                "AGI":0,
                "LUK":0
                },
            "state":{
                "HP":100+bouns_lvl,
                "current_hp":100,
                "MP上限":300+bouns_lvl,
                "current_mp":0,
                "ATK":50,
                "物理貫穿":0,
                "MATK":50,
                "魔法貫穿":0,
                "DEF":0,
                "MDEF":0,
                "速度":0,
                "ASPD":50,
                "CSPD":50,
                "暴擊率":0,
                "暴擊傷害":0,
                "穩定率":50,
                "恨意值":100,
                "受到傷害%(減少)":0,
                "等效命中":0,
                "等效防禦":0
                },
            "sp":10 + bouns_lvl,
            "ap":30 + bouns_lvl*2,
            "Lv":1,
            "bouns_Lv":bouns_lvl,
            "sex":None,
            "mainjob":None,
            "supjob":None,
            "merry":None,
            "merry_reward":False,
            "effecting":[],
            "bag":[],
            "mail":[],
            "energy":100
            }
        async def button_callback(interaction):
            custom = interaction.data['custom_id']
            async def on_select_option(interaction):
                rpg["mainjob"] = select1.values[0]
                for i,option in enumerate(main_options,start=0):
                    if select1.values[0] == main_options[i].value:
                        main = main_options[i].label
                        break

                async def on_select_option1(interaction):
                    rpg["supjob"] = select2.values[0]
                    for i,option in enumerate(sup_options,start=0):
                        if select2.values[0] == sup_options[i].value:
                            sup = sup_options[i].label
                            break

                    async def on_select_option2(interaction):
                        rpg["sex"] = select3.values[0]
                        for i,option in enumerate(sex,start=0):
                            if select3.values[0] == sex[i].value:
                                s = sex[i].label
                                break
                        async def on_select_option3(interaction):
                            if interaction.data['custom_id'] == 'accept':
                                rpg_data[str(interaction.user.id)] = rpg
                                embed = discord.Embed(title="登記完成", description="歡迎加入rpg的世界！！",color=randcolor())
                                embed.add_field(name="主職業:", value=main,inline=False)
                                embed.add_field(name="副職業:", value=sup,inline=False)
                                embed.add_field(name="性別:", value=s,inline=False)
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                                sign[str(interaction.user.id)] = {
                                    "state":False,
                                    "continue":False,
                                    "day":0
                                    }
                                await interaction.response.edit_message(content=None,embed=embed,view=None)
                                with open('rpg_data.json','w',encoding='utf-8') as file,open('sign_in.json','w') as file2:
                                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                                    json.dump(sign,file2, indent=4)

                            elif interaction.data['custom_id'] == 'reject':
                                embed = discord.Embed(title="登記取消", description="",color=randcolor())
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
                                await interaction.response.edit_message(content=None,embed=embed,view=None)

                        embed = discord.Embed(title="最終確認", description="確認後就不能更改了喔！",color=randcolor())
                        embed.add_field(name="主職業:", value=main,inline=False)
                        embed.add_field(name="副職業:", value=sup,inline=False)
                        embed.add_field(name="性別:", value=s,inline=False)
                        button3=Button(label="確認",custom_id="accept",style = discord.ButtonStyle.green)
                        button4=Button(label="取消",custom_id="reject",style = discord.ButtonStyle.red)
                        button3.callback = on_select_option3
                        button4.callback = on_select_option3
                        view=View()
                        view.add_item(button3)
                        view.add_item(button4)
                        await interaction.response.edit_message(content=None,embed=embed,view=view)

                    embed = discord.Embed(title="感謝你加入rpg的世界", description="現在 我要為你做一些教學",color=randcolor())
                    embed.add_field(name="", value='很好，看來你已經選好職業了',inline=False)
                    embed.add_field(name="接下來要選擇性別，", value='以下總共有三種性別可以選:',inline=False)
                    embed.add_field(name="", value='- 男性',inline=False)
                    embed.add_field(name="", value='- 女性',inline=False)
                    embed.add_field(name="", value='- ~~扶他~~',inline=False)
                    embed.add_field(name="其中", value='**男性**和**女性**可以結婚\n**同性別**也可以結婚(扶他除外)',inline=False)
                    embed.add_field(name="", value='**扶他**只能和男性與女性其中一方結婚',inline=False)
                    embed.add_field(name="結婚後會有各種能力加成", value='現在，來選擇你的性別吧',inline=False)
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    sex = [
                        discord.SelectOption(label='男性', value='男性',description="可以和男性或女性或扶他結婚"),
                        discord.SelectOption(label='女性', value='女性',description="可以和女性或男性或扶他結婚"),
                        discord.SelectOption(label='扶他', value='扶他',description="可以和男性或女性結婚"),
                        ]
                    select3 =  discord.ui.Select(placeholder='🤰🏿點我選擇性別！', options=sex)
                    view = discord.ui.View(timeout=None)
                    select3.callback = on_select_option2
                    view.add_item(select3)
                    await interaction.response.edit_message(content=None,embed=embed,view=view)

                sup_options = [
                    discord.SelectOption(label='製藥師', value='製藥師',description="可以製作強大的藥品供玩家使用"),
                    discord.SelectOption(label='精煉師', value='精煉師',description="精煉各種裝備，使能力值得到大幅加強"),
                    discord.SelectOption(label='製裝師', value='製裝師',description="可以製作各種裝備"),
                    discord.SelectOption(label='附魔師', value='附魔師',description="消耗大量素材，給裝備附上強大能力"),
                    discord.SelectOption(label='穿孔師', value='穿孔師',description="消耗大量素材，給裝備穿孔"),
                    discord.SelectOption(label='礦工', value='礦工',description="金屬和獸品的主要來源，偶爾會獲得魔素"),
                    discord.SelectOption(label='喜歡伐木的獵人', value='喜歡伐木的獵人',description="布料和木材和藥品的主要來源"),
                    discord.SelectOption(label='合成師', value='合成師',description="解鎖各種合成配方?，用於合成關鍵物品"),
                    discord.SelectOption(label='分解師', value='分解師',description="用於分解材料，獲得額外金幣獎勵"), 
                    ]
                select2 =  discord.ui.Select(placeholder='⚒️點我選擇副職業！', options=sup_options)
                view = discord.ui.View(timeout=None)
                select2.callback = on_select_option1
                view.add_item(select2)
                await interaction.response.edit_message(content=None,view=view)

            main_options = [
                    discord.SelectOption(label='旋風槍', value='旋風槍',description="有著高面板和高速度的優勢"),
                    discord.SelectOption(label='拔刀劍', value='拔刀劍',description="以頻繁無敵而聞名，但是傷害略勝一籌"),
                    discord.SelectOption(label='單手劍', value='單手劍',description="六邊形戰士"),
                    discord.SelectOption(label='雙手劍', value='雙手劍',description="有著全rpg最高的ATK，但是速度如同烏龜"),
                    discord.SelectOption(label='弓', value='弓',description="多段的傷害，使打限傷不再痛苦(速度:中等)"),
                    discord.SelectOption(label='連弩', value='連弩',description="超高機動性的速度，可以創造許多額外回合，以及頻繁的異常狀態(攻擊:低)"),
                    discord.SelectOption(label='法杖', value='法杖',description="大量的MP上限回復優勢，給隊友創造很多機會"),
                    discord.SelectOption(label='拳套', value='拳套',description="超硬身版，全場最盧")
                    ]   
            select1 = discord.ui.Select(placeholder='⚔️點我選擇主職業！', options=main_options)          
            select1.callback = on_select_option           
            view = discord.ui.View(timeout=None)
            view.add_item(select1)
            if custom == "yes" and check == interaction.user.id:
                embed = discord.Embed(title="感謝你加入rpg的世界", description="現在 我要為你做一些教學",color=randcolor())
                embed.add_field(name="首先，這是一個團結性質的rpg\n目標是一起打敗王，取得稀有寶物", value='當然也不免於中間的整裝等...**\n總之，終極目標是取得寶物，獲取大量鮭魚幣！**',inline=False)
                embed.add_field(name="(如果想看詳細流程 可以看下圖: (左上角開始))", value='https://media.discordapp.net/attachments/1154076530792730697/1199229261475745822/rpg.jpg',inline=False)
                embed.add_field(name="接下來是名詞介紹:", value='',inline=False)
                embed.add_field(name="主職業", value='就是後續闖蕩天下的職業！\n請慎選，不同的職業有不同的優勢，要重製需要龐大的代價',inline=False)
                embed.add_field(name="副職業", value='用於生產的職業，產出原料，或是強化裝備等...',inline=False)
                embed.add_field(name="速度", value='用來衡量先攻先守的標準，較快有先攻的機會',inline=False)
                embed.add_field(name="素材", value='民生職業不可或缺的物品，用於各種製作',inline=False)
                embed.add_field(name="", value='現在，來選擇你的職業吧!',inline=False)
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(content=None,embed=embed,view=view)
                

        embed = discord.Embed(title="歡迎來到rpg的世界", description="",color=randcolor())
        embed.add_field(name=f"{interaction.user.display_name}", value='你好，\n看你這樣子，應該是第一次接觸吧?',inline=True)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        button.callback = button_callback
        button2.callback = button_callback
        view=View(timeout=None)
        view.add_item(button)
        view.add_item(button2)
        button2.disabled= True
        embed.color = discord.Colour.dark_blue()
        await interaction.response.send_message(embed=embed , view=view,ephemeral=True)

    else:
        if check and entry_["lvl"] > 0:
            if rpg_data[str(interaction.user.id)]["bouns_Lv"] + int(math.log2(entry_["lvl"])) != rpg_data[str(interaction.user.id)]["bouns_Lv"]:
                rpg_data[str(interaction.user.id)]["sp"] += int(math.log2(entry_["lvl"]))-rpg_data[str(interaction.user.id)]["bouns_Lv"]
                rpg_data[str(interaction.user.id)]["ap"] += (int(math.log2(entry_["lvl"]))-rpg_data[str(interaction.user.id)]["bouns_Lv"])*2
                rpg_data[str(interaction.user.id)]["bouns_Lv"] = int(math.log2(entry_["lvl"]))
        embed = discord.Embed(title="個人資料", description=f"{interaction.user.mention}你的資料如下:",color=randcolor())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.add_field(name="主職業", value=rpg_data[f"{str(interaction.user.id)}"]["mainjob"],inline=False)
        embed.add_field(name="副職業", value=rpg_data[f"{str(interaction.user.id)}"]["supjob"],inline=False)
        embed.add_field(name="角色等級", value=rpg_data[f"{str(interaction.user.id)}"]["Lv"] + rpg_data[f"{str(interaction.user.id)}"]["bouns_Lv"],inline=False)
        embed.add_field(name="性別", value=rpg_data[f"{str(interaction.user.id)}"]["sex"],inline=False)
        embed.add_field(name="能量", value=rpg_data[f"{str(interaction.user.id)}"]["energy"],inline=False)
        if rpg_data[f"{str(interaction.user.id)}"]["merry"] == None:
            embed.add_field(name="婚姻狀態", value="無伴侶",inline=False)
        else:
            embed.add_field(name="婚姻狀態", value=f'已與{bot.get_user(rpg_data[f"{str(interaction.user.id)}"]["merry"]).mention}結婚',inline=False)
 
        if rpg_data[f"{str(interaction.user.id)}"]["ap"] and rpg_data[f"{str(interaction.user.id)}"]["sp"]:
            embed.add_field(name="(提醒)", value=f'有未使用的能力點！！({rpg_data[f"{str(interaction.user.id)}"]["ap"]})\n有未使用的技能點！！({rpg_data[f"{str(interaction.user.id)}"]["sp"]})',inline=False)
        elif rpg_data[f"{str(interaction.user.id)}"]["ap"]:
            embed.add_field(name="(提醒)", value=f'有未使用的能力點！！({rpg_data[f"{str(interaction.user.id)}"]["ap"]})',inline=False)
        elif rpg_data[f"{str(interaction.user.id)}"]["sp"]:
            embed.add_field(name="(提醒)", value=f'有未使用的技能點！！({rpg_data[f"{str(interaction.user.id)}"]["sp"]})',inline=False)

        if len(rpg_data[f"{str(interaction.user.id)}"]["mail"]) != 0:
            embed.add_field(name="(提醒)", value=f'禮物箱有道具未領取！！({len(rpg_data[str(interaction.user.id)]["mail"])})',inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        with open('rpg_data.json','w',encoding='utf-8') as file:
            json.dump(rpg_data,file, indent=4,ensure_ascii=False)
        await interaction.response.send_message(embed=embed,ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

@bot.tree.command(name="查看能力點",description="查看你的能力點數")
async def check_ability(interaction:discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if str(interaction.user.id) in rpg_data:
        user_data = rpg_data[str(interaction.user.id)]
        ab_values = user_data["ab_value"]
        total_points = sum(ab_values.values())

        embed = discord.Embed(title="能力點數", description=f"{interaction.user.mention}你的能力點數如下:",color=randcolor())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        for ability, value in ab_values.items():
            if total_points !=0:
                slash_count = min(int(value / total_points * 10), 10)
            else:
                slash_count = 0
            slash_str = "█" * slash_count
            embed.add_field(name=f'{ability.upper()} {slash_str}', value=value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

    else:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=randcolor())
        embed.add_field(name=f"請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

def update_state(interaction):
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)

    i = rpg_data[str(interaction.user.id)]["state"]
    tmp_ab_value = {}
    index_ab_value = []
    for a,v in rpg_data[str(interaction.user.id)]["ab_value"].items():
        tmp_ab_value.update({a:v})
        index_ab_value.append(a)

    for equip,value in rpg_data[str(interaction.user.id)]["state"].items():
        if equip not in ["current_hp","current_mp"]:
            rpg_data[str(interaction.user.id)]["state"][equip] = 0
        if equip == "恨意值":
            rpg_data[str(interaction.user.id)]["state"][equip] = 100

    for equip,value in rpg_data[str(interaction.user.id)]["equip"].items():
        if value == None:
            continue
        else:
            for v in value["effect"]:
                if v["index"] in index_ab_value and v["type"] == "+":
                    tmp_ab_value[v["index"]] += v["value"]
                elif v["index"] in index_ab_value and v["type"] == "-":
                    tmp_ab_value[v["index"]] -= v["value"]

            for v in value["effect"]:
                if v["index"] in index_ab_value and v["type"] == "x":
                    if v["value"] > 0:
                        tmp_ab_value[v["index"]] = int(tmp_ab_value[v["index"]]*1+v["value"]/100)
                    else:
                        tmp_ab_value[v["index"]] = int(tmp_ab_value[v["index"]]*1+v["value"]/100)

    STR = tmp_ab_value["STR"]
    DEX = tmp_ab_value["DEX"]
    INT = tmp_ab_value["INT"]
    VIT = tmp_ab_value["VIT"]
    AGI = tmp_ab_value["AGI"]
    LUK = tmp_ab_value["LUK"]
    rpg_data[str(interaction.user.id)]["state"]["ATK"] = 50 + int(STR*2) + int(DEX*1.5) +int(AGI*1.2)
    rpg_data[str(interaction.user.id)]["state"]["MATK"] = 50 + int(INT*2) + int(DEX*1.1)
    if rpg_data[str(interaction.user.id)]["equip"]["主手"] is not None:
        if rpg_data[str(interaction.user.id)]["equip"]["主手"]["category"] != '法杖':
            rpg_data[str(interaction.user.id)]["state"]["ATK"] += int(rpg_data[str(interaction.user.id)]["equip"]["主手"]["atk"]*2)
        else:
            rpg_data[str(interaction.user.id)]["state"]["MATK"] += int(rpg_data[str(interaction.user.id)]["equip"]["主手"]["atk"]*3)
    rpg_data[str(interaction.user.id)]["state"]["HP上限"] = 100 + rpg_data[str(interaction.user.id)]["Lv"] + rpg_data[str(interaction.user.id)]["bouns_Lv"] + int(VIT*2)
    rpg_data[str(interaction.user.id)]["state"]["MP上限"] = 300 + rpg_data[str(interaction.user.id)]["Lv"] + rpg_data[str(interaction.user.id)]["bouns_Lv"]
    rpg_data[str(interaction.user.id)]["state"]["速度"] = int(AGI*2)     
    rpg_data[str(interaction.user.id)]["state"]["攻擊MP回復"] = 5 
    rpg_data[str(interaction.user.id)]["state"]["ASPD"] = int(AGI*3)
    rpg_data[str(interaction.user.id)]["state"]["CSPD"] = int(DEX*3) + int(INT*1.2)
    rpg_data[str(interaction.user.id)]["state"]["暴擊率"] = int(LUK/5)
    rpg_data[str(interaction.user.id)]["state"]["暴擊傷害"] = int(LUK/10)
    rpg_data[str(interaction.user.id)]["state"]["穩定率"] = 50 + int(sum(value/10 for value in rpg_data[str(interaction.user.id)]["ab_value"].values()))
   
    for equip, values in rpg_data[str(interaction.user.id)]["equip"].items():
        if values is not None and (equip not in ["主手","副手"]):
            if equip == '胸甲':
                rpg_data[str(interaction.user.id)]["state"]["DEF"] += int(values["def"]*1.5)
                rpg_data[str(interaction.user.id)]["state"]["MDEF"] += int(values["def"]*1.5)
            else:
                rpg_data[str(interaction.user.id)]["state"]["DEF"] += int(values["def"]*1.1)
                rpg_data[str(interaction.user.id)]["state"]["MDEF"] += int(values["def"]*1.1)

    for equip, values in rpg_data[str(interaction.user.id)]["equip"].items():
        if values is not None:
            for v in values["effect"]:
                if v["index"] not in ["INT","VIT","AGI","LUK","STR","DEX"]:
                    if v["type"] == "+":
                        rpg_data[str(interaction.user.id)]["state"][v["index"]] += v["value"]
                    elif v["type"] == "-":
                        rpg_data[str(interaction.user.id)]["state"][v["index"]] -= v["value"]

            for v in values["effect"]:
                if v["index"] not in ["INT","VIT","AGI","LUK","STR","DEX"]:
                    if v["type"] == "x":
                        rpg_data[str(interaction.user.id)]["state"][v["index"]] = int(rpg_data[str(interaction.user.id)]["state"][v["index"]] * ((100 + v["value"]) / 100))

    for drug in rpg_data[str(interaction.user.id)]["effecting"]:
        for effect in drug["effect"]:
            if effect["index"] == "current_hp" or effect["index"] == "current_mp" and effect["index"] == 'x':
                i = effect["index"].replace("current_","").upper()+"上限"
                rpg_data[str(interaction.user.id)]["state"][effect["index"]] = rpg_data[str(interaction.user.id)]["state"][i]*(effect["value"]/100)
            elif effect["type"] == "+" or effect["type"] == "-":
                rpg_data[str(interaction.user.id)]["state"][effect["index"]] = int(rpg_data[str(interaction.user.id)]["state"][effect["index"]]+effect["value"])
            elif effect["type"] == "x":
                rpg_data[str(interaction.user.id)]["state"][effect["index"]] = int(rpg_data[str(interaction.user.id)]["state"][effect["index"]]*((1+effect["value"])/100))

    if rpg_data[str(interaction.user.id)]["state"]["current_hp"] > rpg_data[str(interaction.user.id)]["state"]["HP上限"]:
        rpg_data[str(interaction.user.id)]["state"]["current_hp"] = rpg_data[str(interaction.user.id)]["state"]["HP上限"]
    if rpg_data[str(interaction.user.id)]["state"]["current_hp"] <= 0:
        rpg_data[str(interaction.user.id)]["state"]["current_hp"] = 1

    if rpg_data[str(interaction.user.id)]["state"]["current_mp"] > rpg_data[str(interaction.user.id)]["state"]["MP上限"]:
        rpg_data[str(interaction.user.id)]["state"]["current_mp"] = rpg_data[str(interaction.user.id)]["state"]["MP上限"]
    if rpg_data[str(interaction.user.id)]["state"]["current_mp"] < 0:
        rpg_data[str(interaction.user.id)]["state"]["current_mp"] = 0


    with open('rpg_data.json','w',encoding='utf-8') as file:
        json.dump(rpg_data,file, indent=4,ensure_ascii=False)

@bot.tree.command(name="增加能力點",description="增加你的能力點數")
@app_commands.describe(要加的點數="必須大於0")
async def add_ability(interaction: discord.Interaction,要加的點數:int):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=randcolor())
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif 要加的點數 <= 0:
        embed = discord.Embed(title=":x: 要加的點數不可小於0！", description=f"",color=randcolor())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["ap"] >= 要加的點數:
        async def o(interaction):
            v = select.values[0]
            embed = discord.Embed(title="增加成功！", description=f"{interaction.user.mention}你的能力點數如下:",color=randcolor())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            for ability, value in rpg_data[str(interaction.user.id)]["ab_value"].items():
                if ability == v:
                    embed.add_field(name=f'{ability.upper()}', value=f'{value} {bot.get_emoji(1224919705220026468)} {value+要加的點數}', inline=False)
                else:
                    embed.add_field(name=f'{ability.upper()}', value=value, inline=False)

            rpg_data[str(interaction.user.id)]["ab_value"][v] += 要加的點數
            rpg_data[str(interaction.user.id)]["ap"] -= 要加的點數
            await interaction.response.edit_message(content="",embed=embed,view=None)
            with open('rpg_data.json','w',encoding='utf-8') as file:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)
            update_state(interaction)

        ABILITY = []
        for ab,val in rpg_data[str(interaction.user.id)]["ab_value"].items():
            ABILITY.append(discord.SelectOption(label=ab.upper(),value=ab,description=f'{val} -> {val+要加的點數}'))
        select = discord.ui.Select(placeholder='點我選擇能力點數！', options=ABILITY)          
        select.callback = o           
        view = discord.ui.View(timeout=None)
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)
    else:
        embed = discord.Embed(title="噢噢...你的能力點數不夠", description=f"",color=randcolor())
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name=f'你只有 {rpg_data[str(interaction.user.id)]["ap"]} 點能力點！', value=f'(缺少了 {要加的點數 - rpg_data[str(interaction.user.id)]["ap"]} 點)',inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="pt背包",description="查看pt背包")
async def pt(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    embed = discord.Embed(title="素材倉庫", description=f"{interaction.user.mention} 以下是你的素材倉庫",color=randcolor())
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1096366346763243560.webp")
    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
    index = [[1224925736297693305,'金屬'],[1206653212136964118,'布料'],[1224925724926803978,'獸品'],[1224925700159705128,'藥品'],[1224925712054485087,'木材'],[1224925688482500630,'魔素']]
    for i,value in enumerate(rpg_data[str(interaction.user.id)]["pt"].values()):
        embed.add_field(name=f"{bot.get_emoji(index[i][0])} {index[i][1]}", value=f"{value} / 100000",inline=False)
    await interaction.response.send_message(embed=embed,ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

@bot.tree.command(name="rpg背包",description="查看道具背包")
async def pt(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if len(rpg_data[str(interaction.user.id)]["bag"]) > 0:
        embed = discord.Embed(title=f'背包 ({len(rpg_data[str(interaction.user.id)]["bag"])} / 25)', description=f"{interaction.user.mention} 以下是你的背包",color=randcolor())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988729158601408562/1224952288150294538/stsmall507x507-pad600x600f8f8f8.png?ex=661f5cb8&is=660ce7b8&hm=e704166c81eb16ae670e0cf46eab6ce2409ef2f987377c33b2f644a282f951a5&")
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        for item in rpg_data[str(interaction.user.id)]["bag"]:
            if item["kind"] == "equip":
                xtals = ""
                for i in range(1, 3):
                    if item[f"xtal{i}"] != None:
                        xtals += f'\n鑲嵌孔: {item[f"xtal{i}"]["name"]}  '
                    
                if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    embed.add_field(name=f'({item["category"]}){item["name"]}+{item["refine"]} ATK: {item["atk"]}{xtals}',value=item["des"],inline=False)
                else:
                    embed.add_field(name=f'({item["category"]}){item["name"]}+{item["refine"]} DEF: {item["def"]}{xtals}',value=item["des"],inline=False)
            elif item["des"] != None:
                embed.add_field(name=f'{item["name"]} x {item["per"]}',value=item["des"],inline=False)
            else:
                embed.add_field(name=f'{item["name"]} x {item["per"]}',value='',inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

    elif len(rpg_data[str(interaction.user.id)]["bag"]) == 0:
        embed = discord.Embed(title="背包", description=f"{interaction.user.mention} 以下是你的背包",color=randcolor())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988729158601408562/1224952288150294538/stsmall507x507-pad600x600f8f8f8.png?ex=661f5cb8&is=660ce7b8&hm=e704166c81eb16ae670e0cf46eab6ce2409ef2f987377c33b2f644a282f951a5&")
        embed.add_field(name=f'空空如也',value='',inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

    else:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=randcolor())
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

def item_checks(interaction, item, pt_refuse, item_refuse, rpg_data, idx, recipe):
    pt_check = True
    item_check = True
    item_s = item

    for name, val in recipe.get(rpg_data[str(interaction.user.id)]["supjob"], {}).items():
        if item_s == name:
            for material in val["meterial"]:
                if material["name"] in idx and material["count"] != 0:
                    if rpg_data[str(interaction.user.id)]["pt"][material["name"]] >= material["count"]:
                        rpg_data[str(interaction.user.id)]["pt"][material["name"]] -= material["count"]
                    else:
                        pt_check = False
                        pt_refuse.append((material["name"], f'缺少{material["count"]-rpg_data[str(interaction.user.id)]["pt"][material["name"]]} pt'))
                elif material["count"] != 0:
                    item_exists = False
                    for item in rpg_data[str(interaction.user.id)]["bag"]:
                        if item["name"] == material["name"]:
                            item_exists = True
                            if material["count"] < item["per"]:
                                item["per"] -= material["count"]
                            elif material["count"] == item["per"]:
                                rpg_data[str(interaction.user.id)]["bag"].remove(item)
                            else:
                                item_check = False
                                item_refuse.append((material["name"], f'缺少{material["count"]-item["per"]} 個'))
                    if not item_exists:
                        item_check = False
                        item_refuse.append((material["name"], f'缺少{material["count"]} 個'))
    return pt_check, item_check, pt_refuse, item_refuse

async def bag_check(rpg_data,interaction):
    hour,minute,period = time()
    check = False
    if len(rpg_data[str(interaction.user.id)]["bag"]) >= 25:
        check = True
        embed = discord.Embed(title="噢噢...你的背包已滿！", description=f"",color=discord.Color.red())
        embed.add_field(name="快去整理你的背包！！", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
        return check

@bot.tree.command(name="職業技能",description="使用你的專屬職業技能")
async def skill(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file,open('recipe.json','r',encoding='utf-8') as file1 , open('job.json','r',encoding='utf-8') as file2:
        rpg_data = json.load(file)
        recipe = json.load(file1)
        job = json.load(file2)

    idx = ['藥品','獸品','魔素','木材','布料','金屬']

    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '礦工':
        miner_title = [
            "你正身處礦坑！",
            "你正在深入地底尋找寶藏！",
            "你正在地底挖掘珍貴的礦物！",
            "操！前面沒路了！",
            "你的探照燈正在充電！",
            "你剛剛挖到了鑽石！",
            "你碰到了一大座岩漿湖！",
            "礦坑差一點崩塌！",
            "洞裡有好多蝙蝠！",
            "你正在和其他礦工火拼！",
            "你被大蜘蛛咬了！",
            "你感受著地底深處的黑暗和潮濕"
            ]
        if str(interaction.user.id) in job:
            items = ""
            for item in job[str(interaction.user.id)]["gain"]:
                if item["kind"] == "pt":
                    items += f"{item['name']} {item['per']} pt\n"
                elif item["kind"] == "coin":
                    items += f"{item['name']} {item['per']} s\n"
                elif item["kind"] == "item":
                    items += f"{item['name']} x {item['per']} \n"
                else:
                    items += f"{item['name']}\n"
            if job[str(interaction.user.id)]["time"] == 0:
                embed = discord.Embed(title=':pick: 你的工作結束了！',description='',color=randcolor())
                embed.add_field(name='以下是你獲得的道具',value=items,inline=False)
                total = sum(1 if (i["kind"] != "pt" and i["kind"] != "coin") else 0 for i in job[str(interaction.user.id)]["gain"])
                bag_full = False
                mail_items = 0
                if 50-(len(rpg_data[str(interaction.user.id)]["bag"]) + len(rpg_data[str(interaction.user.id)]["mail"])) >= total:
                    for item in job[str(interaction.user.id)]["gain"]:
                        if item["kind"] == "pt":
                            if rpg_data[str(interaction.user.id)]["pt"][item["name"]] + item["per"] > 100000:
                                rpg_data[str(interaction.user.id)]["pt"][item["name"]] = 100000
                            else:
                                rpg_data[str(interaction.user.id)]["pt"][item["name"]] += item["per"]
                        elif item["kind"] == "coin":
                            rpg_data[str(interaction.user.id)]["coin"] += item["per"]
                        else:
                            if len(rpg_data[str(interaction.user.id)]["bag"]) == 25:
                                bag_full = True
                                taipei_time = datetime.now(taipei_timezone)
                                mail_items += 1
                                user_info = {
                                    "user":"礦工挖礦獎勵",
                                    "time":f"{taipei_time.year}/{taipei_time.month}/{taipei_time.day} {taipei_time.hour}:{taipei_time.minute}"
                                    }
                                item.update(user_info)
                                rpg_data[str(interaction.user.id)]["mail"].append(item)
                            
                            else:
                                rpg_data[str(interaction.user.id)]["bag"].append(item)
                else:
                    embed.add_field(name='',value='你的背包與禮物箱已滿，道具將不匯入。',inline=False)
                if not bag_full:
                    embed.add_field(name='',value='道具已全數匯入背包！',inline=False)
                else:
                    embed.add_field(name='',value=f'背包已滿，共 {mail_items} 個道具進入了禮物箱',inline=False)

                del job[str(interaction.user.id)]
                with open('rpg_data.json','w',encoding='utf-8') as file,open('job.json','w',encoding='utf-8') as file2:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                    json.dump(job,file2, indent=4,ensure_ascii=False)
            else:
                embed = discord.Embed(title=f':pick: {random.choice(miner_title)}',description='',color=randcolor())
                embed.add_field(name='你的工時還剩餘',value=f'`{job[str(interaction.user.id)]["time"]}` 分鐘',inline=False)
                if rpg_data[str(interaction.user.id)]["energy"] > 0:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'(能量充足 產能提升 {rpg_data[str(interaction.user.id)]["energy"]/2} %)',inline=False)
                elif rpg_data[str(interaction.user.id)]["energy"] > -30:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'精力一般',inline=False)
                else:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'(精力不足 產能降低 {rpg_data[str(interaction.user.id)]["energy"]} %\n請補充能量)',inline=False)
                if len(job[str(interaction.user.id)]["gain"]) == 0:
                    embed.add_field(name='獲得的道具',value='無道具',inline=False)
                else:
                    embed.add_field(name='獲得的道具',value=items,inline=False)

            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            async def miner_0(interaction):
                embed = discord.Embed(title=f':pick: 你開始了工作',description='',color=randcolor())
                embed.add_field(name='工時尚餘',value=f'{select.values[0]} 小時')
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(content=None,embed=embed,view=None)
                job[str(interaction.user.id)] = {
                    "luk":rpg_data[str(interaction.user.id)]["ab_value"]["LUK"],
                    "job":rpg_data[str(interaction.user.id)]["supjob"],
                    "fortune":int(select.values[0]),
                    "time":60*int(select.values[0]),
                    "gain":[]
                    }
                with open('rpg_data.json','w',encoding='utf-8') as file,open('job.json','w',encoding='utf-8') as file2:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                    json.dump(job,file2, indent=4,ensure_ascii=False)

            job_time = []
            time_ = [1,2,3,4,5,6,7,8]
            for t in time_:
                job_time.append(discord.SelectOption(label=f'{t}小時',description=f'消耗 {t*12} 點能量',value=t))
            view = discord.ui.View()
            select = discord.ui.Select(placeholder="(礦工)點我選擇工時", options=job_time)      
            select.callback = miner_0
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '喜歡伐木的獵人':
        hunter_title = [
            "你正在伐木中！",
            "你發現一處神秘的森林！",
            "你正在採集珍貴的木材！",
            "你正在和獵物火拼！",
            "你正在叢林裡！",
            "你正在在叢林中尋找隱藏的寶藏！",
            "你正在探索未知的森林地帶！",
            "你正在與叢林中的猛獸進行生死對決！",
            "你差點被獅子咬死！",
            "靠！菸斗沒草了",
            "你剛剛滑倒了！",
            "你遇到了一棵會講話的樹！"
            ]
        if str(interaction.user.id) in job:
            items = ""
            for item in job[str(interaction.user.id)]["gain"]:
                if item["kind"] == "pt":
                    items += f"{item['name']} {item['per']} pt\n"
                elif item["kind"] == "coin":
                    items += f"{item['name']} {item['per']} s\n"
                elif item["kind"] == "item":
                    items += f"{item['name']} x {item['per']} \n"
                else:
                    items += f"{item['name']}\n"
            if job[str(interaction.user.id)]["time"] == 0:
                embed = discord.Embed(title=':axe: 你的工作結束了！',description='',color=randcolor())
                embed.add_field(name='以下是你獲得的道具',value=items,inline=False)
                total = sum(i["per"] if (i["kind"] != "pt" and i["kind"] != "coin") else 0 for i in job[str(interaction.user.id)]["gain"])
                bag_full = False
                mail_items = 0
                if 50-(len(rpg_data[str(interaction.user.id)]["bag"]) + len(rpg_data[str(interaction.user.id)]["mail"])) >= total:
                    for item in job[str(interaction.user.id)]["gain"]:
                        if item["kind"] == "pt":
                            if rpg_data[str(interaction.user.id)]["pt"][item["name"]] + item["per"] > 100000:
                                rpg_data[str(interaction.user.id)]["pt"][item["name"]] = 100000
                            else:
                                rpg_data[str(interaction.user.id)]["pt"][item["name"]] += item["per"]
                        elif item["kind"] == "coin":
                            rpg_data[str(interaction.user.id)]["coin"] += item["per"]
                        elif item["kind"] == "item":
                            check = False
                            for i in rpg_data[str(interaction.user.id)]["bag"]:
                                check = False
                                if i["name"] == item["name"]:
                                    i["per"] += item["per"]
                                    check = True
                                    break

                            if not check:
                                rpg_data[str(interaction.user.id)]["bag"].append(item)
                        else:
                            if len(rpg_data[str(interaction.user.id)]["bag"]) == 25:
                                taipei_time = datetime.now(taipei_timezone)
                                bag_full = True
                                mail_items += 1
                                user_info = {
                                    "user":"伐木/狩獵獎勵",
                                    "time":f"{taipei_time.year}/{taipei_time.month}/{taipei_time.day} {taipei_time.hour}:{taipei_time.minute}"
                                    }
                                item.update(user_info)
                                rpg_data[str(interaction.user.id)]["mail"].append(item)
                            
                            else:
                                rpg_data[str(interaction.user.id)]["bag"].append(item)
                else:
                    embed.add_field(name='',value='你的背包與禮物箱已滿，道具將不匯入。',inline=False)
                if not bag_full:
                    embed.add_field(name='',value='道具已全數匯入背包！',inline=False)
                else:
                    embed.add_field(name='',value=f'背包已滿，共 {mail_items} 個道具進入了禮物箱',inline=False)

                del job[str(interaction.user.id)]
                with open('rpg_data.json','w',encoding='utf-8') as file,open('job.json','w',encoding='utf-8') as file2:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                    json.dump(job,file2, indent=4,ensure_ascii=False)
            else:
                embed = discord.Embed(title=f':axe: {random.choice(hunter_title)}',description='',color=randcolor())
                embed.add_field(name='你的工時還剩餘',value=f'`{job[str(interaction.user.id)]["time"]}` 分鐘',inline=False)
                if rpg_data[str(interaction.user.id)]["energy"] > 0:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'(能量充足 產能提升 {rpg_data[str(interaction.user.id)]["energy"]/2} %)',inline=False)
                elif rpg_data[str(interaction.user.id)]["energy"] > -30:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'精力一般',inline=False)
                else:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'(精力不足 產能降低 {rpg_data[str(interaction.user.id)]["energy"]} %\n請補充能量)',inline=False)
                if len(job[str(interaction.user.id)]["gain"]) == 0:
                    embed.add_field(name='獲得的道具',value='無道具',inline=False)
                else:
                    embed.add_field(name='獲得的道具',value=items,inline=False)

            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            async def miner_0(interaction):
                embed = discord.Embed(title=f':axe: 你開始了工作',description='',color=randcolor())
                embed.add_field(name='工時尚餘',value=f'{select.values[0]} 小時')
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(content=None,embed=embed,view=None)
                job[str(interaction.user.id)] = {
                    "luk":rpg_data[str(interaction.user.id)]["ab_value"]["LUK"],
                    "job":rpg_data[str(interaction.user.id)]["supjob"],
                    "fortune":int(select.values[0]),
                    "time":60*int(select.values[0]),
                    "gain":[]
                    }
                with open('rpg_data.json','w',encoding='utf-8') as file,open('job.json','w',encoding='utf-8') as file2:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                    json.dump(job,file2, indent=4,ensure_ascii=False)

            job_time = []
            time_ = [1,2,3,4,5,6,7,8]
            for t in time_:
                job_time.append(discord.SelectOption(label=f'{t}小時',description=f'消耗 {t*12} 點能量',value=t))
            view = discord.ui.View()
            select = discord.ui.Select(placeholder="(喜歡伐木的獵人)點我選擇工時", options=job_time)      
            select.callback = miner_0
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '合成師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        c = await bag_check(rpg_data,interaction)
        if c:
            return
        async def fusion_0(interaction):
            selects = [select,select1,select2,select3,select4]
            user_pt = rpg_data[str(interaction.user.id)]["pt"]
            for select_find in selects:
                if len(select_find.values) != 0:
                    item = select_find.values[0].split(',')[0]
                    index = select_find.values[0].split(',')[1]
                    break
            embed = discord.Embed(title="是否要合成這個物品？", description=f"",color=randcolor())
            embed.add_field(name="道具名稱", value=item, inline=False)
            embed.add_field(name="道具數量", value=recipe["合成師"][index][item]["per"], inline=False)
            for pt in recipe["合成師"][index][item]["meterial"]:
                if recipe["合成師"][index][item]["kind"] == 'item' or recipe["合成師"][index][item]["kind"] == 'energy':
                    embed.add_field(name=pt["name"],value=f'{pt["count"]}',inline=False)
                else:
                    embed.add_field(name=pt["name"],value=f'{pt["count"]} pt',inline=False)
            button=Button(label="確認",custom_id="yes",style = discord.ButtonStyle.green)
            button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
            async def fusion_1(interaction):
                if interaction.data["custom_id"] == 'yes':
                    check = False
                    item = select_find.values[0].split(',')[0]
                    embed = discord.Embed(title="素材不足！", description=f"",color=discord.Color.red())
                    if item != '濃縮能量棒':
                        for pt in recipe["合成師"][index][item]["meterial"]:
                            if pt["name"] not in ["魔素","藥品","布料","金屬","獸品","木材"]:
                                for i in rpg_data[str(interaction.user.id)]["bag"]:
                                    check = True
                                    if i["name"] == pt["name"] and i["per"] >= pt["per"]:
                                        check = False
                            elif user_pt[pt["name"]] < pt["count"]:
                                check = True
                                embed.add_field(name=pt["name"],value=f'缺少 {pt["count"] - user_pt[pt["name"]]} pt')
                    else:
                        for item_ in rpg_data[str(interaction.user.id)]["bag"]:
                            check = True
                            if item_["name"] in ["熊肉","豬肉","牛肉","羊肉","鴨肉","雞肉"]:
                                check = False
                                if item_["per"] -1 == 0:
                                    rpg_data[str(interaction.user.id)]["bag"].remove(item_)
                                    break
                                else:
                                    item_["per"] -=1
                                    break
                    if check:
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                    else:
                        rpg_data[str(interaction.user.id)]["energy"] -= 10
                        embed = discord.Embed(title="合成成功", description=f"",color=randcolor())
                        embed.add_field(name="道具名稱", value=item, inline=False)
                        embed.add_field(name="道具數量", value=recipe["合成師"][index][item]["per"], inline=False)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                        if item != '濃縮能量棒':
                            for pt in recipe["合成師"][index][item]["meterial"]:
                                if pt not in ["魔素","藥品","布料","金屬","獸品","木材"]:
                                    for i in rpg_data[str(interaction.user.id)]["bag"]:
                                        if i["name"] == pt["name"]:
                                            if i["per"] - pt["per"] == 0:
                                                rpg_data[str(interaction.user.id)]["bag"].remove(i)
                                            else:
                                                i["per"] -= pt["per"]
                                else:
                                    user_pt[pt["name"]] -= pt["count"]

                        check = False
                        for item_find in rpg_data[str(interaction.user.id)]["bag"]:
                            if item_find["name"] == item:
                                item_find["per"] += recipe["合成師"][index][item]["per"]
                                check = True
                                break

                        if not check:
                            if recipe["合成師"][index][item]["kind"] == "item":
                                data = {
                                    "name": item,
                                    "per": recipe["合成師"][index][item]["per"],
                                    "des": recipe["合成師"][index][item]["des"],
                                    "kind": "item",
                                    "effect": None
                                    }
                            elif recipe["合成師"][index][item]["kind"] == "reset":
                                data = {
                                    "name": item,
                                    "per": recipe["合成師"][index][item]["per"],
                                    "des": recipe["合成師"][index][item]["des"],
                                    "kind": "reset",
                                    "effect": None
                                    }
                            elif recipe["合成師"][index][item]["kind"] == "refine":
                                data = {
                                    "name": item,
                                    "per": recipe["合成師"][index][item]["per"],
                                    "des": recipe["合成師"][index][item]["des"],
                                    "refine_pt": recipe["合成師"][index][item]["refine_pt"],
                                    "kind": "refine",
                                    "effect": None
                                    }
                            elif recipe["合成師"][index][item]["kind"] == "sloting":
                                data = {
                                    "name": item,
                                    "per": recipe["合成師"][index][item]["per"],
                                    "des": recipe["合成師"][index][item]["des"],
                                    "slot1_p": recipe["合成師"][index][item]["slot1_p"],
                                    "slot2_p": recipe["合成師"][index][item]["slot2_p"],
                                    "kind": "sloting",
                                    "effect": None
                                    }
                            elif recipe["合成師"][index][item]["kind"] == "extract":
                                 data = {
                                    "name": item,
                                    "per": recipe["合成師"][index][item]["per"],
                                    "des": recipe["合成師"][index][item]["des"],
                                    "kind": "extract",
                                    "effect": None
                                 }
                            elif recipe["合成師"][index][item]["kind"] == "energy":
                                 data = {
                                    "name": item,
                                    "per": recipe["合成師"][index][item]["per"],
                                    "des": recipe["合成師"][index][item]["des"],
                                    "kind": "energy",
                                    "value": recipe["合成師"][index][item]["value"],
                                    "effect": None
                                    }

                            rpg_data[str(interaction.user.id)]["bag"].append(data)

                elif interaction.data["custom_id"] == 'no':
                    embed = discord.Embed(title="合成取消", description="",color=randcolor())
                   
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(content=None,embed=embed,view=None)
                with open('rpg_data.json','w',encoding='utf-8') as file:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)

            view = View()
            button.callback = fusion_1
            button2.callback = fusion_1
            view.add_item(button)
            view.add_item(button2)
            await interaction.response.edit_message(embed=embed,view=view)

        view = discord.ui.View()
        for i,name in enumerate(recipe["合成師"]):
            item_can_fusion = [] 
            for n, item in recipe["合成師"][name].items():
                d = ""
                for des in item["meterial"]:
                    d += f'{des["name"]}x{des["count"]} '
                item_can_fusion.append(discord.SelectOption(label=f'{n} x {item["per"]}', value=f'{n},{name}', description=f'{item["des"]} {d}'))
            if i == 0:
                select = discord.ui.Select(placeholder=name, options=item_can_fusion)      
                select.callback = fusion_0
            elif i == 1:
                select1 = discord.ui.Select(placeholder=name, options=item_can_fusion)      
                select1.callback = fusion_0
            elif i == 2:
                select2 = discord.ui.Select(placeholder=name, options=item_can_fusion)      
                select2.callback = fusion_0
            elif i == 3:
                select3 = discord.ui.Select(placeholder=name, options=item_can_fusion)      
                select3.callback = fusion_0
            elif i == 4:
                select4 = discord.ui.Select(placeholder=name, options=item_can_fusion)      
                select4.callback = fusion_0

        view.add_item(select)
        view.add_item(select1)
        view.add_item(select2)
        view.add_item(select3)
        view.add_item(select4)
        await interaction.response.send_message(view=view, ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '製藥師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        c = await bag_check(rpg_data,interaction)
        if c:
            return
        async def skill1(interaction):
            item_s = select.values[0]
            pt_refuse = []
            item_refuse = []
            pt_check, item_check, pt_refuse, item_refuse = item_checks(interaction, item_s, pt_refuse, item_refuse, rpg_data, idx, recipe)
            for name, val in recipe.get(rpg_data[str(interaction.user.id)]["supjob"], {}).items():
                if item_s == name:
                    if pt_check and item_check:
                        check = False
                        for n in rpg_data[str(interaction.user.id)]["bag"]:
                            if n["name"] == item_s:
                                n["per"] += 1
                                check = True
                                break
                        if not check:
                            if val["kind"] != 'energy':
                                data = {
                                    "name": item_s,
                                    "per": 1,
                                    "des": val["des"],
                                    "kind": val["kind"],
                                    "drug_type":val["drug_type"],
                                    "effect": val["effect"]
                                }
                            else:
                                data = {
                                    "name": item_s,
                                    "per": 1,
                                    "des": val["des"],
                                    "kind": val["kind"],
                                    "drug_type":val["drug_type"],
                                    "value":val["value"],
                                    "effect": val["effect"]
                                }

                            rpg_data[str(interaction.user.id)]["bag"].append(data)

                        rpg_data[str(interaction.user.id)]["energy"] -= 10
                        embed = discord.Embed(title="合成成功！", description=f"合成了:",color=randcolor())
                        embed.add_field(name="道具名稱", value=name, inline=False)
                        embed.add_field(name="道具數量", value='1', inline=False)
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                        await interaction.response.edit_message(content=None, embed=embed, view=None)
                        break
            else:
                embed = discord.Embed(title="合成失敗", description=f"缺少材料:",color=discord.Color.red())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                if pt_check == False:
                    for i in pt_refuse:
                        embed.add_field(name=i[0],value=i[1],inline=False)
                if item_check == False:
                    for i in item_refuse:
                        embed.add_field(name=i[0],value=i[1],inline=False)
                await interaction.response.edit_message(content=None, embed=embed, view=None) 
            with open('rpg_data.json','w',encoding='utf-8') as file:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)
        option = []
        for item_name, item_data in recipe.get(rpg_data[str(interaction.user.id)]["supjob"], {}).items():
            description = ", ".join([f"{material['name']} x {material['count']}" for material in item_data["meterial"]])
            option.append(discord.SelectOption(label=item_name, value=item_name, description=description))
        select = discord.ui.Select(placeholder='(製藥師)點我合成道具！',options=option)      
        select.callback = skill1
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '製裝師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        c = await bag_check(rpg_data,interaction)
        if c:
            return
        async def skill2(interaction):
            item_s = select.values[0]
            pt_refuse = []
            item_refuse = []
            pt_check, item_check, pt_refuse, item_refuse = item_checks(interaction, item_s, pt_refuse, item_refuse, rpg_data, idx, recipe)
            for name, val in recipe.get(rpg_data[str(interaction.user.id)]["supjob"], {}).items():
                if item_s == name:
                    if pt_check and item_check:
                        s_1 = 0
                        for inde in range(10):
                            s_1 += random.uniform(0,0.01)

                        rpg_data[str(interaction.user.id)]["energy"] -= 10
                        embed = discord.Embed(title="合成成功！", description=f"合成了:",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.add_field(name="道具名稱", value=name, inline=False)

                        xtal1 = None
                        xtal2 = None
                        xtal_lottery = random.randint(0,100)
                        if xtal_lottery == 0:
                            xtal1 = {
                                "name":"-",
                                "kind":"xtal",
                                "per":1,
                                "des":None,
                                "effect":None
                                }
                            xtal2 = {
                                "name":"-",
                                "kind":"xtal",
                                "per":1,
                                "des":None,
                                "effect":None
                                }
                            embed.add_field(name="鑲嵌孔", value='+2', inline=False)

                        elif xtal_lottery <= 10:
                            xtal1 = {
                                "name":"-",
                                "kind":"xtal",
                                "per":1,
                                "des":None,
                                "effect":None
                                }
                            embed.add_field(name="鑲嵌孔", value='+1', inline=False)

                        if val["slot"] in [["主手"],["副手"],["主手","副手"]]:
                            data = {
                                "name": item_s,
                                "per": 1,
                                "des": val["des"],
                                "kind": val["kind"],
                                "slot": val["slot"],
                                "xtal1":xtal1,
                                "xtal2":xtal2,
                                "stated":0,
                                "element":None,
                                "category":val["category"],
                                "refine":val["refine"],
                                "refine_pts":0,
                                "atk":int(val["f_atk"]*(1+s_1)+int(s_1)),
                                "f_atk":val["f_atk"],
                                "effect": val["effect"]
                            }
                            embed.add_field(name="ATK", value=f'+{data["atk"]-data["f_atk"]}', inline=False)
                        else:
                            data = {
                                "name": item_s,
                                "per": 1,
                                "des": val["des"],
                                "kind": val["kind"],
                                "slot": val["slot"],
                                "xtal1":xtal1,
                                "xtal2":xtal2,
                                "stated":0,
                                "element":None,
                                "category":val["category"],
                                "refine":val["refine"],
                                "refine_pts":0,
                                "def":int(val["f_def"]*(1+s_1)+int(s_1)),
                                "f_def":val["f_def"],
                                "effect": val["effect"]
                            }
                            embed.add_field(name="DEF", value=f'+{data["def"]-data["f_def"]}', inline=False)
                        rpg_data[str(interaction.user.id)]["bag"].append(data)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                        await interaction.response.edit_message(content=None, embed=embed, view=None)
                            
                    else:
                        embed = discord.Embed(title="合成失敗", description=f"缺少材料:",color=discord.Color.red())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        if pt_check == False:
                            for i in pt_refuse:
                                embed.add_field(name=i[0],value=i[1],inline=False)
                        if item_check == False:
                            for i in item_refuse:
                                embed.add_field(name=i[0],value=i[1],inline=False)
                        await interaction.response.edit_message(content=None, embed=embed, view=None) 
            with open('rpg_data.json','w',encoding='utf-8') as file:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)
        option = []
        for item_name, item_data in recipe.get(rpg_data[str(interaction.user.id)]["supjob"], {}).items():
            description = ", ".join([f"{material['name']} x {material['count']}" for material in item_data["meterial"]])
            option.append(discord.SelectOption(label=item_name, value=item_name, description=description))
        select = discord.ui.Select(placeholder='(製裝師)點我合成裝備！',options=option)      
        select.callback = skill2
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '穿孔師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        check = False
        equip_can_use = []
        for index,item in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if item["kind"] == 'extract' or item["kind"] == 'sloting':
                check = True

            if item["kind"] == "equip":
                num_slots = sum(1 for xtal in [item["xtal1"], item["xtal2"]] if xtal is not None)

                if num_slots < 2:
                    xtals = ""
                    for j in range(1, 3):
                        if item[f"xtal{j}"] is not None and item[f"xtal{j}"] != '-':
                            xtals += f'鑲嵌孔{j}: {item[f"xtal{j}"]["name"]} '

                    if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                        equip_can_use.append(discord.SelectOption(
                            label=f'{item["name"]}+{item["refine"]} (pt:{item["refine_pts"]}) ({item["atk"]})', 
                            value=index, 
                            description=xtals.strip()))
                    else:
                        equip_can_use.append(discord.SelectOption(
                            label=f'{item["name"]}+{item["refine"]} (pt:{item["refine_pts"]}) ({item["def"]})', 
                            value=index, 
                            description=xtals.strip()))

                elif num_slots > 0 and (item["xtal1"]["name"] != '-' or item["xtal2"]["name"] != '-'):
                    xtals = ""
                    for j in range(1, 3):
                        if item[f"xtal{j}"] is not None and item[f"xtal{j}"] != '-':
                            xtals += f'鑲嵌孔{j}: {item[f"xtal{j}"]["name"]} '

                    if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                        equip_can_use.append(discord.SelectOption(
                            label=f'{item["name"]}+{item["refine"]} (pt:{item["refine_pts"]}) ({item["atk"]})', 
                            value=index, 
                            description=xtals.strip()))
                    else:
                        equip_can_use.append(discord.SelectOption(
                            label=f'{item["name"]}+{item["refine"]} (pt:{item["refine_pts"]}) ({item["def"]})', 
                            value=index, 
                            description=xtals.strip()))

        if len(equip_can_use) == 0 or not check:
            embed = discord.Embed(title="沒有可以穿孔的道具", description=f"",color=discord.Color.red())
            embed.add_field(name="請確認你的背包喔！", value="",inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            await interaction.response.send_message(embed=embed,ephemeral=True)

        else:
            async def slot_1(interaction):
                async def slot_2(interaction):
                    async def open_slot_1(interaction):
                        custom = interaction.data["custom_id"]
                        if equip["xtal1"] == None:
                            percent = item["slot1_p"]
                            i = 1
                        else:
                            percent = item["slot2_p"]
                            i = 2

                        if custom == 'yes':
                            rpg_data[str(interaction.user.id)]["energy"] -= 10
                            embed = discord.Embed(title=f'緞造成果',description='',color=randcolor())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            if random.randint(0,100) <= percent:
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                                embed.add_field(name='鑲嵌孔',value=f'{i-1} -> {i}',inline=False)
                                data = {
                                    "name": "-",
                                    "kind": "xtal",
                                    "per":1,
                                    "des":None,
                                    "effect": None
                                }
                                equip[f"xtal{i}"] = data
                                embed.add_field(name='',value='大功告成！',inline=False)
                                
                            else:
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/901687420297314384.webp")
                                embed.add_field(name='鑲嵌孔',value=f'{i-1} -> {i-1}',inline=False)
                                embed.add_field(name='',value='失敗了...',inline=False)

                            if item["per"] - 1 == 0:
                                rpg_data[str(interaction.user.id)].remove(item)
                            else:
                                item["per"] -=1

                        elif custom == 'no':
                            embed = discord.Embed(title=f':warning: 穿孔取消！',description='',color=randcolor())

                        await interaction.response.edit_message(view=None,embed=embed)
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                            json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                    async def extract_1(interaction):
                        async def extract_2(interaction):
                            custom = interaction.data["custom_id"]
                            equip = rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])]
                            if custom == 'yes':
                                rpg_data[str(interaction.user.id)]["energy"] -= 10
                                embed = discord.Embed(title='抽取成果',description='',color=randcolor())
                                embed.add_field(name='抽取成功！',value='',inline=False)
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                embed.add_field(name='',value='大功告成！',inline=False)
                                data = {
                                    "name": "-",
                                    "kind": "xtal",
                                    "per":1,
                                    "des":None,
                                    "effect": None
                                }
                                check = False
                                for i in rpg_data[str(interaction.user.id)]["bag"]:
                                    if i["kind"] == 'equip':
                                        if i["name"] == equip[f"xtal{index}"]["name"]:
                                            i["per"] += 1
                                            check = True
                                            break
                                if not check:
                                    rpg_data[str(interaction.user.id)]["bag"].append(equip[f'xtal{index}'])

                                equip[f"xtal{index}"] = data
                                if item["per"] - 1 == 0:
                                    rpg_data[str(interaction.user.id)].remove(item)
                                else:
                                    item["per"] -=1

                            elif custom == 'no':
                                embed = discord.Embed(title=f':warning: 抽取取消！',description='',color=randcolor())

                            await interaction.response.edit_message(view=None,embed=embed)
                            with open('rpg_data.json','w',encoding='utf-8') as file:
                                json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                        c = await bag_check(rpg_data,interaction)
                        if c:
                            return

                        index = select2.values[0]
                        embed = discord.Embed(title='最終確認',description='確定要抽取這顆緞晶嗎？',color=randcolor())
                        embed.add_field(name='鑲嵌孔'+index,value=equip[f'xtal{index}']["name"])
                        button=Button(label="接受",custom_id="yes",style = discord.ButtonStyle.green)
                        button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                        button.callback = extract_2
                        button2.callback = extract_2
                        view=View()
                        view.add_item(button)
                        view.add_item(button2)
                        await interaction.response.edit_message(view=view,embed=embed)

                    item = rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])]
                    if item["kind"] == 'extract':
                        xtal_can_extract = []
                        if equip["xtal1"] is not None and equip["xtal1"]["name"] != '-':
                            xtal_can_extract.append(discord.SelectOption(label=equip["xtal1"]["name"],description='鑲嵌孔1',value='1'))
                        if equip["xtal2"] is not None and equip["xtal2"]["name"] != '-':
                            xtal_can_extract.append(discord.SelectOption(label=equip["xtal2"]["name"],description='鑲嵌孔2',value='2'))
                        select2 = discord.ui.Select(placeholder='選擇要抽取的欄位',options=xtal_can_extract)      
                        select2.callback = extract_1
                        view = discord.ui.View()
                        view.add_item(select2)
                        await interaction.response.edit_message(view=view)


                    else:
                        embed = discord.Embed(title=f'穿孔確認',description='',color=randcolor())
                        embed.add_field(name=f'將使用的道具：',value=item["name"],inline=False)
                        if equip["xtal1"] == None:
                            embed.add_field(name=f'穿孔成功率(0->1)：',value=f'{item["slot1_p"]}%',inline=False)
                        else:
                            embed.add_field(name=f'穿孔成功率(1->2)：',value=f'{item["slot2_p"]}%',inline=False)
                        if equip["slot"] in [["主手"],["副手"],["主手","副手"]]:
                            embed.add_field(name=f'裝備資訊',value=f'{equip["name"]}+{equip["refine"]} (ATK:{equip["atk"]})',inline=False)
                        else:
                            embed.add_field(name=f'裝備資訊',value=f'{equip["name"]}+{equip["refine"]} (DEF:{equip["def"]})',inline=False)
                        embed.add_field(name=f'裝備能力',value=equip["des"],inline=False)
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')

                        button=Button(label="接受",custom_id="yes",style = discord.ButtonStyle.green)
                        button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                        button.callback = open_slot_1
                        button2.callback = open_slot_1
                        view=View()
                        view.add_item(button)
                        view.add_item(button2)
                        await interaction.response.edit_message(view=view,embed=embed)

                item_can_use = []
                equip = rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])]
                for index,item in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
                    if item["kind"] == 'extract' and equip["xtal1"] is not None:
                        if equip["xtal1"] is not None and (equip["xtal1"]["name"] != '-' or (equip["xtal2"] is not None and equip["xtal2"]["name"] != '-')):
                            item_can_use.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})',description=item["des"],value=index))

                    if item["kind"] == 'sloting':
                        if equip["xtal1"] is None:
                            if item["slot1_p"] is not None:
                                item_can_use.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})',description=f'開啟鑲嵌孔1機率:{item["slot1_p"]}%',value=index))
                        elif equip["xtal2"] is None:
                            if item["slot2_p"] is not None:
                                item_can_use.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})',description=f'開啟鑲嵌孔2機率:{item["slot2_p"]}%',value=index))

                select1 = discord.ui.Select(placeholder='選擇道具',options=item_can_use)      
                select1.callback = slot_2
                view = discord.ui.View()
                view.add_item(select1)
                await interaction.response.edit_message(view=view)

            select = discord.ui.Select(placeholder='(穿孔師)點我穿孔/抽取鍛晶！',options=equip_can_use)      
            select.callback = slot_1
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '精煉師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        equip_can_refine = []
        for index,item in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if item["kind"] == "equip":
                xtals = "鑲嵌孔:"
                count = 0
                for j in range(1, 3):
                    if item[f"xtal{j}"] != None:
                        count += 1
                xtals += str(count)

                if item["refine"] < 20:
                    if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                        equip_can_refine.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]}(pt:{item["refine_pts"]}) ({item["atk"]}) {xtals}', value=index, description=item["des"]))
                    else:
                        equip_can_refine.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]}(pt:{item["refine_pts"]}) ({item["def"]}) {xtals}', value=index, description=item["des"]))
        if len(equip_can_refine) == 0:
            embed = discord.Embed(title="沒有可以精練的裝備", description=f"",color=discord.Color.red())
            embed.add_field(name="請確認你的背包喔！", value="",inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            await interaction.response.send_message(embed=embed,ephemeral=True)

        else:
            async def refine_1(interaction):
                async def refine_2(interaction):
                    before = item["refine"]
                    refine_pt_increase = 550 
                    item["refine_pts"] += rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])]["refine_pt"]

                    final = before

                    while True:
                        total_material_required = final * (final + 1) // 2 * refine_pt_increase + 500
                        if item["refine_pts"] >= total_material_required:
                            final += 1
                        else:
                            break

                    if final > 20:
                        final = 20
                    item["refine"] = final

                    rpg_data[str(interaction.user.id)]["energy"] -= 10
                    embed = discord.Embed(title='強化結果',description='',color=randcolor())
                    embed.add_field(name='精煉值',value=f'{before} -> {final}',inline=False)
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    exter_persent = rpg_data[str(interaction.user.id)]["ab_value"]["LUK"] / 500
                    embed.add_field(name='PT值',value=f'{item["refine_pts"] - rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])]["refine_pt"]} -> {item["refine_pts"]}',inline=False)
                    for i in range(before, final+1):
                        if len(item["effect"]) == 0:
                            break
                        elif i % 5 == 0 and i != 0:
                            idx = random.randint(0, len(item["effect"]) - 1)
                            if "%" not in item["effect"][idx]["index"]:
                                if item["effect"][idx]["value"] >= 0:
                                    num = max(int(item["effect"][idx]["value"] * ( 1.5 + exter_persent)),1)
                                else:
                                    num = 0
                                embed.add_field(name=item["effect"][idx]["index"],value=f'{item["effect"][idx]["value"]} -> {num}',inline=False)
                                item["des"] = item["des"].replace(f'{item["effect"][idx]["index"]}+{item["effect"][idx]["value"]}', f'{item["effect"][idx]["index"]}+{num}')
                                item["effect"][idx]["value"] = num
                            else:
                                if item["effect"][idx]["value"] >= 0:
                                    num = max(int(item["effect"][idx]["value"] * ( 1.5 + exter_persent )),1)
                                else:
                                    num = 0
                                embed.add_field(name=item["effect"][idx]["index"],value=f'{item["effect"][idx]["value"]}% -> {num}%',inline=False)
                                item["des"] = item["des"].replace(f'{item["effect"][idx]["index"]}+{item["effect"][idx]["value"]}%', f'{item["effect"][idx]["index"]}+{num}%')
                                item["effect"][idx]["value"] = num

                    rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])]["per"] -=1
                    if rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])]["per"] == 0:
                        del(rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])])
                    await interaction.response.edit_message(embed=embed,view=None)
                    with open('rpg_data.json','w',encoding='utf-8') as file:
                        json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                item = rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])]
                pts = []
                for i,pt in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
                    if pt["kind"] == "refine":
                        pts.append(discord.SelectOption(label=f'{pt["name"]}({pt["per"]})',value=i,description=pt["des"]))
                if len(pts) == 0:
                    embed = discord.Embed(title="精煉素材不足", description=f"",color=discord.Color.red())
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    embed.add_field(name="再去多賺一點！", value="",inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                    await interaction.response.send_message(embed=embed,ephemeral=True)
                    return

                select1 = discord.ui.Select(placeholder='請選擇要投入的道具',options=pts)      
                select1.callback = refine_2
                view = discord.ui.View()
                view.add_item(select1)
                await interaction.response.edit_message(view=view)

            select = discord.ui.Select(placeholder='(精煉師)點我精煉裝備！',options=equip_can_refine)      
            select.callback = refine_1
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '分解師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        item_break = []
        for index,item in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if item["kind"] == "equip":
                if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    item_break.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]} ({item["atk"]})', value=index, description=item["des"]))
                else:
                    item_break.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]} ({item["def"]})', value=index, description=item["des"]))
        if len(item_break) == 0:
            embed = discord.Embed(title="沒有可以分解的物品", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name="請確認你的背包喔！", value="",inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            await interaction.response.send_message(embed=embed,ephemeral=True)

        else:
            async def item_b(interaction):
                break_items = {}
                items_to_remove = []

                for item in select.values:
                    for met in recipe["製裝師"]:
                        if rpg_data[str(interaction.user.id)]["bag"][int(item)]["name"] == met:
                            for items in recipe["製裝師"][met]["meterial"]:
                                rand_count = random.uniform(0.2, 0.8)
                                if items["name"] in break_items:
                                    break_items[items["name"]] += max(1, int(items["count"] * rand_count))
                                else:
                                    break_items[items["name"]] = max(1, int(items["count"] * rand_count))

                    if len(rpg_data[str(interaction.user.id)]["bag"][int(item)]["effect"]) != 0:
                        mana = random.randint(0,len(rpg_data[str(interaction.user.id)]["bag"][int(item)]["effect"])*1000)
                        if "魔素" in break_items:
                            break_items["魔素"] += mana
                        else:
                            break_items["魔素"] = mana

                    items_to_remove.append(int(item))

                for idx in sorted(items_to_remove, reverse=True):
                    rpg_data[str(interaction.user.id)]["bag"].pop(idx)

                rpg_data[str(interaction.user.id)]["energy"] -= 10
                embed = discord.Embed(title=":white_check_mark: 分解成功！", description=f"以下是分解的材料:",color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                for name,count in break_items.items():
                    embed.add_field(name=f'{name}', value=f'x {count}',inline=False)
                    if name in ["金屬","布料","獸品","藥品","木材","魔素"]:
                        rpg_data[str(interaction.user.id)]["pt"][name] += count
                    else:
                        for item in rpg_data[str(interaction.user.id)]["bag"]:
                            if item["name"] == name:
                                item["per"] += count
                                break
                            else:
                                data = {
                                    "name": name,
                                    "per": count,
                                    "des": "",
                                    "kind": "item",
                                    "effect": None
                                    }
                                rpg_data[str(interaction.user.id)]["bag"].append(data)
                                break

                await interaction.response.edit_message(view=None,embed=embed,content=None)
                with open('rpg_data.json','w',encoding='utf-8') as file:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)

            select = discord.ui.Select(placeholder='(分解師)點我分解裝備！',options=item_break,min_values=1,max_values=len(item_break))      
            select.callback = item_b
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["supjob"] == '附魔師':
        if rpg_data[str(interaction.user.id)]["energy"] <= -90:
            embed = discord.Embed(title='噢噢...你太累了！',description='',color=discord.Color.red())
            embed.add_field(name='請靜待體力回復到-90以上',value='或是使用道具',inline=False)
            await interaction.response.send_message(embed=embed)
            return
        equip_can_stat = []
        for index,equip in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if equip["kind"] == 'equip':
                stated =len(equip["effect"])
                if equip["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    if equip["element"] != None:
                        stated +=1
                if stated < 5 and equip["stated"] <= 5:
                    if equip["slot"] in [["主手"],["副手"],["主手","副手"]]:
                        equip_can_stat.append((discord.SelectOption(label=f'{equip["name"]}+{equip["refine"]} ({equip["atk"]}) (剩餘{5-equip["stated"]}次)', value=index, description=equip["des"])))
                    else:
                        equip_can_stat.append((discord.SelectOption(label=f'{equip["name"]}+{equip["refine"]} ({equip["def"]}) (剩餘{5-equip["stated"]}次)', value=index, description=equip["des"])))
        if len(equip_can_stat) == 0:
            embed = discord.Embed(title="沒有合適附魔的裝備", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name="請確認你的背包喔！", value="",inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            async def stat(interaction):
                index = int(select.values[0])
                item = rpg_data[str(interaction.user.id)]["bag"][index]
                async def stat_1(interaction):
                    async def ele_stat(interaction):
                        custom = interaction.data['custom_id']
                        if custom == 'yes':
                            rpg_data[str(interaction.user.id)]["energy"] -= 10
                            entry = True
                            if random.randint(0,100) <= percent:
                                embed = discord.Embed(title="鍛造結果", description="",color=randcolor())
                                embed.add_field(name=item["name"], value=f'{item["des"]} {select.split(",")[0]}', inline=False)
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                embed.add_field(name='', value='大功告成！', inline=False)
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                                
                            else:
                                b = random.randint(0,1)
                                embed = discord.Embed(title="鍛造結果", description="",color=randcolor())
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                if b:
                                    embed.add_field(name=item["name"], value=f'{item["des"]} {select.split(",")[0]}', inline=False)
                                else:
                                    embed.add_field(name=item["name"], value=f'{item["des"]}', inline=False)
                                    entry = False
                                embed.add_field(name='', value='失敗了...', inline=False)
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/901687420297314384.webp")

                            item["stated"] += 1
                            if entry:
                                item["element"] = select.split(",")[0]
                                item["des"] += f' {select.split(",")[0]}'

                        elif custom == 'no':
                            embed = discord.Embed(title="附魔取消", description="",color=randcolor())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
                            embed.color = discord.Colour.dark_blue()
                        await interaction.response.edit_message(content=None,embed=embed,view=None)
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                    
                    async def norm_stat(interaction):
                        custom = interaction.data['custom_id']
                        if custom == 'yes':
                            rpg_data[str(interaction.user.id)]["energy"] -= 10
                            if random.randint(0,100) <= percent:
                                final_strength = int(select.split(",")[3])
                                des = select.split(",")[0].replace("%","")+"+"+str(final_strength)
                                if "%" in select.split(",")[0]:
                                    des += "%"
                                embed = discord.Embed(title="鍛造結果", description="",color=randcolor())
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                embed.add_field(name=item["name"], value=f'{item["des"]} {des}', inline=False)
                                embed.add_field(name='', value='大功告成！', inline=False)
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                            
                            else:
                                rand_strength_start = random.randint(-int(select.split(",")[3]),int(select.split(",")[3])-1)
                                final_strength = rand_strength_start
                                for test in range(rand_strength_start,int(select.split(",")[3])):
                                    if random.randint(0,100) <= percent:
                                        final_strength = test
                                        break
                                if final_strength >= 0:
                                    des = select.split(",")[0]+"+"+str(final_strength)
                                else:
                                    des = select.split(",")[0]+str(final_strength)
                                if "%" in select.split(",")[0]:
                                    if final_strength >= 0:
                                        des += "%"
                                    else:
                                        des = select.split(",")[0].replace("%","")+str(final_strength)+"%"

                                embed = discord.Embed(title="鍛造結果", description="",color=randcolor())
                                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                                embed.add_field(name=item["name"], value=f'{item["des"]} {des}', inline=False)
                                embed.add_field(name='', value='失敗了...', inline=False)
                                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/901687420297314384.webp")
                            data = {
                                "type": select.split(",")[2],
                                "index": select.split(",")[0],
                                "attribute": select.split(",")[1],
                                "value": final_strength
                                }
                            item["effect"].append(data)
                            item["stated"] += 1
                            if "%" in select.split(",")[0]:
                                if final_strength >= 0:
                                    item["des"] += " "+des
                            else:
                                item["des"] += " "+des

                        elif custom == 'no':
                            embed = discord.Embed(title="附魔取消", description="",color=randcolor())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
                            embed.color = discord.Colour.dark_blue()
                        await interaction.response.edit_message(content=None,embed=embed,view=None)


                        with open('rpg_data.json','w',encoding='utf-8') as file:
                                json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                    async def del_stat(interaction):
                        rpg_data[str(interaction.user.id)]["energy"] -= 10
                        embed = discord.Embed(title="鍛造結果", description="",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.add_field(name=item["name"], value=f'{item["des"].replace(item["element"],"")}', inline=False)
                        embed.add_field(name='', value='大功告成！', inline=False)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1053887019467681812.webp")
                        await interaction.response.edit_message(content=None,embed=embed,view=None)
                        
                        item["stated"] += 1
                        item["des"] = item["des"].replace(item["element"],"")
                        item["element"] = None
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                                json.dump(rpg_data,file, indent=4,ensure_ascii=False)   

                    selects = [select1,select2,select3,select4,select5]
                    percent_list = [100,80,50,30,10]
                    for s in selects:
                        if len(s.values) != 0:
                            select = s.values[0]
                            break
                    length = len(item["effect"])
                    if item.get("element",None) != None:
                        length += 1
                    percent = percent_list[length]
                    button=Button(label="確認附魔",custom_id="yes",style = discord.ButtonStyle.green)
                    button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                    view = View()
                    view.add_item(button)
                    view.add_item(button2)

                    if select == 'delete_element':
                        embed = discord.Embed(title="最終確認", description=f"",color=randcolor())
                        embed.add_field(name=f'{item["name"]}+{item["refine"]} ({item["atk"]})', value=f'{item["des"]}',inline=False)
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.add_field(name=f'能力:', value=f'消除屬性',inline=False)
                        button.callback = del_stat
                        button2.callback = del_stat
                        
                        await interaction.response.edit_message(content=None, embed=embed, view=view)

                    elif select.split(',')[1] == 'ele':
                        if int(rpg_data[str(interaction.user.id)]["pt"][select.split(',')[3]]) >= int(select.split(',')[4]):
                            embed = discord.Embed(title="最終確認", description=f"",color=randcolor())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            if item["slot"] in [["主手"],["副手"],["主手","副手"]]: 
                                embed.add_field(name=f'{item["name"]}+{item["refine"]} ({item["atk"]})', value=f'{item["des"]}',inline=False)
                            else:
                                embed.add_field(name=f'{item["name"]}+{item["refine"]} ({item["def"]})', value=f'{item["des"]}',inline=False)
                            embed.add_field(name=f'能力:', value=f'{select.split(",")[0]}',inline=False)
                            embed.add_field(name=f'機率:', value=f'{percent}%',inline=False)
                        else:
                            embed = discord.Embed(title="噢噢...素材不足", description=f"",color=discord.Color.red())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            embed.add_field(name="缺少了", value=f"{select.split(',')[3]} x {int(select.split(',')[4]) - rpg_data[str(interaction.user.id)]['pt'][select.split(',')[3]]}",inline=False)
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                            view = View()
                        
                        button.callback = ele_stat
                        button2.callback = ele_stat
                        
                        await interaction.response.edit_message(content=None, embed=embed, view=view)

                    else:
                        if "%" in select.split(",")[0]:
                            des = select.split(",")[0].replace("%","")+"+"+select.split(",")[3]+"%"
                        else:
                            des = select.split(",")[0]+"+"+select.split(",")[3]

                        if rpg_data[str(interaction.user.id)]["pt"][select.split(',')[4]] >= int(select.split(',')[5]):
                            embed = discord.Embed(title="最終確認", description=f"",color=randcolor())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            if item["slot"] in [["主手"],["副手"],["主手","副手"]]: 
                                embed.add_field(name=f'{item["name"]}+{item["refine"]} ({item["atk"]})', value=f'{item["des"]}',inline=False)
                            else:
                                embed.add_field(name=f'{item["name"]}+{item["refine"]} ({item["def"]})', value=f'{item["des"]}',inline=False)
                            embed.add_field(name=f'能力:', value=f'{des}',inline=False)
                            embed.add_field(name=f'機率:', value=f'{percent}%',inline=False)
                        else:
                            embed = discord.Embed(title="噢噢...素材不足", description=f"",color=discord.Color.red())
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            embed.add_field(name="缺少了", value=f"{select.split(',')[4]} x {int(select.split(',')[5]) - int(rpg_data[str(interaction.user.id)]['pt'][select.split(',')[4]])}",inline=False)
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                            view = View()

                        button.callback = norm_stat
                        button2.callback = norm_stat
                        await interaction.response.edit_message(embed=embed,view=view)

                embed = discord.Embed(title=':arrow_double_down: 請選擇能力',description='',color=randcolor())
                atk = [#des,stat,value,max
                    ("ATK","atk","+",20,"獸品",10000),("ATK%","atk","x",5,"獸品",30000),("MATK","matk","+",20,"木材",10000),("MATK%","matk","x",5,"木材",30000),("物理貫穿%","p.p.","+",3,"獸品",30000),("魔法貫穿%","m.p.","+",3,"木材",30000),("DEF","def","+",20,"金屬",5000),("DEF%","def","x",5,"金屬",5000),("MDEF","mdef","+",20,"金屬",5000),("MDEF%","mdef","x",5,"金屬",5000)
                    ]
                atk_list = []
                for i in atk:
                    found = False
                    for effect in item["effect"]:
                        if effect["attribute"] == i[1] and effect["type"] == i[2]:
                            found = True
                            break
                    if found:
                        continue
                    atk_list.append(discord.SelectOption(label=f'{i[0]}', value=f'{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{i[5]}', description=f'{i[4]} x {i[5]}  成功最大值:{i[3]}'))

                select1 = discord.ui.Select(placeholder='一般類',options=atk_list)      
                select1.callback = stat_1
                view = discord.ui.View()
                view.add_item(select1)

                c = [
                    ("暴擊率","crit_rate","+",10,"魔素",25000),("暴擊率%","crit_rate","%",5,"魔素",55000),("暴擊傷害","crit_dmg","+",5,"魔素",35000),("暴擊傷害%","crit_dmg","%",2,"魔素",70000)
                    ]
                c_list = []
                for i in c:
                    found = False
                    for effect in item["effect"]:
                        if effect["attribute"] == i[1] and effect["type"] == i[2]:
                            found = True
                            break
                    if found:
                        continue
                    c_list.append(discord.SelectOption(label=f'{i[0]}', value=f'{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{i[5]}', description=f'{i[4]} x {i[5]}  成功最大值:{i[3]}'))
                select2 = discord.ui.Select(placeholder='暴擊類',options=c_list)      
                select2.callback = stat_1
                view.add_item(select2)

                ability = [
                    ("STR","str","+",5,"獸品",3000),("STR%","str","x",2,"獸品",20000),("DEX","dex","+",5,"藥品",3000),("DEX%","dex","x",2,"藥品",20000),("INT","int","+",5,"木材",3000),("INT%","int","x",2,"木材",20000),("VIT","vit","+",5,"金屬",3000),("VIT%","vit","x",2,"金屬",20000),("AGI","agi","+",5,"布料",3000),("AGI%","agi","x",2,"布料",20000),("LUK","luk","+",5,"魔素",3000),("LUK%","luk","x",2,"魔素",20000)
                    ]
                ability_list = []
                for i in ability:
                    found = False
                    for effect in item["effect"]:
                        if effect["attribute"] == i[1] and effect["type"] == i[2]:
                            found = True
                            break
                    if found:
                        continue
                    ability_list.append(discord.SelectOption(label=f'{i[0]}', value=f'{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{i[5]}', description=f'{i[4]} x {i[5]}  成功最大值:{i[3]}'))
                select3 = discord.ui.Select(placeholder='能力類',options=ability_list)      
                select3.callback = stat_1
                view.add_item(select3)

                e = [
                    ("速度","speed","+",10,"布料",10000),("速度%","speed","%",3,"布料",15000),("受到傷害%(減少)","damage","+",2,"魔素",100000),("等效命中","equ_hit","+",10,"藥品",10000),("等效命中%","equ_hit","x",5,"藥品",15000),("等效防禦","equ_def","+",10,"金屬",10000),("等效防禦%","equ_def","x",5,"金屬",15000),("HP上限","HP上限","+",500,"金屬",15000),("HP上限%","HP上限%","x",20,"金屬",75000),("MP上限","MP上限%","+",500,"木材",15000),("MP上限%","MP上限%","x",20,"木材",75000)
                    ]
                e_list = []
                for i in e:
                    found = False
                    for effect in item["effect"]:
                        if effect["attribute"] == i[1] and effect["type"] == i[2]:
                            found = True
                            break
                    if found:
                        continue
                    e_list.append(discord.SelectOption(label=f'{i[0]}', value=f'{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{i[5]}', description=f'{i[4]} x {i[5]}  成功最大值:{i[3]}'))
                select4 = discord.ui.Select(placeholder='特殊效果類',options=e_list)      
                select4.callback = stat_1
                view.add_item(select4)

                if rpg_data[str(interaction.user.id)]["bag"][index]["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    ele = [
                        ("神族","ele",1,"魔素",10000),("魔族","ele",1,"魔素",10000),("人族","ele",1,"魔素",10000),("獸族","ele",1,"魔素",10000),("爬行族","ele",1,"魔素",10000),("不死族","ele",1,"魔素",10000)
                        ]
                    ele_list = []
                    if rpg_data[str(interaction.user.id)]["bag"][index]["element"] != None:
                        ele_list = [discord.SelectOption(label=f'消除屬性(無消耗)', value=f'delete_element', description=f'100%消除附魔 但是會增加附魔次數。')]
                    else:
                        for i in ele:
                            ele_list.append(discord.SelectOption(label=f'{i[0]}', value=f'{i[0]},{i[1]},{i[2]},{i[3]},{i[4]}', description=f'{i[3]} x {i[4]} 成功最大值:{i[2]}'))

                    select5 = discord.ui.Select(placeholder='屬性強化類',options=ele_list)      
                    select5.callback = stat_1
                    view.add_item(select5)
                else:
                    select5 = []

                await interaction.response.edit_message(view=view,embed=embed,content=None)

            select = discord.ui.Select(placeholder='(附魔師)選擇附魔裝備！',options=equip_can_stat)      
            select.callback = stat
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

    else:
        await interaction.response.send_message(ephemeral=True,content='你為什麼沒有職業?')

@bot.tree.command(name="丟棄",description="丟棄背包物品")
@app_commands.describe(數量='要丟棄的數量，必須>0')
async def skill(interaction: discord.Interaction,數量:int):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif 數量 <= 0:
        embed = discord.Embed(title="丟棄的數量不可以小於1！！", description=f"",color=discord.Color.red())
        embed.add_field(name="||~~媽的聽不懂是不是~~||", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        item = []
        for idx,i in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if i["per"] >= 數量:
                if i["kind"] == "equip":
                    xtals = "鑲嵌孔:"
                    count = 0
                    for j in range(1, 3):
                        if i[f"xtal{j}"] != None:
                            count += 1
                    xtals += str(count)

                    if i["slot"] in [["主手"],["副手"],["主手","副手"]]:
                        item.append(discord.SelectOption(label=f'{i["name"]}+{i["refine"]} (ATK : {i["atk"]})\n{xtals}', value=idx,description=i["des"]))
                    else:
                        item.append(discord.SelectOption(label=f'{i["name"]}+{i["refine"]} (DEF : {i["def"]}){xtals}', value=idx,description=i["des"]))

                else:
                    item.append(discord.SelectOption(label=f'{i["name"]}({i["per"]})', value=idx,description=i["des"]))

        if not len(item):#len(item) == 0(False)
            embed = discord.Embed(title=f"沒有合適數量的物品", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name=f"沒有數量大於或等於 `{數量}` 的物品", value="",inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            bag_index = []
            bag = rpg_data[str(interaction.user.id)]["bag"]
            async def trash(interaction):
                async def button_callback(interaction):
                    custom = interaction.data['custom_id']
                    if custom == 'yes':
                        for idx, val in sorted(bag_index, key=lambda x: x[0], reverse=True):
                            if val:
                                bag.remove(bag[idx])
                            else:
                                bag[idx]["per"] -= 數量
                        embed = discord.Embed(title="刪除成功！", description="",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                        embed.color = discord.Colour.green()
                        await interaction.response.edit_message(content=None,embed=embed,view=None)
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                            json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                    elif custom == 'no':
                        embed = discord.Embed(title="刪除取消", description="",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
                        embed.color = discord.Colour.dark_blue()
                        await interaction.response.edit_message(content="",embed=embed,view=None)

                embed = discord.Embed(title=f"確定要丟棄這些道具嗎？", description=f"丟棄後不可回復喔！",color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/597781420408176650.webp')
                for t in select.values:
                    t = int(t)
                    if bag[t]["kind"] == 'equip':
                        xtals = ""
                        for j in range(1, 3):
                            if bag[t][f"xtal{j}"] != None:
                                xtals += f'\n鑲嵌孔: {bag[t][f"xtal{j}"]["name"]}  '

                        if bag[t]["slot"] in [["主手"],["副手"],["主手","副手"]]:
                            embed.add_field(name=f'{bag[t]["name"]}+{bag[t]["refine"]} ATK:{bag[t]["atk"]}{xtals}', value=bag[t]["des"],inline=False)
                        else:
                            embed.add_field(name=f'{bag[t]["name"]}+{bag[t]["refine"]} DEF:{bag[t]["def"]}{xtals}', value=bag[t]["des"],inline=False)
                    else:
                        embed.add_field(name=f'{bag[t]["name"]}({數量})', value=bag[t]["des"],inline=False)
                    if 數量 == bag[t]["per"]:
                        bag_index.append((t,True))
                    else:
                        bag_index.append((t,False))
                view = View()
                button=Button(label="確認",custom_id="yes",style = discord.ButtonStyle.green)
                button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                button.callback = button_callback
                button2.callback = button_callback
                view=View()
                view.add_item(button)
                view.add_item(button2)
                await interaction.response.edit_message(content=None, embed=embed, view=view) 

            select = discord.ui.Select(placeholder='垃圾 垃圾 丟進垃圾桶！',options=item,min_values=1,max_values=len(item))      
            select.callback = trash
            view = discord.ui.View(timeout=None)
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)

@bot.tree.command(name="隱私設定",description="設定部分資訊的隱私狀態")
@app_commands.choices(開關=[
    app_commands.Choice(name="隱私", value="T"),
    app_commands.Choice(name="公開", value="F"),
    ])
@app_commands.describe(開關="設定是否公開")
async def ys(interaction: discord.Interaction,開關: app_commands.Choice[str]):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        embed = discord.Embed(title="設定完成", description=f"",color=randcolor())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        if 開關.value == 'T':
            rpg_data[str(interaction.user.id)]["ephemeral"] = True
            embed.add_field(name="你把狀態設定設成 `隱私`", value="",inline=False)
        elif 開關.value == 'F':
            rpg_data[str(interaction.user.id)]["ephemeral"] = False
            embed.add_field(name="你把狀態設定設成 `公開`", value="",inline=False)

        await interaction.response.send_message(embed=embed,ephemeral=True)
        with open('rpg_data.json','w',encoding='utf-8') as file:
            json.dump(rpg_data,file, indent=4,ensure_ascii=False)

@bot.tree.command(name="錢包",description="查看你有多少錢")
async def skill(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    embed = discord.Embed(title="錢包", description=f"",color=randcolor())
    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
    embed.add_field(name=f'你有 :coin:`{rpg_data[str(interaction.user.id)]["coin"]}`s', value="",inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

@bot.tree.command(name="裝備欄",description="查看你的裝備")
async def equip_list(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        embed = discord.Embed(title="裝備列表", description=f"",color=randcolor())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1206672010575483040/1227070256703340564/OIP.png?ex=6627113b&is=66149c3b&hm=281c50835f55211b3c44d93368f6eeef39afc0b8688e2854712aa47b81791859&')
        for body,equipment in rpg_data[str(interaction.user.id)]["equip"].items():
            if equipment == None:
                embed.add_field(name=f'{body} : 無', value="",inline=False)
            else:
                if equipment["slot"] not in [["主手"],["副手"],["主手","副手"]]:
                    embed.add_field(name=f'{body} : {equipment["name"]}+{equipment["refine"]} DEF:{equipment["def"]}', value='',inline=False)
                else:
                    embed.add_field(name=f'{body} : ({equipment["category"]}){equipment["name"]}+{equipment["refine"]} ATK:{equipment["atk"]}', value='',inline=False)
    
        await interaction.response.send_message(embed=embed, ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

@bot.tree.command(name="穿裝備",description="穿上裝備")
@app_commands.choices(部位=[
    app_commands.Choice(name="主手", value="主手"),
    app_commands.Choice(name="副手", value="副手"),
    app_commands.Choice(name="頭部", value="頭部"),
    app_commands.Choice(name="胸甲", value="胸甲"),
    app_commands.Choice(name="護腿", value="護腿"),
    app_commands.Choice(name="靴子", value="靴子"),
    app_commands.Choice(name="首飾", value="首飾"),
    app_commands.Choice(name="戒指", value="戒指"),
    ])
@app_commands.describe(部位="要穿的部位")
async def equip(interaction: discord.Interaction,部位: app_commands.Choice[str]):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        rule = [("單手劍","單手劍"),("弓","拔刀劍")]
        l = []
        if rpg_data[str(interaction.user.id)]["equip"][部位.value] != None:
            l.append(discord.SelectOption(label='脫掉裝備', value='dequip',description=''))

        for index,e in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if e["kind"] == "equip":
                if 部位.value in e["slot"]:
                    if 部位.value == "副手":
                        if rpg_data[str(interaction.user.id)]["equip"]["主手"] != None:
                            for r in rule:
                                if rpg_data[str(interaction.user.id)]["equip"]["主手"]["category"] == r[0] and e["category"] == r[1]:
                                    l.append(discord.SelectOption(label=f'{e["name"]}+{e["refine"]} ({e["atk"]})', value=index,description=e["des"]))
                                    break
                        else:
                            embed = discord.Embed(title="沒有可以穿的裝備", description=f"",color=discord.Color.red())
                            embed.add_field(name="請先穿戴主手武器", value="",inline=False)
                            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                            await interaction.response.send_message(embed=embed,ephemeral=True)
                            return

                    else:
                        if e["slot"] in [["主手"],["副手"],["主手","副手"]] and e["category"] == rpg_data[str(interaction.user.id)]["mainjob"]:
                            l.append(discord.SelectOption(label=f'{e["name"]}+{e["refine"]} ({e["atk"]})', value=index,description=e["des"]))
                        elif e["slot"] not in [["主手"],["副手"],["主手","副手"]]:
                            l.append(discord.SelectOption(label=f'{e["name"]}+{e["refine"]} ({e["def"]})', value=index,description=e["des"]))
        if len(l) == 0:
            embed = discord.Embed(title="沒有可以穿的裝備", description=f"",color=discord.Color.red())
            embed.add_field(name="請確認你的背包喔！", value="",inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            await interaction.response.send_message(embed=embed,ephemeral=True)

        else:
            async def equip1(interaction):
                if select.values[0] == 'dequip':
                    rpg_data[str(interaction.user.id)]["bag"].append(rpg_data[str(interaction.user.id)]["equip"][部位.value])
                    rpg_data[str(interaction.user.id)]["equip"][部位.value] = None
                    if rpg_data[str(interaction.user.id)]["equip"]["副手"] != None:
                        rpg_data[str(interaction.user.id)]["bag"].append(rpg_data[str(interaction.user.id)]["equip"]["副手"])
                        rpg_data[str(interaction.user.id)]["equip"]["副手"] = None
                    embed = discord.Embed(title=":white_check_mark: 脫裝成功", description=f"",color=randcolor())

                elif rpg_data[str(interaction.user.id)]["equip"][部位.value] != None:
                    rpg_data[str(interaction.user.id)]["bag"].append(rpg_data[str(interaction.user.id)]["equip"][部位.value])
                    rpg_data[str(interaction.user.id)]["equip"][部位.value] = rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])]
                    rpg_data[str(interaction.user.id)]["bag"].remove(rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])])
                    embed = discord.Embed(title=":white_check_mark: 裝備成功", description=f"",color=randcolor())

                else:
                    rpg_data[str(interaction.user.id)]["equip"][部位.value] = rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])]
                    rpg_data[str(interaction.user.id)]["bag"].remove(rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])])
                    embed = discord.Embed(title=":white_check_mark: 裝備成功", description=f"",color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(embed=embed,view=None,content=None)
                with open('rpg_data.json','w',encoding='utf-8') as file:
                    json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                update_state(interaction)
        
            embed = discord.Embed(title=f"目前你的{部位.value}資訊", description=f"",color=randcolor())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            if rpg_data[str(interaction.user.id)]["equip"][部位.value] == None:
                embed.add_field(name="無裝備", value="",inline=False)
            else:
                if rpg_data[str(interaction.user.id)]["equip"][部位.value]["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    embed.add_field(name=f'({rpg_data[str(interaction.user.id)]["equip"][部位.value]["category"]}){rpg_data[str(interaction.user.id)]["equip"][部位.value]["name"]}+{rpg_data[str(interaction.user.id)]["equip"][部位.value]["refine"]}', value=f'ATK : {rpg_data[str(interaction.user.id)]["equip"][部位.value]["atk"]}',inline=False)
                else:
                        embed.add_field(name=f'{rpg_data[str(interaction.user.id)]["equip"][部位.value]["name"]}+{rpg_data[str(interaction.user.id)]["equip"][部位.value]["refine"]}', value=f'DEF : {rpg_data[str(interaction.user.id)]["equip"][部位.value]["def"]}',inline=False)
            select = discord.ui.Select(placeholder='選擇要穿的裝備',options=l)      
            select.callback = equip1
            view = discord.ui.View(timeout=None)
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True,embed=embed)

@bot.tree.command(name="禮物箱領取",description="領取道具")
async def mail_take(interaction: discord.Interaction):
    hour,minute,period = time()
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    gift = rpg_data[str(interaction.user.id)]["mail"]

    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    c = await bag_check(rpg_data,interaction)
    if c:
        return

    elif len(gift) == 0:
        embed = discord.Embed(title="你的禮物箱 (0 / 25)", description=f"",color=randcolor())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="空空如也", value="",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        async def take_gift_1(interaction):
            bag = rpg_data[str(interaction.user.id)]["bag"]
            index = 0
            items = []
            for i in select.values:
                check = False
                for t in bag:
                    if rpg_data[str(interaction.user.id)]["mail"][int(i)]["kind"] == "pt":
                        break
                    elif rpg_data[str(interaction.user.id)]["mail"][int(i)]["name"] == t["name"]:
                        check = True
                        break
                if not check and rpg_data[str(interaction.user.id)]["mail"][int(i)]["name"] not in items:
                    if rpg_data[str(interaction.user.id)]["mail"][int(i)]["kind"] != 'equip':
                        items.append(rpg_data[str(interaction.user.id)]["mail"][int(i)]["name"])
                    index += 1
            if index > 25 - len(bag):
                embed = discord.Embed(title="你的背包裝不下了！", description=f"",color=discord.Color.red())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                embed.add_field(name="請先整理你的背包喔！", value="",inline=False)
                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
                await interaction.response.edit_message(embed=embed,view=None)
            else:
                embed = discord.Embed(title="",description=f':white_check_mark: 已領取共 {len(select.values)} 個物品',color=randcolor())
                await interaction.response.edit_message(embed=embed,view=None)
                for i in sorted(select.values,reverse=True):
                    item = rpg_data[str(interaction.user.id)]["mail"][int(i)]
                    if item["kind"] == "pt":
                        rpg_data[str(interaction.user.id)]["pt"][item["name"]] += item["per"]
                        if rpg_data[str(interaction.user.id)]["pt"][item["name"]] > 100000:
                            rpg_data[str(interaction.user.id)]["pt"][item["name"]] = 100000
                        gift.remove(gift[int(i)])
                    elif item["kind"] == 'equip':
                        del item["user"]
                        del item["time"]
                        bag.append(item)
                        gift.remove(gift[int(i)])
                    else:
                        check = False
                        for j in bag:
                            if item["name"] == j["name"]:
                                j["per"] += item["per"]
                                check = True
                                break
                        if not check:
                            del item["user"]
                            del item["time"]
                            bag.append(item)
                        gift.remove(gift[int(i)])

            with open('rpg_data.json','w',encoding='utf-8') as file:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)

        gift_list = []
        embed = discord.Embed(title=f"你的禮物箱 ({len(gift)} / 25)", description=f"",color=randcolor())
        for index,item in enumerate(gift):
            if item["kind"] == 'equip':
                if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    gift_list.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]} ATK:{item["atk"]}',value=index,description=f'來自{item["user"]}的物品 {item["time"]}'))
                    embed.add_field(name=f'{item["name"]}+{item["refine"]} ATK:{item["atk"]}',value=item["des"],inline=False)
                else:
                    gift_list.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]} DEF:{item["def"]}',value=index,description=f'來自{item["user"]}的物品 {item["time"]}'))
                    embed.add_field(name=f'{item["name"]}+{item["refine"]} DEF:{item["def"]}',value=item["des"],inline=False)
            else:
                gift_list.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})',value=index,description=f'來自{item["user"]}的物品 {item["time"]}'))
                embed.add_field(name=f'{item["name"]} x {item["per"]}',value=item["des"],inline=False)

        select = discord.ui.Select(placeholder='選擇要領取的物品！(素材溢出將刪除)',options=gift_list,min_values=1,max_values=len(gift_list))      
        select.callback = take_gift_1
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True,embed=embed)

@bot.tree.command(name="寄送道具",description="寄送一種道具")
@app_commands.choices(種類=[
    app_commands.Choice(name="道具", value="道具"),
    app_commands.Choice(name="素材PT", value="素材PT"),
    ])
@app_commands.describe(種類="選擇一個種類",數量="要寄送的數量",用戶名稱="輸入用戶的ID(可簡短輸入)")
async def equip(interaction: discord.Interaction,數量:int,種類: app_commands.Choice[str],用戶名稱:str):
    hour,minute,period = time()
    user_id = 0

    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    user_list = []
    for user in rpg_data:
        try:
            if 用戶名稱 in bot.get_user(int(user)).name and bot.get_user(int(user)).id != interaction.user.id:
                user_list.append(discord.SelectOption(label=bot.get_user(int(user)).global_name, value=user,description=bot.get_user(int(user)).name))
        except AttributeError:
            continue

    gift_list = []
    if 種類.value == "道具":
        for index,item in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
            if item["kind"] == 'equip' and 數量 == 1:
                if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                    gift_list.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]} ATK:{item["atk"]}',description=item["des"],value=index))
                else:
                    gift_list.append(discord.SelectOption(label=f'{item["name"]}+{item["refine"]} DEF:{item["def"]}',description=item["des"],value=index))
            elif item["kind"] != "equip" and item["per"] >= 數量:
                gift_list.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})',description=item["des"],value=index))

    else:
        for pt in rpg_data[str(interaction.user.id)]["pt"]:
            if rpg_data[str(interaction.user.id)]["pt"][pt] >= 數量:
                gift_list.append(discord.SelectOption(label=pt,description=f'剩餘 {rpg_data[str(interaction.user.id)]["pt"][pt]}',value=pt))

    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    elif len(gift_list) == 0:
        embed = discord.Embed(title=":x: 沒有符合條件的物品", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請確認道具數量喔", value="",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif 數量 < 1:
        embed = discord.Embed(title="寄送的數量不可以小於1", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請重新輸入正確的數字", value="",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif len(user_list) == 0:
        embed = discord.Embed(title=":x: 找不到適合的用戶！", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請確認輸入的ID是否正確", value="",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif len(user_list) > 25:
        embed = discord.Embed(title=":x: 尋找到的用戶太多！", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請提升的ID的精度", value="",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        async def mail_1(interaction):
            async def mail_2(interaction):
                async def mail_3(interaction):
                    custom = interaction.data["custom_id"]
                    if custom == 'yes':
                        taipei_time = datetime.now(taipei_timezone)
                        user_info = {
                            "user":interaction.user.name,
                            "time":f"{taipei_time.year}/{taipei_time.month}/{taipei_time.day} {taipei_time.hour}:{taipei_time.minute}"
                            }
                        embed = discord.Embed(title="寄送成功",description='已寄送給',color=randcolor())
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                        embed.add_field(name=bot.get_user(int(user_id)).global_name,value=bot.get_user(int(user_id)).name,inline=False)
                        await interaction.response.edit_message(embed=embed,view=None)
                        if 種類.value == "道具":
                            tmp = item["per"] - 數量
                            item["per"] = 數量
                            item.update(user_info)
                            rpg_data[user_id]["mail"].append(item)
                            if tmp == 0:
                                rpg_data[str(interaction.user.id)]["bag"].remove(item)
                            else:
                                item["per"] = tmp
                        else:
                            data = {
                                "name":select1.values[0],
                                "kind":"pt",
                                "per":數量,
                                "des":"",
                                "user":interaction.user.name,
                                "time":f"{taipei_time.year}/{taipei_time.month}/{taipei_time.day} {taipei_time.hour}:{taipei_time.minute}"
                                }
                            rpg_data[user_id]["mail"].append(data)
                            rpg_data[str(interaction.user.id)]["pt"][select1.values[0]] -= 數量
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                            json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                    elif custom == 'no':
                        embed = discord.Embed(title="寄送取消",description='',color=randcolor())
                        await interaction.response.edit_message(embed=embed,view=None)

                embed = discord.Embed(title="最終確認",description='以下是你要寄送的物品：',color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                if 種類.value == "道具":
                    item = rpg_data[str(interaction.user.id)]["bag"][int(select1.values[0])]
                    if item["kind"] == "equip":
                        if item["slot"] in [["主手"],["副手"],["主手","副手"]]:
                            embed.add_field(name=f'{item["name"]}+{item["refine"]} ATK:{item["atk"]}',value=item["des"],inline=False)
                        else:
                            embed.add_field(name=f'{item["name"]}+{item["refine"]} DEF:{item["def"]}',value=item["des"],inline=False)
                    elif item["kind"] == "item" or item["kind"] == "energy":
                        embed.add_field(name=f'{item["name"]}x{數量}',value=item["des"],inline=False)
                    else:
                        embed.add_field(name=f'{item["name"]}x{數量} pt',value=item["des"],inline=False)
                else:
                    pt = rpg_data[str(interaction.user.id)]["pt"][select1.values[0]]
                    embed.add_field(name=select1.values[0],value=數量,inline=False)

                button=Button(label="寄送",custom_id="yes",style = discord.ButtonStyle.green)
                button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                button.callback = mail_3
                button2.callback = mail_3
                view=View()
                view.add_item(button)
                view.add_item(button2)
                await interaction.response.edit_message(view=view,embed=embed)

            user_id = select.values[0]
            if len(rpg_data[user_id]["mail"]) == 25:
                embed = discord.Embed(title=":x: 該用戶信箱已滿", description=f"",color=discord.Color.red())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                embed.add_field(name="叫他清信箱", value="",inline=False)
                await interaction.response.edit_message(embed=embed,ephemeral=True)
            else:
                select1 = discord.ui.Select(placeholder='選擇一個物品',options=gift_list)      
                select1.callback = mail_2
                view = discord.ui.View()
                view.add_item(select1)
                await interaction.response.edit_message(view=view)
            
        select = discord.ui.Select(placeholder='選擇一個用戶',options=user_list)      
        select.callback = mail_1
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)

@bot.tree.command(name="結婚",description="與某人結婚")
@app_commands.describe(用戶名稱="輸入用戶的ID(可簡短輸入)")
async def equip(interaction: discord.Interaction,用戶名稱:str):
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)

    hour,minute,period = time()

    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
        return

    if rpg_data[str(interaction.user.id)]["merry"] != None:
        embed = discord.Embed(title="你已經有伴侶了！", description="",color=discord.Color.red())
        embed.add_field(name="如果要和其他人結婚 請先使用 /離婚", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        await interaction.response.send_message(content=None,embed=embed,ephemeral=True)

    else:
        user_can_merry = []
        i = interaction.user.id
        for user in rpg_data:
            if 用戶名稱 in bot.get_user(int(user)).name and int(user) != interaction.user.id and not (rpg_data[str(interaction.user.id)]["sex"] == "扶他" and rpg_data[str(user)]["sex"] == "扶他") and rpg_data[user]["merry"] is None:
                user_can_merry.append(discord.SelectOption(label=f'{bot.get_user(int(user)).global_name} ({rpg_data[user]["sex"]})',description=bot.get_user(int(user)).name,value=int(user)))
        if len(user_can_merry) == 0:
            embed = discord.Embed(title=":x: 沒有適和結婚的人", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name="請確認用戶是否正確喔", value="",inline=False)
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif len(user_can_merry) > 25:
            embed = discord.Embed(title=":x: 可以結婚的用戶太多", description=f"",color=discord.Color.red())
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            embed.add_field(name="請提升的ID的精度", value="",inline=False)
            await interaction.response.send_message(embed=embed,ephemeral=True)
            
        else:
            async def merry_1(interaction):
                async def merry_2(interaction):
                    custom = interaction.data["custom_id"]
                    if custom == "yes":
                        rpg_data[str(i)]["merry"] = user_id
                        rpg_data[str(user_id)]["merry"] = i
                        embed = discord.Embed(title=f"`{bot.get_user(user_id).global_name}` 接受了你的求婚！！", description=f"",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        await bot.get_user(i).send(embed=embed,view=None)
                        embed = discord.Embed(title=f"你現在跟 `{bot.get_user(i).global_name}` 是伴侶了！", description=f"",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        await m.delete()
                        await bot.get_user(user_id).send(view=view,embed=embed)
                        embed = discord.Embed(title=f":partying_face:", description=f"",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.add_field(name=f'{bot.get_user(i).global_name}({rpg_data[str(i)]["sex"]}) 和 {interaction.user.global_name}({rpg_data[str(user_id)]["sex"]}) 結婚了！', value="",inline=False)
                        await bot.get_channel(c).send(view=view,embed=embed)
                        embed = discord.Embed(title=f"獲得新的獎勵！", description=f"",color=randcolor())
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        embed.add_field(name=f"由於是第一次結婚 系統將給你：", value="",inline=False)
                        embed.add_field(name=":coin:`1000` s 作為獎勵", value="",inline=False)
                        if not rpg_data[str(i)]["merry_reward"]:
                            await bot.get_user(i).send(embed=embed,view=None)
                            rpg_data[str(i)]["merry_reward"] = True
                            rpg_data[str(i)]["coin"] += 1000
                        if not rpg_data[str(interaction.user.id)]["merry_reward"]:
                            await interaction.user.send(embed=embed,view=None)
                            rpg_data[str(interaction.user.id)]["merry_reward"] = True
                            rpg_data[str(interaction.user.id)]["coin"] += 1000

                        with open('rpg_data.json','w',encoding='utf-8') as file:
                            json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                    elif custom == "no":
                        embed = discord.Embed(title=f":cry: `{bot.get_user(user_id)}` 拒絕了你的求婚", description=f"",color=randcolor())
                        await bot.get_user(i).send(embed=embed,view=None)
                        embed = discord.Embed(title=f":white_check_mark: 成功拒絕了求婚", description=f"",color=randcolor())
                        await m.delete()
                        await bot.get_user(user_id).send(view=view,embed=embed)

                user_id = int(select.values[0])
                embed = discord.Embed(title=f"是否接受 `{interaction.user.global_name}` 的求婚？", description=f"",color=randcolor())
                try:
                    embed.add_field(name=f"(求婚來自群組：`{interaction.user.guild.name}`)", value="",inline=False)
                except:
                    embed.add_field(name=f"(求婚來自機器人私訊)", value="",inline=False)
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                button=Button(label="接受",custom_id="yes",style = discord.ButtonStyle.green)
                button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                button.callback = merry_2
                button2.callback = merry_2
                view=View(timeout=None)
                view.add_item(button)
                view.add_item(button2)
                m = await bot.get_user(user_id).send(view=view,embed=embed)
                view=View(timeout=None)
                embed = discord.Embed(title=f":white_check_mark: 求婚成功！", description=f"",color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                embed.add_field(name=f"請等待 `{bot.get_user(user_id).global_name}` 的回應", value="",inline=False)
                await interaction.response.edit_message(view=view,embed=embed)
                c = interaction.channel.id

            select = discord.ui.Select(placeholder='選擇要結婚的用戶',options=user_can_merry)      
            select.callback = merry_1
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view,ephemeral=True)
            
@bot.tree.command(name="離婚",description="與伴侶離婚")
async def lihun(interaction: discord.Interaction):
    with open('rpg_data.json','r',encoding='utf-8') as file,open('dismerry.json','r') as file1:
        rpg_data = json.load(file)
        dismerry = json.load(file1)

    hour,minute,period = time()

    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif rpg_data[str(interaction.user.id)]["merry"] == None:
        embed = discord.Embed(title="你還沒有伴侶！", description="",color=randcolor())
        embed.add_field(name="如果要和其他人離婚 請先使用 /結婚", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        await interaction.response.send_message(content=None,embed=embed,ephemeral=True)

    elif str(interaction.user.id) in dismerry:
        if dismerry[str(interaction.user.id)]["day"] >= 3:
            embed = discord.Embed(title="你們離婚了！(日期已超過3天)", description="",color=randcolor())
            embed.add_field(name=f"你恢復了單身", value="",inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await bot.get_user(rpg_data[str(interaction.user.id)]["merry"]).send(embed=embed)
            rpg_data[str(interaction.user.id)]["merry"] = None
            rpg_data[rpg_data[str(interaction.user.id)]["merry"]]["merry"] = None
            with open('rpg_data.json','w',encoding='utf-8') as file:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)

        else:
            embed = discord.Embed(title="你正在等待回應！", description="",color=randcolor())
            embed.add_field(name=f'目前等待天數: {dismerry[str(interaction.user.id)]["day"]}', value="",inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        async def dismerry_1(interaction):
            async def dismerry_2(interaction):
                custom = interaction.data["custom_id"]
                if custom == 'yes':
                    embed = discord.Embed(title="你們離婚了！", description="",color=randcolor())
                    embed.add_field(name=f"你恢復了單身", value="",inline=False)
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    await interaction.message.delete()
                    await interaction.user.send(view=None,embed=embed)
                    await self_user.send(view=None,embed=embed)
                    rpg_data[str(interaction.user.id)]["merry"] = None
                    rpg_data[str(self_user.id)]["merry"] = None
                    del dismerry[str(self_user.id)]
                    with open('rpg_data.json','w',encoding='utf-8') as file,open('dismerry.json','w') as file1:
                        json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                        json.dump(dismerry,file1, indent=4)
                    
                elif custom == 'no':
                    embed = discord.Embed(title=":white_check_mark: 離婚請求已拒絕", description="",color=randcolor())
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    await interaction.response.edit_message(view=None,embed=embed)
                    await interaction.message.delete()
                    await interaction.user.send(view=None,embed=embed)
                    embed = discord.Embed(title="你的伴侶拒絕了你的離婚請求！", description="",color=randcolor())
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    await self_user.send(view=None,embed=embed)
                    del dismerry[str(self_user.id)]
                    with open('dismerry.json','w') as file1:
                        json.dump(dismerry,file1, indent=4)

            custom = interaction.data["custom_id"]
            if custom == 'yes':
                data = {
                    "day":0
                    }
                dismerry[str(interaction.user.id)] = data
                with open('dismerry.json','w') as file1:
                    json.dump(dismerry,file1, indent=4)

                embed = discord.Embed(title=":white_check_mark: 離婚請求已提出", description="",color=randcolor())
                embed.add_field(name=f"請等待對方接受(或是等待3天)", value="",inline=False)
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(view=None,embed=embed)
                embed = discord.Embed(title="您的伴侶提出了離婚！", description="",color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                button=Button(label="接受",custom_id="yes",style = discord.ButtonStyle.green)
                button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
                button.callback = dismerry_2
                button2.callback = dismerry_2
                view=View(timeout=None)
                view.add_item(button)
                view.add_item(button2)
                await user.send(embed=embed,view=view)
            elif custom == 'no':
                embed = discord.Embed(title=":white_check_mark: 離婚請求已取消", description="",color=randcolor())
                embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                await interaction.response.edit_message(view=None,embed=embed)

        self_user = interaction.user
        user = bot.get_user(rpg_data[str(interaction.user.id)]["merry"])
        embed = discord.Embed(title="確定要離婚嗎？", description="",color=randcolor())
        embed.add_field(name=f"你將跟 `{user.global_name}` 離婚", value="",inline=False)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        button=Button(label="接受",custom_id="yes",style = discord.ButtonStyle.green)
        button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
        button.callback = dismerry_1
        button2.callback = dismerry_1
        view=View()
        view.add_item(button)
        view.add_item(button2)
        await interaction.response.send_message(view=view,embed=embed,ephemeral=True)
        
@bot.tree.command(name="能力頁面",description="查看你的能力")
async def ability(interaction: discord.Interaction):
    with open('rpg_data.json','r',encoding='utf-8') as file:
        rpg_data = json.load(file)
    without = ["current_hp","current_mp"]
    hpmp = ["HP上限","MP上限"]
    percent = ["穩定率","恨意值","受到傷害%(減少)"]
    hour,minute,period = time()
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        update_state(interaction)
        with open('rpg_data.json','r',encoding='utf-8') as file:
            rpg_data = json.load(file)
        embed = discord.Embed(title=f'能力列表',description=f'{interaction.user.mention} 以下是你的能力',color=randcolor())
        embed.set_thumbnail(url=interaction.user.avatar)
        for name,value in rpg_data[str(interaction.user.id)]["state"].items():
            if name not in without:
                if name in hpmp:
                    embed.add_field(name=name.replace("上限",""),value=f'{rpg_data[str(interaction.user.id)]["state"]["current_"+ name.replace("上限","").lower()]} (上限：{value})'
,inline=False)
                elif name in percent:
                    embed.add_field(name=name,value=f'{value}%',inline=False)
                else:
                    embed.add_field(name=name,value=value,inline=False)
        if len(rpg_data[str(interaction.user.id)]["effecting"]) != 0:
            items = ""
            for i in rpg_data[str(interaction.user.id)]["effecting"]:
                items += f'{i["name"]} ({i["des"]})'
            embed.add_field(name='使用的道具(下次戰鬥後將消耗)',value=items,inline=False)

        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        await interaction.response.send_message(embed=embed,ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])

@bot.tree.command(name="使用道具",description="選擇一個背包中可以使用的道具")
async def item_use(interaction: discord.Interaction):
    with open('rpg_data.json','r',encoding='utf-8') as file,open('job.json','r',encoding='utf-8') as file1:
        rpg_data = json.load(file)
        job = json.load(file1)
    hour,minute,period = time()
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    item_can_use = []
    for index, item in enumerate(rpg_data[str(interaction.user.id)]["bag"]):
        if item["kind"] == "drug" and item["drug_type"] is not None:
            item_can_use.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})', value=index, description=f'{item["drug_type"]} {item["des"]}'))
        elif item["kind"] == "drug" or item["kind"] == "reset" or item["kind"] == 'energy':
            item_can_use.append(discord.SelectOption(label=f'{item["name"]} ({item["per"]})', value=index, description=f'{item["des"]}'))

    if len(item_can_use) == 0:
        embed = discord.Embed(title='噢噢...沒有可以使用的道具',color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請確認你的背包喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        async def use_item_1(interaction):
            async def use_item_2(interaction):
                async def use_item_3(interaction):
                    name = select.values[0].split(',')[0]
                    index = select.values[0].split(',')[1]
                    rpg_data[str(interaction.user.id)][index] = name

                    if item["per"] -1 == 0:
                        rpg_data[str(interaction.user.id)]["bag"].remove(rpg_data[str(interaction.user.id)]["bag"][item_index])
                    else:
                        item["per"] -=1
                    embed = discord.Embed(title=':white_check_mark: 重製完成。',description='',color=randcolor())
                    await interaction.response.edit_message(embed=embed,view=None)
                    with open('rpg_data.json','w',encoding='utf-8') as file:
                        json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                custom = interaction.data["custom_id"]
                if custom == "yes":
                    if item["kind"] == "drug":
                        embed = discord.Embed(title=':white_check_mark: 使用成功',description='',color=randcolor())
                        embed.add_field(name=item["des"],value='',inline=False)
                        check = False
                        for i in item["effect"]:
                            if i["index"] in ["current_hp","current_mp"]:
                                check = True
                                d = i["index"].replace("current_","").upper()+"上限"
                                if i["type"] == 'x':
                                    rpg_data[str(interaction.user.id)]["state"][i["index"]] = rpg_data[str(interaction.user.id)]["state"][i]*(i["value"]/100)
                                elif i["type"] == '+':
                                    rpg_data[str(interaction.user.id)]["state"][i["index"]] = min(rpg_data[str(interaction.user.id)]["state"][i["index"]]+i["value"],rpg_data[str(interaction.user.id)]["state"][d])
                                elif i["type"] == '-':
                                    rpg_data[str(interaction.user.id)]["state"][i["index"]] = min(rpg_data[str(interaction.user.id)]["state"][i["index"]]-i["value"],rpg_data[str(interaction.user.id)]["state"][d])
                        if check:
                            if item["per"] -1 == 0:
                                rpg_data[str(interaction.user.id)]["bag"].remove(item)
                            else:
                                item["per"] -= 1

                        elif len(rpg_data[str(interaction.user.id)]["effecting"]) == 0:
                            rpg_data[str(interaction.user.id)]["effecting"].append(item)
                            if item["per"] -1 == 0:
                                rpg_data[str(interaction.user.id)]["bag"].remove(rpg_data[str(interaction.user.id)]["bag"][item_index])
                            else:
                                item["per"] -=1
                            embed.add_field(name=item["name"],value='的效果已經新增',inline=False)
                        else:
                            for index,e in enumerate(rpg_data[str(interaction.user.id)]["effecting"]):
                                if e["drug_type"] == item["drug_type"]:
                                    embed.add_field(name=e["name"],value='的效果已被覆蓋',inline=False)
                                    rpg_data[str(interaction.user.id)]["effecting"][index] = item
                                    break
                                else:
                                    rpg_data[str(interaction.user.id)]["effecting"].append(item)
                                    embed.add_field(name=item["name"],value='的效果已經新增',inline=False)
                        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                        await interaction.response.edit_message(embed=embed,view=None)
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                            json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                    elif item["kind"] == "reset":
                        if item["name"] == '主職業重製書':
                            for equip,value in rpg_data[str(interaction.user.id)]["equip"].items():
                                if value is not None:
                                    embed = discord.Embed(title=':x: 請先將裝備欄清空！',description='',color=discord.Color.red())
                                    await interaction.response.edit_message(embed=embed,view=None)
                                    return
                            main_options = [
                                discord.SelectOption(label='旋風槍', value='旋風槍,mainjob',description="有著高面板和高速度的優勢"),
                                discord.SelectOption(label='拔刀劍', value='拔刀劍,mainjob',description="以頻繁無敵而聞名，但是傷害略勝一籌"),
                                discord.SelectOption(label='單手劍', value='單手劍,mainjob',description="六邊形戰士"),
                                discord.SelectOption(label='雙手劍', value='雙手劍,mainjob',description="有著全rpg最高的ATK，但是速度如同烏龜"),
                                discord.SelectOption(label='弓', value='弓,mainjob',description="多段的傷害，使打限傷不再痛苦(速度:中等)"),
                                discord.SelectOption(label='連弩', value='連弩,mainjob',description="超高機動性的速度，可以創造許多額外回合，以及頻繁的異常狀態(攻擊:低)"),
                                discord.SelectOption(label='法杖', value='法杖,mainjob',description="大量的mp回復優勢，給隊友創造很多機會"),
                                discord.SelectOption(label='拳套', value='拳套,mainjob',description="超硬身版，全場最盧")
                                ]   
                            for i in main_options:
                                if i.label == rpg_data[str(interaction.user.id)]["mainjob"]:
                                    main_options.remove(i)
                                    break
                            select = discord.ui.Select(placeholder='選擇新的主職業！',options=main_options)      
                            select.callback = use_item_3
                            view = discord.ui.View()
                            view.add_item(select)
                            await interaction.response.edit_message(view=view,embed=None)

                        elif item["name"] == '副職業重製書':
                            if str(interaction.user.id) in job:
                                if job[str(interaction.user.id)]["time"] == 0:
                                    embed = discord.Embed(title=':x: 請先領取工作獎勵',description='',color=discord.Color.red())
                                else:
                                    embed = discord.Embed(title=':x: 請先等待工作結束',description=f'尚餘 `{job[str(interaction.user.id)]}` 分鐘',color=discord.Color.red())
                                await interaction.response.edit_message(embed=embed,view=None)
                                return

                            sup_options = [
                                discord.SelectOption(label='製藥師', value='製藥師,supjob',description="可以製作強大的藥品供玩家使用"),
                                discord.SelectOption(label='精煉師', value='精煉師,supjob',description="精煉各種裝備，使能力值得到大幅加強"),
                                discord.SelectOption(label='製裝師', value='製裝師,supjob',description="可以製作各種裝備"),
                                discord.SelectOption(label='附魔師', value='附魔師,supjob',description="消耗大量素材，給裝備附上強大能力"),
                                discord.SelectOption(label='穿孔師', value='穿孔師,supjob',description="消耗大量素材，給裝備穿孔"),
                                discord.SelectOption(label='礦工', value='礦工,supjob',description="金屬和獸品的主要來源，偶爾會獲得魔素"),
                                discord.SelectOption(label='喜歡伐木的獵人', value='喜歡伐木的獵人,supjob',description="布料和木材和藥品的主要來源"),
                                discord.SelectOption(label='合成師', value='合成師,supjob',description="解鎖各種合成配方?，用於合成關鍵物品"),
                                discord.SelectOption(label='分解師', value='分解師,supjob',description="用於分解材料，獲得額外金幣獎勵"), 
                                ]
                            for i in sup_options:
                                if i.label == rpg_data[str(interaction.user.id)]["supjob"]:
                                    sup_options.remove(i)
                                    break
                            select = discord.ui.Select(placeholder='選擇新的副職業！',options=sup_options)      
                            select.callback = use_item_3
                            view = discord.ui.View()
                            view.add_item(select)
                            await interaction.response.edit_message(view=view,embed=None)

                        elif item["name"] == '性別重製書':
                            if rpg_data[str(interaction.user.id)]["merry"] is not None:
                                embed = discord.Embed(title=':x: 請先與你的伴侶離婚',description='',color=discord.Color.red())
                                await interaction.response.edit_message(embed=embed,view=None)
                                return

                            sex = [
                                discord.SelectOption(label='男性', value='男性,sex',description="可以和男性或女性或扶他結婚"),
                                discord.SelectOption(label='女性', value='女性,sex',description="可以和女性或男性或扶他結婚"),
                                discord.SelectOption(label='扶他', value='扶他,sex',description="可以和男性或女性結婚"),
                                ]
                            for i in sex:
                                if i.label == rpg_data[str(interaction.user.id)]["sex"]:
                                    sex.remove(i)
                                    break
                            select = discord.ui.Select(placeholder='選擇新的性別！',options=sex)      
                            select.callback = use_item_3
                            view = discord.ui.View()
                            view.add_item(select)
                            await interaction.response.edit_message(view=view,embed=None)

                    elif item["kind"] == 'energy':
                        embed = discord.Embed(title='回復成功',description='',color=discord.Color.green())
                        embed.add_field(name='能量值',value=f'{rpg_data[str(interaction.user.id)]["energy"]} -> {min(100,rpg_data[str(interaction.user.id)]["energy"]+item    ["value"])}')
                        rpg_data[str(interaction.user.id)]["energy"] = min(100,rpg_data[str(interaction.user.id)]["energy"]+item["value"])
                        if item["per"] - 1 == 0:
                            rpg_data[str(interaction.user.id)]["bag"].remove(item)
                        else:
                            item["per"] -= 1
                        await interaction.response.edit_message(view=None,embed=embed)
                        with open('rpg_data.json','w',encoding='utf-8') as file:
                            json.dump(rpg_data,file, indent=4,ensure_ascii=False)

                elif custom == 'no':
                    embed = discord.Embed(title=':white_check_mark: 使用取消',description='',color=randcolor())
                    embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
                    await interaction.response.edit_message(embed=embed,view=None)
                

            item = rpg_data[str(interaction.user.id)]["bag"][int(select.values[0])]
            item_index = int(select.values[0])
            embed = discord.Embed(title="確定要使用這個道具嗎？",description='',color=randcolor())
            if item["kind"] == "drug":
                if item["drug_type"] is not None:
                    embed.add_field(name=f'{item["name"]} ({item["per"]})',value=f'{item["drug_type"]} {item["des"]}',inline=False)
                else:
                    embed.add_field(name=f'{item["name"]} ({item["per"]})',value=f'{item["des"]}',inline=False)
            else:
                embed.add_field(name=f'{item["name"]} ({item["per"]})',value=f'{item["des"]}',inline=False)
            button=Button(label="接受",custom_id="yes",style = discord.ButtonStyle.green)
            button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
            button.callback = use_item_2
            button2.callback = use_item_2
            view=View()
            view.add_item(button)
            view.add_item(button2)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.edit_message(view=view,embed=embed)

        select = discord.ui.Select(placeholder='選擇要使用的道具',options=item_can_use)      
        select.callback = use_item_1
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)

@bot.tree.command(name="每日簽到",description="簽到獲取獎勵")
async def item_use(interaction: discord.Interaction):
    with open('rpg_data.json','r',encoding='utf-8') as file,open('sign_in.json','r') as file1,open('user.json','r') as file2:
        rpg_data = json.load(file)
        sign = json.load(file1)
        user = json.load(file2)
    hour,minute,period = time()
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif sign[str(interaction.user.id)]["state"] == True:
        embed = discord.Embed(title=":x: 你今天已經簽到過了！", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name=f'今天是你簽到的第 {sign[str(interaction.user.id)]["day"]} 天', value="請明天再來。",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

    else:
        embed = discord.Embed(title=f"獲得獎勵了！", description=f"",color=randcolor())
        sign[str(interaction.user.id)]["state"] = True
        sign[str(interaction.user.id)]["day"] += 1
        coin = random.randint(100,200+sign[str(interaction.user.id)]["day"])
        fish_coin = random.randint(200,300+sign[str(interaction.user.id)]["day"]*5)
        embed.add_field(name=':coin: 金幣',value=coin,inline=True)
        embed.add_field(name=f'{bot.get_emoji(1219122262427304048)} 鮭魚幣',value=fish_coin,inline=True)
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name=f'', value=f'今天是你簽到的第 {sign[str(interaction.user.id)]["day"]} 天',inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=rpg_data[str(interaction.user.id)]["ephemeral"])
        rpg_data[str(interaction.user.id)]["coin"] += coin
        for e in user:
            if e["user_id"] == str(interaction.user.id):
                e["coin"] += fish_coin
                break

        with open('rpg_data.json', 'w', encoding='utf-8') as file,open('sign_in.json', 'w') as file1,open('user.json', 'w') as file2:
            json.dump(rpg_data, file, ensure_ascii=False, indent=4)
            json.dump(sign, file1, indent=4)
            json.dump(user, file2, indent=4)

@bot.tree.command(name="打工",description="打工賺錢")
async def item_use(interaction: discord.Interaction):
    with open('rpg_data.json','r',encoding='utf-8') as file,open('job.json','r',encoding='utf-8') as file1:
        rpg_data = json.load(file)
        job = json.load(file1)
    hour,minute,period = time()
    if str(interaction.user.id) not in rpg_data:
        embed = discord.Embed(title="噢噢...好像找不到你的資料", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="請先使用 </rpg個人資料:1234344284572876820> 登記你的資料喔！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    elif (rpg_data[str(interaction.user.id)]["supjob"] == "礦工" or rpg_data[str(interaction.user.id)]["supjob"] == "喜歡伐木的獵人"):
        embed = discord.Embed(title="礦工和獵人不可以打工！", description=f"",color=discord.Color.red())
        embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
        embed.add_field(name="你們只可以用職業技能賺錢！", value="",inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
        return
    elif str(interaction.user.id) in job:
        items = ""
        for item in job[str(interaction.user.id)]["gain"]:
            if item["kind"] == "pt":
                items += f"{item['name']} {item['per']} pt\n"
            elif item["kind"] == "coin":
                items += f"{item['name']} {item['per']} s\n"
            else:
                items += f"{item['name']}\n"
        if job[str(interaction.user.id)]["time"] == 0:
            embed = discord.Embed(title=":carpentry_saw: 你的打工結束了！", description=f'你總共過勞了 {job[str(interaction.user.id)]["overwork"]} 次',color=randcolor())
            embed.add_field(name='獲得的道具',value=items,inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            total = sum(1 if (i["kind"] != "pt" and i["kind"] != "coin") else 0 for i in job[str(interaction.user.id)]["gain"])
            bag_full = False
            mail_items = 0
            if 50-(len(rpg_data[str(interaction.user.id)]["bag"]) + len(rpg_data[str(interaction.user.id)]["mail"])) >= total:
                for item in job[str(interaction.user.id)]["gain"]:
                    if item["kind"] == "pt":
                        if rpg_data[str(interaction.user.id)]["pt"][item["name"]] + item["per"] > 100000:
                            rpg_data[str(interaction.user.id)]["pt"][item["name"]] = 100000
                        else:
                            rpg_data[str(interaction.user.id)]["pt"][item["name"]] += item["per"]
                    elif item["kind"] == "coin":
                        rpg_data[str(interaction.user.id)]["coin"] += item["per"]
                    else:
                        if len(rpg_data[str(interaction.user.id)]["bag"]) == 25:
                            taipei_time = datetime.now(taipei_timezone)
                            bag_full = True
                            mail_items += 1
                            user_info = {
                                "user":"打工獎勵",
                                "time":f"{taipei_time.year}/{taipei_time.month}/{taipei_time.day} {taipei_time.hour}:{taipei_time.minute}"
                                }
                            item.update(user_info)
                            rpg_data[str(interaction.user.id)]["mail"].append(item)
                            
                        else:
                            rpg_data[str(interaction.user.id)]["bag"].append(item)
            else:
                embed.add_field(name='',value='你的背包與禮物箱已滿，道具將不匯入。',inline=False)
            if not bag_full:
                embed.add_field(name='',value='道具已全數匯入背包！',inline=False)
            else:
                embed.add_field(name='',value=f'背包已滿，共 {mail_items} 個道具進入了禮物箱',inline=False)

            del job[str(interaction.user.id)]
            with open('rpg_data.json','w',encoding='utf-8') as file,open('job.json','w',encoding='utf-8') as file2:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                json.dump(job,file2, indent=4,ensure_ascii=False)
            embed.add_field(name="", value="",inline=False)
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif job[str(interaction.user.id)]["time"] >= 0:
            little_job = [
                "快樂打工人！",
                "你正在被壓榨！",
                "||扶他，看招！||"
                ]
            embed = discord.Embed(title=f':carpentry_saw: {random.choice(little_job)}',description='',color=randcolor())
            embed.add_field(name='你的工時還剩餘',value=f'`{job[str(interaction.user.id)]["time"]}` 分鐘',inline=False)
            if rpg_data[str(interaction.user.id)]["energy"] > 0:
                    embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'(能量充足 產能提升 {rpg_data[str(interaction.user.id)]["energy"]/2} %)',inline=False)
            elif rpg_data[str(interaction.user.id)]["energy"] > -30:
                embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'精力一般',inline=False)
            else:
                embed.add_field(name=f'能量剩餘 {rpg_data[str(interaction.user.id)]["energy"]}',value=f'(精力不足 產能降低 {rpg_data[str(interaction.user.id)]["energy"]} %\n請補充能量)',inline=False)
            if len(job[str(interaction.user.id)]["gain"]) == 0:
                embed.add_field(name='獲得的道具',value='無道具',inline=False)
            else:
                embed.add_field(name='獲得的道具',value=items,inline=False)
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        async def little_work_0(interaction):
            embed = discord.Embed(title=f':carpentry_saw: 你開始了打工',description='',color=randcolor())
            embed.add_field(name='工時尚餘',value=f'{select.values[0]} 小時')
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)')
            await interaction.response.edit_message(content=None,embed=embed,view=None)
            job[str(interaction.user.id)] = {
                "luk":rpg_data[str(interaction.user.id)]["ab_value"]["LUK"],
                "job":"other",
                "sex":rpg_data[str(interaction.user.id)]["sex"],
                "fortune":1,
                "work_time":0,
                "time":60*int(select.values[0]),
                "gain":[],
                "overwork":0
                }
            with open('rpg_data.json','w',encoding='utf-8') as file,open('job.json','w',encoding='utf-8') as file2:
                json.dump(rpg_data,file, indent=4,ensure_ascii=False)
                json.dump(job,file2, indent=4,ensure_ascii=False)
        job_time = []
        time_ = [1,8,16,24]
        for t in time_:
            job_time.append(discord.SelectOption(label=f'{t}小時',description=f'消耗 {t*15} 點能量',value=t))
        view = discord.ui.View()
        select = discord.ui.Select(placeholder="(打工)點我選擇工時", options=job_time)      
        select.callback = little_work_0
        view.add_item(select)
        await interaction.response.send_message(view=view,ephemeral=True)

@bot.tree.command(name="音樂指令幫助",description="顯示所有音樂指令的幫助")
async def music_help(interaction: discord.Interaction):
    content = """
指令前綴& 如果指令是中文，則簡體繁體都有效

# &j &jo (join) &加入語音
>加入目前用戶所在語音房

# &l &le (leave) &退出語音
>退出目前用戶的語音房

# &p &pl (play) &播放
## ⭡播歌用這個！！！
>此指令必須在後面跟上連結或是搜尋歌名

目前只支援：
- yt單曲、歌單
- mixerbox歌單
- Spotify完全不支援
搜尋名稱有時候會不準確 建議打語歌曲相關的名稱

# &skip (skip) &跳過
>跳過這首歌 如果後面沒歌了就會直接結束

# &s &st (stop) &暫停
>暫停這首歌

# &r &re (resume) &繼續
>繼續暫停的歌

# &list (list) &佇列
>顯示目前正在排隊的歌(不包含當前播放的歌)

# &i (infomation) &訊息 &歌曲訊息
>顯示當前撥放歌曲的詳細訊息、以及大部分功能按鈕化(控制面板)

# 控制面板(用&i會跳出來)
以下有一些指令沒有的功能：

## -播放狀態：
    共有三種狀態：
    -普通輪播
    -單首循環
    -隨機撥放  
    預設是普通輪播，每按一次會切換到下一種狀態。

## -最愛清單：
    允許你珍藏喜歡的歌，以便你快速搜尋，加入歌單(上限25首)
    ※**只限定單曲，歌單暫不支援，有需要再做**

## -歷史紀錄
    列出上五首播的歌，以便你不知道聽了啥。

## -調整音量
    可以調整0~100 0為靜音，100為最大聲。

打算做但還沒做：
1.批量跳過(斟酌中)

注意事項：
1.整體使用體驗不如專業的音樂機器人(Ex.很多bug、使用不順) 意在中文化使用
2.有任何建議(或bug)歡迎提出
"""
    await interaction.response.send_message(content=content,ephemeral=True)

def create_embed(all_products, page_number):
    product = all_products[page_number]
    
    embed = discord.Embed(title="查詢結果", color=0xF0FFFF)
    embed.add_field(name=f"商品主人", value=product['user'], inline=False)
    embed.add_field(name=f"商品名稱", value=product['name'], inline=False)
    embed.add_field(name=f"商品價格", value=product['price'], inline=False)
    embed.add_field(name=f"商品數量", value=product['quantity'], inline=False)
    embed.add_field(name="上架日期", value=product["update"],inline=False)
    embed.add_field(name="類別", value=product["type_name"],inline=False)
    embed.add_field(name=f"商品描述", value=product['describe'], inline=False)
    if product['url'] == None:
        embed.add_field(name=f"商品圖片", value="無", inline=False)
    else:
        embed.add_field(name=f"商品圖片", value='', inline=False)
        embed.set_image(url=product['url'])
    embed.set_footer(text=f"{page_number+1}頁 / {len(all_products)}頁")
    
    return embed

def format_duration(duration):
    if duration is None:
        return '未知'
    
    duration = int(duration)
    hours, remainder = divmod(duration, 3600)
    mins, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f'{hours}:{mins:02d}:{secs:02d}'
    else:
        return f'{mins}:{secs:02d}'


skip_next = False

async def convert_spotify_to_audio_url(spotify_url):
    try:
        command = ['spotdl', 'url', spotify_url]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"Error during Spotify to audio URL conversion: {stderr.decode()}")
            return None, None, None

        audio_urls = re.findall(r'https://[^\s]+', stdout.decode())
        if len(audio_urls) > 1:
            audio_url = audio_urls[1]
        else:
            print("Less than two valid audio URLs found.")
            return None, None, None

        track_id = re.search(r'spotify.com/track/(\w+)', spotify_url)
        if track_id:
            track_id = track_id.group(1)
            track_info = sp.track(track_id)
            title = track_info['name']
            duration = track_info['duration_ms'] / 1000
            formatted_duration = format_duration(duration)
            return audio_url, title, formatted_duration

        return audio_url, None, None

    except Exception as e:
        print(f"Error during Spotify to audio URL conversion: {e}")
        return None, None, None

current_song = {}
song_status = {}
song_history = {}
audio_source = None
volume = {}
last_message = {}
store_embed ={}

async def play(ctx, from_after=True, g_id=None):
    await asyncio.sleep(1)
    global skip_next, current_song, queue, song_status,audio_source,song_history,volume_check

    status_found = False
    for i, j in song_status.items():
        if str(ctx.guild.id) == i:
            status_found = True
            break
    if not status_found:
        song_status.update({str(ctx.guild.id): 1})

    if g_id not in song_history:
        song_history[g_id] = []

    g_queue = queue[g_id]

    if from_after and not g_queue and song_status[str(ctx.guild.id)] not in [2, 3]:
        return

    if ctx.guild.id not in current_song:
        current_song[ctx.guild.id] = {}

    g_current_song = current_song[ctx.guild.id]

    if not g_queue and song_status[str(ctx.guild.id)] not in [2, 3]:
        g_current_song = {}
        return

    if song_status[str(ctx.guild.id)] == 1:
        song = g_queue.pop(0)
    elif song_status[str(ctx.guild.id)] == 2:
        song = g_current_song
    else:
        song = random.sample(g_queue, 1)[0] if len(g_queue) > 0 else g_current_song

    if len(song_history[ctx.guild.id]) == 5:
        del song_history[g_id][0]
    song_history[g_id].append(song)

    url_ = song['url']
    g_current_song.update(song)

    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and not vc.is_playing():
        try:
            ffmpeg_before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
            ffmpeg_options = '-vn'

            audio_source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    url_,
                    before_options=ffmpeg_before_options,
                    options=ffmpeg_options
                ),
                volume=0.1 if g_id not in volume else volume[g_id][0]
            )
            def after_playing(error):
                global skip_next

                if error:
                    print(f"错误: {error}")
                if not skip_next:
                    bot.loop.create_task(play(ctx, g_id=g_id))
                else:
                    skip_next = False
            vc.play(audio_source, after=after_playing)
        except Exception as e:
            print("意外错误:", str(e))

def get_voice_client(guild):
    for vc in bot.voice_clients:
        if vc.guild == guild:
            return vc
    return None

async def get_audio_url(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'extract_flat': True,
        'force_generic_extractor': True
    }
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(ydl_opts).extract_info(url, download=False))
    if 'entries' in info:
        return [entry['url'] for entry in info['entries']]
    return info.get('url', '')

def extract_playlist_id(playlist_url):
    match = re.search(r'spotify\.com/playlist/([a-zA-Z0-9]+)', playlist_url)
    return match.group(1) if match else None

def get_spotify_thumbnail(track_id):
    track_info = sp.track(track_id)
    if track_info and 'album' in track_info and 'images' in track_info['album']:
        images = track_info['album']['images']
        if images:
            return images[0]['url']
    return None

current_page = 0
PAGE_SIZE = 25

async def update_message(message, queue, page):
    embed = generate_embed(queue, page)
    buttons = discord.ui.View()
    buttons.clear_items()
    
    prev_button = discord.ui.Button(label='上一頁', style=discord.ButtonStyle.primary, disabled=page == 0)
    next_button = discord.ui.Button(label='下一頁', style=discord.ButtonStyle.primary, disabled=(page + 1) * PAGE_SIZE >= len(queue))
    
    async def previous_callback(interaction: discord.Interaction):
        nonlocal page
        if page > 0:
            page -= 1
            await interaction.response.defer()
            await update_message(message, queue, page)
    
    async def next_callback(interaction: discord.Interaction):
        nonlocal page
        if (page + 1) * PAGE_SIZE < len(queue):
            page += 1
            await interaction.response.defer()
            await update_message(message, queue, page)

    prev_button.callback = previous_callback
    next_button.callback = next_callback
    
    buttons.add_item(prev_button)
    buttons.add_item(next_button)
    
    await message.edit(embed=embed, view=buttons)

def generate_embed(queue, page):
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(queue))
    embed = discord.Embed(title=f'音樂佇列(第{page + 1}頁)', description=f'共{len(queue)}首')

    if queue:
        for idx in range(start, end):
            song = queue[idx]
            embed.add_field(
                name=f"{bot.get_emoji(1266320607520231445) if song['app'] == 'yt' else bot.get_emoji(1294206903538155561)} | {song['title']}",
                value=f'[{song["time"]}]({song["original_url"]}){(10 - len(str(song["time"]))) * " "}來自:**{song["user"]}**',
                inline=False)
    else:
        embed.add_field(name='目前無歌曲正在撥放！', value='', inline=True)

    return embed

@bot.event
async def on_message(message):
    with open('user.json', 'r') as file, open('afk.json', 'r', encoding='utf-8-sig') as file1:
        data = json.load(file)
        afk = json.load(file1)

    global save,queue,skip_next,current_song,song_status
    for user_id, afk_data in afk.items():   
        if user_id == str(message.author.id):
            if afk_data["afk_time"] - len(message.content) * 5 >= 0:
                afk_data["afk_time"] -= len(message.content) * 5
            else:
                afk_data["afk_time"] = 0

    if message.author == bot.user:
        return

    if message.guild.id not in queue:
        queue[message.guild.id] = []
    g_queue = queue[message.guild.id]

    if message.guild.id not in current_song:
        current_song[message.guild.id] = {}

    g_current_song = current_song[message.guild.id]

    if message.content == '!afk':
        content = []
        print(message.author.id)
        for user_id, afk_data in afk.items():
            if afk_data["afk_time"] >= 21600:
                content.append(f'名稱: {afk_data["display_name"]} ({afk_data["name"]})\n時間:{afk_data["afk_time"]}(分鐘)\n\n')
        if len(content) == 0:
            await message.reply('無不活躍成員！')
        else:
            j=0
            stop = 0
            for idx,i in enumerate(content):
                j += len(i)
                if j > 2000:
                    await message.reply(''.join(content[stop:idx-1]))
                    stop = idx
                    j = 0

            await message.reply(''.join(content[stop:]))

    elif '!lot' in message.content and message.author.id == 579618807237312512:
        try:
            user = []

            async for m in bot.get_channel(1183431186161340466).history():
                for e in m.embeds:
                    name = e.title.split('抽到了：')[0]
                    found = False
        
                    for index, n in enumerate(user):
                        if n[0] == name:
                            found = True
                            break
        
                    if not found:
                        user.append([name, 0, {}, ''])  # [name, spina, items, reward]
                        index = len(user) - 1
        
                    for j in e.fields:
                        if j.name.endswith('眾神幣'):
                            user[index][1] += int(j.name.split('萬眾神幣')[0])
                        else:
                            if j.name in user[index][2]:
                                user[index][2][j.name] += 1
                            else:
                                user[index][2][j.name] = 1

            result = ""
            for r in user:
                result += f"\n{r[0]}\n"
                if r[1]:
                    result += f"眾神幣 {r[1]} 萬\n"
                if r[2]:
                    for item_name, count in r[2].items():
                        result += f"{item_name} x {count}\n"
                result += r[-1]

            await message.reply(content=result)

        except IndexError:
            await message.reply(content='Error 缺少必要的函數')

    elif '!del' in message.content and message.author.id == 579618807237312512:
        try:
            if message.content.split(' ')[1] == 'all':
                try:
                    name = message.content.split(' ')[2]
                    count = 0
                    async for m in bot.get_channel(1183431186161340466).history():
                        for e in m.embeds:
                            if name in e.title:
                               count += 1
                               await m.delete()
                            continue
                    if count == 0:
                        await message.reply(content=f'無搜尋結果')
                    else:
                        await message.reply(content=f'共刪除{count}個結果')

                except IndexError:
                    count = 0
                    
                    async for m in bot.get_channel(1183431186161340466).history():
                        count += 1
                        for e in m.embeds:
                            save += '\n'+e.title+'\n'
                            for j in e.fields:
                                save += f'{j.name}\n{j.value}'
                        await m.delete()
                    await message.reply(content=f'共刪除{count}個結果')

        except IndexError:
            await message.reply(content='Error 缺少必要的函數')

    elif '!save' in message.content and message.author.id == 579618807237312512:
        if len(save) >0 :
            await message.reply(content=save)
        elif len(save) > 2000:
            chunks = [save[i:i+2000] for i in range(0, len(save), 2000)]
            for chunk in chunks:
                await message.reply(content=chunk)
        else:
            await message.reply(content='None')

    elif '&j' == message.content or '&jo' == message.content or '&加入語音' == message.content or '&加入语音' == message.content:
        if message.author.voice:
            in_same_channel = False
            for vc in bot.voice_clients:
                if vc.channel == message.author.voice.channel:
                    in_same_channel = True
                    break

            if in_same_channel:
                embed = discord.Embed(title=':x:機器人已經在你所在的語音房了！',color=discord.Color.red())
                await message.reply(content='',embed=embed)

            else:
                hour,minute,period = time()
                for vc in bot.voice_clients:
                    if vc.guild == message.guild:
                        await vc.disconnect()
                        break
                await message.author.voice.channel.connect()
                embed = discord.Embed(title=f':white_check_mark:成功加入**{message.author.display_name}**的語音房！',description=f'在{period}{hour}:{minute}時加入了`{message.author.voice.channel.name}`',color=randcolor())
                await message.reply(content='',embed=embed)

        else:
            embed = discord.Embed(title=':x:你不在語音房內！',description='請先加入一個語音房。',color=discord.Color.red())
            await message.reply(content='',embed=embed)

    elif '&l' == message.content or '&le' == message.content or '&退出語音' == message.content or '&退出语音' == message.content:
        found = False
        for vc in bot.voice_clients:
            if vc.guild == message.guild:
                found = True
                break
        
        if found:
            await vc.disconnect()
            embed = discord.Embed(title=f':white_check_mark:成功退出`{message.author.display_name}`的語音頻道！',description='掰啦////',color=randcolor())
            await message.reply(content='',embed=embed)

        else:
            embed = discord.Embed(title=':x:我不在語音頻道內噢！',color=discord.Color.red())
            await message.reply(content='',embed=embed)

    elif '&p' in message.content or '&pl' in message.content or '&播放' in message.content:
        voice_client = get_voice_client(message.guild)
        found = False
        for vc in bot.voice_clients:
            if vc.guild == message.guild:
                found = True
                voice_client = vc
                break
        query_p = message.content.split(' ')[1:]
        query = ' '.join(query_p)
        if not query:
            embed = discord.Embed(title=':x:指令輸入失敗！',description='請提供網址or搜尋名稱',color=discord.Color.red())
            await message.reply(embed=embed)
            return

        if not found:
            if message.author.voice and message.author.voice.channel:
                try:
                    voice_client = await message.author.voice.channel.connect()
                    found = True
                except Exception as e:
                    embed = discord.Embed(title=':x:加入語音頻道失敗！',description=f'錯誤: {str(e)}',color=discord.Color.red())
                    await message.reply(embed=embed)
                    return
            else:
                embed = discord.Embed(title=':x:我不在語音頻道內噢！',description='請加入一個語音頻道並再次嘗試！', color=discord.Color.red())
                await message.reply(content='', embed=embed)
                return

        hour, minute, period = time()
        if YOUTUBE_REGEX.match(query):
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'nocheckcertificate': True,
                'extract_flat': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                if 'list=' in query and 'watch' in query:
                    video_id = re.search(r'v=([^&]+)', query)
                    if video_id:
                        video_url = f'https://www.youtube.com/watch?v={video_id.group(1)}'
                        info = ydl.extract_info(video_url, download=False)
                        embed = discord.Embed(title=f"{bot.get_emoji(1266320607520231445)} | 成功加入{info.get('title', '')}", description=f'加入者:{message.author.display_name}(在{period}{hour}:{minute})', color=randcolor())
                        await message.reply(embed=embed,silent=True)
                        title = info.get('title', '未知标题')
                        url = await get_audio_url(video_url)
                        duration = info.get('duration', 0)
                        formatted_duration = format_duration(duration)
                        img_url = info.get('thumbnail', '')
                        view_count = info.get('view_count', 0)
                        like = info.get('like_count', 0)
                        up_date = info.get('upload_date', 0)
                        author = info.get('uploader', '未知作者')
                        channel_url = info.get('uploader_url', None)
                        data_ = {
                            'app': 'yt',
                            'url': url,
                            'original_url': video_url,
                            'title': title,
                            'time': formatted_duration,
                            'img_url': img_url,
                            'view_count': view_count,
                            'user': message.author.display_name,
                            'like': like,
                            'up_date': up_date,
                            'author': author,
                            'channel_url': channel_url
                        }
                        g_queue.append(data_)
                    else:
                        await message.reply("无法提取视频 ID。")

                elif 'playlist' in query and 'watch' not in query:
                    inf = ydl.extract_info(query, download=False)
                    if voice_client:
                        playlist = inf['entries']
                        embed = discord.Embed(title=f"{bot.get_emoji(1266320607520231445)} | 成功加入{inf.get('title', [])}(共{len(inf.get('entries', []))}首歌)", description=f'加入者:{message.author.display_name}(在{period}{hour}:{minute})', color=randcolor())
                        await message.reply(embed=embed,silent=True)
                        for vid_info in playlist:
                            info = ydl.extract_info(vid_info.get('url', ''), download=False)
                            video_url = info.get('url', '')
                            title = info.get('title', '未知标题')
                            duration = info.get('duration', 0)
                            formatted_duration = format_duration(duration)
                            img_url = info.get('thumbnail', '')
                            view_count = info.get('view_count', 0)
                            like = info.get('like_count', 0)
                            up_date = info.get('upload_date', 0)
                            author = info.get('uploader', '未知作者')
                            channel_url = info.get('uploader_url', None)
                            data_ = {
                                'app': 'yt',
                                'url': video_url,
                                'title': title,
                                'time': formatted_duration,
                                'img_url': img_url,
                                'user': message.author.display_name,
                                'original_url': vid_info.get('url', ''),
                                'view_count': view_count,
                                'like': like,
                                'up_date': up_date,
                                'author': author,
                                'channel_url': channel_url
                            }
                            g_queue.append(data_)
                            if not voice_client.is_playing() and len(g_queue) == 1:
                                await play(message, g_id=message.guild.id)

                else:
                    info = ydl.extract_info(query, download=False)
                    embed = discord.Embed(title=f"{bot.get_emoji(1266320607520231445)} | 成功加入{info.get('title', '')}", description=f'加入者:{message.author.display_name}(在{period}{hour}:{minute})', color=randcolor())
                    await message.reply(embed=embed,silent=True)
                    title = info.get('title', '未知标题')
                    url = await get_audio_url(query)
                    duration = info.get('duration', 0)
                    formatted_duration = format_duration(duration)
                    img_url = info.get('thumbnail', '')
                    view_count = info.get('view_count', 0)
                    like = info.get('like_count', 0)
                    up_date = info.get('upload_date', 0)
                    author = info.get('uploader', '未知作者')
                    channel_url = info.get('uploader_url', None)
                    data_ = {
                        'app': 'yt',
                        'url': url,
                        'title': title,
                        'time': formatted_duration,
                        'img_url': img_url,
                        'user': message.author.display_name,
                        'original_url': query,
                        'view_count': view_count,
                        'like': like,
                        'up_date': up_date,
                        'author': author,
                        'channel_url': channel_url
                    }
                    g_queue.append(data_)

            if not voice_client.is_playing() and len(g_queue) == 1:
                await play(message, g_id=message.guild.id)

        elif MBPLAYER_REGEX.match(query):
            headers = {
            'referer': 'https://www.mbplayer.com'
        }
            url = f"https://www.mbplayer.com/api/playlist?reverse=true&type=playlist&vectorId={query.split('/')[-1]}"
            try:
                response = requests.get(url, headers=headers)
                m_data = response.json()
            except Exception as e:
                await message.reply(content=f'出現了一點小錯誤\n{e}')
                return

            songs = []
            try:
                for i in m_data["items"]:
                    if i.get("statusCode") == 0:
                        songs.append(i["f"])
            except Exception as e:
                await message.reply(content=f'歌曲解析時出現錯誤：{e}')
                return

            embed = discord.Embed(
                title=f"{bot.get_emoji(1294206903538155561)} | 成功加入{m_data.get('name', '未知歌單')}(共{len(songs)}首歌)",
                description=f'加入者:{message.author.display_name}(在{period}{hour}:{minute})',
                color=randcolor()
            )
            await message.reply(embed=embed, silent=True)

            ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'nocheckcertificate': True,
                    'extract_flat': True,
                }

            if voice_client:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    for v in songs:
                        try:
                            yt_url = f'https://www.youtube.com/watch?v={v}'
                            info = ydl.extract_info(yt_url, download=False)
                            video_url = info.get('url', '')
                            title = info.get('title', '未知标题')
                            duration = info.get('duration', 0)
                            formatted_duration = format_duration(duration)
                            audio_url = await get_audio_url(video_url)
                            img_url = info.get('thumbnail', '')
                            view_count = info.get('view_count', 0)
                            like = info.get('like_count', 0)
                            up_date = info.get('upload_date', 0)
                            author = info.get('uploader', '未知作者')
                            channel_url = info.get('uploader_url', None)

                            data_ = {
                                'app': 'mb',
                                'url': audio_url,
                                'title': title,
                                'time': formatted_duration,
                                'img_url': img_url,
                                'user': message.author.display_name,
                                'original_url': yt_url,
                                'view_count': view_count,
                                'like': like,
                                'up_date': up_date,
                                'author': author,
                                'channel_url': channel_url
                            }

                            g_queue.append(data_)

                            if not voice_client.is_playing() and len(g_queue) == 1:
                                await play(message, g_id=message.guild.id)
            
                        except:
                            continue

        elif SPOTIFY_TRACK_REGEX.match(query):
            embed = discord.Embed(title=':x:我們目前不支援spotify！', description='非常抱歉><', color=discord.Color.red())
            await message.reply(embed=embed)
            return

        elif SPOTIFY_PLAYLIST_REGEX.match(query):
            embed = discord.Embed(title=':x:我們目前不支援spotify歌單！', description='非常抱歉，請使用單曲的方式點歌', color=discord.Color.red())
            await message.reply(embed=embed)

        else:
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'nocheckcertificate': True,
                'extract_flat': True,
            }

            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    search_query = f'ytsearch20:{query} official video'
                    search_results = ydl.extract_info(search_query, download=False)['entries']
                    filtered_results = [result for result in search_results if 'url' in result and 'shorts' not in result['url']]
                    options = [
                        discord.SelectOption(
                            label=f"{result['title']}",
                            value=result['url'],
                            description=format_duration(result.get('duration'))
                        )
                        for result in filtered_results
                    ]
                    if not options:
                        await message.reply(":x:未找到合適的搜尋結果！")
                        return
                    select = discord.ui.Select(placeholder="選擇一首歌", options=options)

                    async def select_callback(interaction):
                        selected_url = interaction.data['values'][0]
                        info = ydl.extract_info(selected_url, download=False)
                        embed = discord.Embed(title=f"{bot.get_emoji(1266320607520231445)} | 成功加入{info.get('title', '')}", description=f'加入者:{message.author.display_name}(在{period}{hour}:{minute})', color=randcolor())
                        embed.set_image(url=info.get('thumbnail', ''))
                        await s.edit(embed=embed, content='', view=None)
                        title = info.get('title', '未知标题')
                        url = await get_audio_url(selected_url)
                        duration = info.get('duration', 0)
                        formatted_duration = format_duration(duration)
                        img_url = info.get('thumbnail', '')
                        view_count = info.get('view_count', 0)
                        like = info.get('like_count', 0)
                        up_date = info.get('upload_date', 0)
                        author = info.get('uploader', '未知作者')
                        channel_url = info.get('uploader_url', None)
                        data_ = {
                            'app': 'yt',
                            'url': url,
                            'title': title,
                            'time': formatted_duration,
                            'img_url': img_url,
                            'user': message.author.display_name,
                            'original_url': selected_url,
                            'view_count': view_count,
                            'like': like,
                            'up_date': up_date,
                            'author': author,
                            'channel_url': channel_url
                        }
                        g_queue.append(data_)
                        if not voice_client.is_playing() and len(g_queue) == 1:
                            await play(message, g_id=message.guild.id)

                    select.callback = select_callback
                    view = discord.ui.View()
                    view.add_item(select)
                    embed = discord.Embed(title="選擇您要播放的歌曲：", color=randcolor())
                    s = await message.reply(content='', embed=embed, view=view)

            except Exception as e:
                await message.reply(f"發生錯誤：{str(e)}")

    elif '&skip' == message.content or '&跳過' == message.content or '&跳过' == message.content:
        voice_client = get_voice_client(message.guild)
        hour,minute,period = time()
        if voice_client and voice_client.is_playing():
            skip_next = True
            voice_client.stop()
            if g_queue or song_status[str(message.guild.id)] in [2,3]: 
                embed = discord.Embed(title=f":white_check_mark: 已跳過{g_current_song['title']}",description=f'{message.author.display_name}跳過了這首歌',color=randcolor())
                await play(message,from_after=False,g_id=message.guild.id)
                embed.set_footer(text=f'{period}{hour}:{minute}')
                await message.reply(embed=embed)

            else:
                embed = discord.Embed(title=f":white_check_mark: 已跳過{g_current_song['title']}",description='已經沒有歌曲正在排隊了喔！',color=randcolor())
                embed.set_footer(text=f'{period}{hour}:{minute}')
                await message.reply(embed=embed)
        else:
            embed = discord.Embed(title=':x: 沒有音樂正在播放！',color=discord.Color.red())
            g_current_song = None
            await message.reply(embed=embed)

    elif '&s' == message.content or '&st' == message.content or '&暫停' == message.content or '&暂停' == message.content:
        voice_client = get_voice_client(message.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(title=':white_check_mark: 音樂已暫停！',description=f'{message.author.display_name}暫停了音樂',color=randcolor())
            await message.reply(embed=embed)
        else:
            embed = discord.Embed(title=':x: 沒有音樂正在撥放！',color=discord.Color.red())
            await message.reply(embed=embed)

    elif '&r' == message.content or '&re' == message.content or '&繼續' == message.content or '&继续' == message.content:
        voice_client = get_voice_client(message.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(title=':white_check_mark: 音樂已恢復播放！',description=f'{message.author.display_name}繼續了音樂',color=randcolor())
            await message.reply(embed=embed)
        elif voice_client and not voice_client.is_playing():
            skip_next = True
            if song_status[str(message.guild.id)] == 1:
                g_queue.insert(1,g_current_song)
            embed = discord.Embed(title=':white_check_mark: 音樂已恢復播放！',description=f'{message.author.display_name}繼續了音樂',color=randcolor())
            await play(message,g_id=message.guild.id)
            await message.reply(embed=embed)
        else:
            embed = discord.Embed(title=':x: 目前音樂沒有暫停！',color=discord.Color.red())
            await message.reply(embed=embed)

    elif '&list' == message.content or '&佇列' == message.content or '&伫列' == message.content:
        if not g_queue:
            await message.reply("目前佇列中沒有歌曲。")
            return

        current_page = 0
        embed = generate_embed(g_queue, current_page)
        embed.color = randcolor()
        buttons = discord.ui.View()

        prev_button = discord.ui.Button(label='上一頁', style=discord.ButtonStyle.primary, disabled=True)
        next_button = discord.ui.Button(label='下一頁', style=discord.ButtonStyle.primary, disabled=(PAGE_SIZE >= len(g_queue)))

        async def previous_callback(interaction: discord.Interaction):
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await interaction.response.defer()
                await update_message(m, g_queue, current_page)

        async def next_callback(interaction: discord.Interaction):
            nonlocal current_page
            if (current_page + 1) * PAGE_SIZE < len(g_queue):
                current_page += 1
                await interaction.response.defer()
                await update_message(m, g_queue, current_page)

        prev_button.callback = previous_callback
        next_button.callback = next_callback

        buttons.add_item(prev_button)
        buttons.add_item(next_button)

        m = await message.reply(embed=embed, view=buttons)

    elif '&i' == message.content or '&訊息' == message.content or '&歌曲訊息' == message.content:
        if len(g_current_song) != 0:
            async def song_setting(interaction):
                status = interaction.data["custom_id"]
                hour, minute, period = time()
                if status == 'stop':
                    voice_client = get_voice_client(interaction.guild)

                    if voice_client:
                        if voice_client.is_playing():
                            voice_client.pause()
                            cont = f':white_check_mark: 音樂已暫停！\n{interaction.user.display_name}暫停了音樂 ({period}{hour}:{minute})'
                        else:
                            voice_client.resume()
                            cont = f':white_check_mark: 音樂已繼續！\n{interaction.user.display_name}繼續了音樂 ({period}{hour}:{minute})'
                    else:
                        embed = discord.Embed(title=':x:我不在語音頻道內噢！',color=discord.Color.red())
                        await interaction.response.send_message(embed=embed)
                        return

                    await interaction.response.edit_message(content=cont)

                elif status == 'continue':
                    
                    voice_client = get_voice_client(message.guild)

                    if voice_client and voice_client.is_playing():
                        global skip_next
                        g_current_song = current_song[message.guild.id]
                        skip_next = True
                        voice_client.stop()
                        status_text = {
                        1:"普通播放",
                        2:"單曲循環",
                        3:"隨機撥放"
                        }
                        if g_queue or song_status[str(interaction.guild.id)] in [2, 3]: 
                            cont = f":white_check_mark: 已跳過{g_current_song['title']}\n{interaction.user.display_name}跳過了這首歌 ({period}{hour}:{minute})"
                            await play(message, from_after=False, g_id=message.guild.id)
                            last_message[interaction.guild.id].children[1].disabled=(len(g_queue) == 0) and (song_status[str(message.guild.id)] not in [2,3])
                            msg = store_embed.get(interaction.guild.id)
                            msg.set_field_at(index=0,name=f'歌曲平台 | 名稱',value=f'{bot.get_emoji(1266320607520231445) if g_current_song["app"]=="yt" else bot.get_emoji(1294206903538155561)} | [{g_current_song["title"]}]({g_current_song["original_url"]})')
                            msg.set_field_at(index=1,name='歌曲長度',value=g_current_song['time'],inline=False)
                            msg.set_field_at(index=2,name='上傳作者',value=f"[{g_current_song['author']}]({g_current_song['channel_url']})",inline=False)
                            msg.set_field_at(index=3,name='點讚次數',value=g_current_song['like'],inline=False)
                            msg.set_field_at(index=4,name='觀看次數',value=g_current_song['view_count'],inline=False)
                            msg.set_field_at(index=5,name='上傳日期',value=(g_current_song['up_date'][:4]+' / '+g_current_song['up_date'][4:6]+' / '+g_current_song['up_date'][6:]),inline=False)
                            msg.set_field_at(index=6,name='點歌用戶',value=g_current_song['user'],inline=False)
                            msg.set_field_at(index=7,name='當前音量',value=int(audio_source.volume*100),inline=False)
                            msg.set_thumbnail(url=g_current_song['img_url']) 
                            await interaction.response.edit_message(content=cont,embed=msg,view=last_message[interaction.guild.id])

                        else:
                            last_message[interaction.guild.id].children[1].disabled=(len(g_queue) == 0) and (song_status[str(message.guild.id)] not in [2,3])
                            cont = f":white_check_mark: 已跳過{g_current_song['title']}\n{interaction.user.display_name}跳過了這首歌\n已經沒有歌曲正在排隊了喔！({period}{hour}:{minute})"
                            await interaction.response.edit_message(content=cont,view=last_message[interaction.guild.id])

                    else:
                        embed = discord.Embed(title=':x: 沒有音樂正在播放！', color=discord.Color.red())
                        await interaction.followup.send(embed=embed, ephemeral=True)


                elif status == 'turn':
                    status_text = {
                        1:"普通播放",
                        2:"單曲循環",
                        3:"隨機撥放"
                        }
                    status_found = False

                    for i,j in song_status.items():
                        if str(message.guild.id) == i:
                            status_found = True
                            j += 1
                            if j == 4:
                                j = 1
                            song_status[i] = j
                            break
                    if not status_found:#1 普通狀態,2 單首循環,3 隨機撥放
                        song_status.update(
                            {str(message.guild.id):2}
                            )
                        cont = f':white_check_mark: 成功把歌單狀態改變為 `{status_text.get(2)}`\n操作者:{interaction.user.display_name} ({period}{hour}:{minute})'

                    else:
                        cont = f':white_check_mark: 成功把歌單狀態改變為 `{status_text.get(j)}`\n操作者:{interaction.user.display_name} ({period}{hour}:{minute})'

                    embed = store_embed.get(interaction.guild.id)
                    last_message[interaction.guild.id].children[1].disabled=(len(g_queue) == 0) and (song_status[str(message.guild.id)] not in [2,3])
                    embed.set_field_at(index=8,name='播放狀態',value=status_text.get(song_status[str(message.guild.id)]),inline=False)
                    await interaction.response.edit_message(content=cont,view=last_message[interaction.guild.id],embed=embed)

                elif status == 'add':
                    g_current_song['user'] = interaction.user.display_name
                    g_queue.append(g_current_song)
                    
                    cont = f"{bot.get_emoji(1266320607520231445)} | 成功加入{g_current_song['title']}\n加入者:{interaction.user.display_name} ({period}{hour}:{minute})"
                    await interaction.response.edit_message(content=cont)
                    
                elif status == 'love':
                    async def love_1(interaction):
                        nonlocal selected_value
                        with open("love_music.json", 'r', encoding='utf-8') as m:
                            music = json.load(m)

                        if interaction.type == discord.InteractionType.component:
                            if isinstance(interaction.data, dict) and 'values' in interaction.data:
                                selected_value = int(interaction.data['values'][0])
                                content = f'選擇了`{music[str(interaction.user.id)][selected_value]["title"]}`\n請選擇一個操作'
                                view.remove_item(select)
                                await interaction.response.edit_message(content=content,view=view)

                            elif isinstance(interaction.data, dict) and 'custom_id' in interaction.data:
                                custom = interaction.data["custom_id"]
                                if custom == "add":
                                    with open("love_music.json", 'r', encoding='utf-8') as m:
                                        music = json.load(m)

                                    music[str(interaction.user.id)].append(g_current_song)
                                    embed = discord.Embed(
                                        title=':white_check_mark: 成功加入最愛',
                                        description=f'歌曲: {g_current_song["title"]} (在{period}{hour}:{minute})',
                                        color=randcolor()
                                    )
                                    await interaction.response.edit_message(embed=embed, view=None)

                                    with open("love_music.json", 'w', encoding='utf-8') as m:
                                        json.dump(music, m, indent=4, ensure_ascii=False)

                                else:
                                    if selected_value is not None:
                                        if custom == 'add_song':
                                            embed = discord.Embed(
                                                title=':white_check_mark: 成功加入此歌曲至歌單',
                                                description=f'歌曲: {g_current_song["title"]} (在{period}{hour}:{minute})', 
                                                color=randcolor()
                                            )
                                            g_queue.append(music[str(interaction.user.id)][selected_value]) 

                                        elif custom == 'del':
                                            embed = discord.Embed(
                                                title=f'成功刪除{music[str(interaction.user.id)][selected_value]["title"]}',
                                                description=f'在{period}{hour}:{minute}',
                                                color=randcolor()
                                            )
                                            music[str(interaction.user.id)].remove(music[str(interaction.user.id)][selected_value])

                                            with open("love_music.json", 'w', encoding='utf-8') as m:
                                                json.dump(music, m, indent=4, ensure_ascii=False)

                                        await interaction.response.edit_message(embed=embed, view=None,content='')
                                    else:
                                        await interaction.response.send_message('請先選擇一首歌！', ephemeral=True)



                    with open("love_music.json",'r',encoding='utf-8') as m:
                        music = json.load(m)

                    selected_value = None
                    g_current_song = current_song[message.guild.id]

                    if str(interaction.user.id) not in music or len(music[str(interaction.user.id)]) == 0:
                        music[str(interaction.user.id)] = []
                        music[str(interaction.user.id)].append(g_current_song)
                        hour,minute,period = time()
                        embed = discord.Embed(title=':white_check_mark: 成功加入最愛',description=f'歌曲:{g_current_song["title"]} (在{period}{hour}:{minute})',color=randcolor())
                        await interaction.response.send_message(embed=embed,ephemeral=True)
                        with open("love_music.json",'w',encoding='utf-8') as m:
                            json.dump(music, m, indent=4, ensure_ascii=False)
                        return

                    love_song = []
                    for idx,i in enumerate(music[str(interaction.user.id)]):
                        love_song.append(discord.SelectOption(label=i["title"],value=idx,description=i["time"]))

                    button_1 = Button(label='加入歌單',custom_id='add_song',style=discord.ButtonStyle.blurple)
                    button_2 = Button(label='刪除此歌',custom_id='del',style=discord.ButtonStyle.blurple)

                    check = False
                    for j in music[str(interaction.user.id)]:
                        if g_current_song["original_url"] == j["original_url"]:
                            check = True
                            break

                    view = View()
                    if not check and len(music[str(interaction.user.id)]):
                        button_3 = Button(label='加入目前正在撥放的歌至最愛',custom_id='add',style=discord.ButtonStyle.success,row=2)
                        view.add_item(button_3)
                        button_3.callback = love_1

                    select = discord.ui.Select(placeholder='選擇一首歌！',options=love_song)      
                    select.callback = love_1
                    view.add_item(select)

                    for i in [button_1,button_2]:
                        view.add_item(i)
                        i.callback = love_1

                    await interaction.response.send_message(view=view,ephemeral=True)

                elif status == 'history':
                    embeds = []
                    await interaction.response.defer(thinking=True ,ephemeral=True)
                    for idx, s in enumerate(reversed(song_history[interaction.guild.id]), start=1):
                        embed = discord.Embed(title=s["title"], url=s['original_url'], description=f'(第{idx}首)', color=randcolor())
                        embed.add_field(name="上傳作者", value=f"[{s['author']}]({s['channel_url']})", inline=False)
                        embed.add_field(name="歌曲長度", value=f"{s['time']}", inline=False)
                        embed.add_field(name="點歌用戶", value=f"{s['user']}", inline=False)
                        embed.set_image(url=s['img_url'])
                        embeds.append(embed)

                    for embed in embeds:
                        await interaction.followup.send(embed=embed, ephemeral=True)


                elif status == 'volume':
                    async def vol(self,interaction):
                        global volume,audio_source
                        if self.guild.id not in volume:
                            volume[self.guild.id] = [0.5]
                        try:
                            volume_v = int(interaction.children[0].value)
                            if 0 <= volume_v <= 100:
                                audio_source.volume = float(volume_v/100)
                                volume[self.guild.id][0] = float(volume_v/100)
                                cont = f':white_check_mark: 成功修改音量！\n{self.user.display_name}把音量修改到了**{volume_v if volume_v != 0 else "靜音"}** ({period}{hour}:{minute})'
                                embed = store_embed.get(self.guild.id)
                                embed.set_field_at(index=7,name='當前音量',value=int(audio_source.volume*100),inline=False)
                                await self.response.edit_message(content=cont,embed=embed)
                            else:
                                embed = discord.Embed(title=':x: 請輸入0~100的數字！',color=discord.Color.red())
                                await self.response.send_message(embed=embed,ephemeral=True)

                        except ValueError:
                            embed = discord.Embed(title=':x: 請輸入0~100的數字！',description=f'您輸入的"{interaction.children[0].value}"並非一串數字',color=discord.Color.red())
                            await self.response.send_message(embed=embed,ephemeral=True)
                            
                    fields = {
                    "input": {
                        "label": "請輸入要調整的音量(0~100)",
                        "placeholder": "0=靜音 50=原始音量 100=兩倍音量",
                        "required": True,
                        "default":int(audio_source.volume*100),
                        "max_length":3,
                        "min_length":1
                    }
                }
                    modal = create_modal("調整音量！", fields, vol)
                    await interaction.response.send_modal(modal)

            if last_message.get(message.guild.id) is not None:
                last_message.get(message.guild.id).stop()

            status_text = {
                1:"普通播放",
                2:"單曲循環",
                3:"隨機撥放"
                }
            embed = discord.Embed(title=f'目前正在撥放的歌曲訊息',color=randcolor())
            embed.add_field(name=f'歌曲平台 | 名稱',value=f'{bot.get_emoji(1266320607520231445) if g_current_song["app"]=="yt" else bot.get_emoji(1294206903538155561)} | [{g_current_song["title"]}]({g_current_song["original_url"]})',inline=False)
            embed.add_field(name='歌曲長度',value=g_current_song['time'],inline=False)
            embed.add_field(name='上傳作者',value=f"[{g_current_song['author']}]({g_current_song['channel_url']})",inline=False)
            embed.add_field(name='點讚次數',value=g_current_song['like'],inline=False)
            embed.add_field(name='觀看次數',value=g_current_song['view_count'],inline=False)
            embed.add_field(name='上傳日期',value=(g_current_song['up_date'][:4]+' / '+g_current_song['up_date'][4:6]+' / '+g_current_song['up_date'][6:]),inline=False)
            embed.add_field(name='點歌用戶',value=g_current_song['user'],inline=False)
            embed.add_field(name='當前音量',value=int(audio_source.volume*100),inline=False)
            embed.add_field(name='播放狀態',value=status_text.get(song_status[str(message.guild.id)]),inline=False)
            embed.set_thumbnail(url=g_current_song['img_url'])
            store_embed.update({message.guild.id:embed})
            view = View(timeout=None)
            stop_button = Button(label='⏯️ 暫停/繼續',custom_id='stop',style=discord.ButtonStyle.primary)
            contionue_button = Button(label='⏭️ 下一首',custom_id='continue',style=discord.ButtonStyle.primary,disabled=(len(g_queue) == 0) and (song_status[str(message.guild.id)] not in [2,3]))
            turn_button = Button(label='🔄 播放狀態',custom_id='turn',style=discord.ButtonStyle.primary)
            add_button = Button(label='➕ 加入目前歌單',custom_id='add',style=discord.ButtonStyle.primary)
            love_button = Button(label='❤️ 最愛清單',custom_id='love',style=discord.ButtonStyle.primary,row=1)
            history_button = Button(label='📜 歷史紀錄',custom_id='history',style=discord.ButtonStyle.primary,row=1)
            volume_button = Button(label='📢 調整音量',custom_id='volume',style=discord.ButtonStyle.primary,row=1)

            view.add_item(stop_button)
            view.add_item(contionue_button)
            view.add_item(turn_button)
            view.add_item(add_button)
            view.add_item(love_button)
            view.add_item(history_button)
            view.add_item(volume_button)

            for i in view.children:
                i.callback = song_setting

            await message.reply(embed=embed,view=view)
            last_message.update({message.guild.id:view})

        else:
            embed = discord.Embed(title=':x:目前沒有歌曲資訊！',color=discord.Color.red())
            await message.reply(embed=embed)
            
    elif '&content' == message.content:
        content = """
指令前綴& 如果指令是中文，則簡體繁體都有效

# &j &jo (join) &加入語音
>加入目前用戶所在語音房

# &l &le (leave) &退出語音
>退出目前用戶的語音房

# &p &pl (play) &播放
## ⭡播歌用這個！！！
>此指令必須在後面跟上連結或是搜尋歌名

目前只支援：
- yt單曲、歌單
- mixerbox歌單
- Spotify完全不支援
搜尋名稱有時候會不準確 建議打語歌曲相關的名稱

# &skip (skip) &跳過
>跳過這首歌 如果後面沒歌了就會直接結束

# &s &st (stop) &暫停
>暫停這首歌

# &r &re (resume) &繼續
>繼續暫停的歌

# &list (list) &佇列
>顯示目前正在排隊的歌(不包含當前播放的歌)

# &i (infomation) &訊息 &歌曲訊息
>顯示當前撥放歌曲的詳細訊息、以及大部分功能按鈕化(控制面板)

# 控制面板(用&i會跳出來)
以下有一些指令沒有的功能：

## -播放狀態：
    共有三種狀態：
    -普通輪播
    -單首循環
    -隨機撥放  
    預設是普通輪播，每按一次會切換到下一種狀態。

## -最愛清單：
    允許你珍藏喜歡的歌，以便你快速搜尋，加入歌單(上限25首)
    ※**只限定單曲，歌單暫不支援，有需要再做**

## -歷史紀錄
    列出上五首播的歌，以便你不知道聽了啥。

## -調整音量
    可以調整0~100 0為靜音，100為最大聲。

打算做但還沒做：
1.批量跳過(斟酌中)

注意事項：
1.整體使用體驗不如專業的音樂機器人(Ex.很多bug、使用不順) 意在中文化使用
2.有任何建議(或bug)歡迎提出
"""
        await message.channel.send(content=content)

    elif '+lot' in message.content and message.author.id == 579618807237312512:
        ch = bot.get_channel(int(message.content.split(' ')[1]))
        msg = await ch.fetch_message(int(message.content.split(' ')[2]))
        number = int(message.content.split(' ')[3])

        users = max(msg.reactions,key=lambda i:i.count)
        users = [user async for user in users.users()]
        lot_msg = f"得獎者 共{number}位:"
        for lot in range(number):
             lot_msg += f"\n{(users.pop(random.randint(0,len(users)-1))).display_name}\n"
        await message.reply(content=lot_msg)
        
    elif '!c' in message.content:
        go_urls = {
            "1356":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=135602",
            "1356A":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=1356A2",
        }

        back_urls = {
            "1356":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=135601",
            "1356A":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=1356A1",
            "1841":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=184102",
            "1841A":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=1841A2",
            "1841B":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=1841B2",
            "5250":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=525002",
            "5250A":"https://www.taiwanbus.tw/eBUSPage/Query/ws/getRData.ashx?type=4&key=5250A2"
        }

        def get_property(car):
            status = car["time"]
            if status == "進站中":
                return (0, 0)
            elif status == "將進站":
                return (1, 0)
            elif '分' in status:
                try:
                    return (2, int(status.replace("分", "")))
                except:
                    hours, minutes = map(int, status.replace("分", "").split(":"))
                    return (2,hours * 60 + minutes)
            else:
                if '發車' in status and status != '尚未發車':
                    try:
                        return (len(status),int(status.replace("發車", "")))
                    except:
                        hours, minutes = map(int,status.replace("發車", "").split(":"))
                        return (2,hours * 60 + minutes)
            
                else:
                    return (len(status),status)

        repo = "長榮 ⭢ 圓山\n車號\t時間\t\t發車數\n"
        car_list = []
        for road,car_info in back_urls.items():
            car_data = json.loads(requests.get(car_info, verify=False).text)
            car_list.append({
                "name":road,
                "len":len(car_data["cars"]),
                "time":car_data["data"][0]["ptime"]
                })

        car_list = sorted(car_list,key=get_property)
        for i in car_list:
            repo += f'{i["name"]}\t{i["time"]}\t{i["len"]}\n'

        repo += '-------------------\n圓山 ⭢ 長榮\n車號\t時間\t發車數\n'
        car_list = []
        for road,car_info in go_urls.items():
            car_data = json.loads(requests.get(car_info, verify=False).text)  
            car_list.append({
                "name":road,
                "len":len(car_data["cars"])
                }
            )
            for i in car_data["data"]:
                if i["na"] == "長榮":
                    car_list[-1].update({
                        "time":i["ptime"]
                        })
                    break

        car_list = sorted(car_list,key=get_property)

        for i in car_list:
            repo += f'{i["name"]}\t{i["time"]}\t{i["len"]}\n'

        await message.reply(repo)

    elif message.channel.id == 1287405276969832448 and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(".pdf"):
                pdf_path = f"./{attachment.filename}"
                await attachment.save(pdf_path)

                try:
                    pdf_document = fitz.open(pdf_path)
                    images = []
                    zoom_x = 2.0
                    zoom_y = 2.0 
                    matrix = fitz.Matrix(zoom_x, zoom_y)
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        pix = page.get_pixmap(matrix=matrix)
                        image_path = f"./page_{page_num + 1}.jpg"
                        pix.save(image_path)

                        images.append(discord.File(image_path))

                        if len(images) == 10:
                            await message.channel.send(files=images)
                            for img in images:
                                os.remove(img.fp.name)
                            images = []
                    if images:
                        await message.channel.send(files=images)
                        for img in images:
                            os.remove(img.fp.name)

                finally:
                    pdf_document.close()
                os.remove(pdf_path)

    coin = len(re.sub(re.compile(r'<:\w+:\d+>'), '', message.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), message.content))
    try:
        if any(entry["user_id"] == str(message.author.id) for entry in data):
            for entry in data:
                if entry["user_id"] == str(message.author.id):
                    entry["coin"] += coin
                    entry["gain"] += coin
                    entry["chat"] += coin
                    if (int(entry["gain"] / 1500) != entry["lvl"]):
                        entry["lvl"] = int(entry["gain"] / 1500)
    except:
        pass
    with open('user.json', 'w') as file, open('afk.json', 'w', encoding='utf-8') as file1:
        json.dump(data, file, indent=4)
        json.dump(afk, file1, indent=4, ensure_ascii=False)

@bot.event#根據刪除的訊息扣分
async def on_message_delete(message):
    with open('user.json', 'r') as file,open('afk.json','r',encoding='utf-8-sig') as file1:
       data = json.load(file)
       afk = json.load(file1)

    for user_id, dat in afk.items():
        if user_id == str(message.author.id):
            dat["afk_time"] += len(message.content)*5
    coin = len(re.sub(re.compile(r'<:\w+:\d+>'), '', message.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), message.content))
    if not message.author.bot:
        if any(entry["user_id"] == str(message.author.id) for entry in data):
          for entry in data:
            if entry["user_id"] == str(message.author.id):
               entry["coin"] -= coin
               entry["gain"] -= coin
               entry["chat"] -= coin
               if (int(entry["gain"]/1500)!= entry["lvl"]):
                    entry["lvl"] = int(entry["gain"]/1500)
    with open('user.json', 'w') as file,open('afk.json', 'w',encoding='utf-8') as file1:
        json.dump(data, file, indent=4)
        json.dump(afk, file1, indent=4,ensure_ascii=False)

@bot.event#根據編輯訊息改分
async def on_message_edit(before,after):
    with open('user.json', 'r') as file:
       data = json.load(file)
    beforelen = len(re.sub(re.compile(r'<:\w+:\d+>'), '', before.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), before.content))
    afterlen = len(re.sub(re.compile(r'<:\w+:\d+>'), '', after.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), after.content))

    if not before.author.bot:
        if any(entry["user_id"] == str(before.author.id) for entry in data):
          for entry in data:
            if entry["user_id"] == str(before.author.id):
                    entry["coin"] += afterlen - beforelen
                    entry["gain"] += afterlen - beforelen
                    entry["chat"] += afterlen - beforelen
            if (int(entry["gain"]/1500)!= entry["lvl"]):
                    entry["lvl"] = int(entry["gain"]/1500)

    with open('user.json', 'w') as file:
       json.dump(data, file, indent=4)

@bot.event#改暱稱監聽
async def on_member_update(before, after):
    if before.nick != after.nick:
        with open('afk.json', 'r', encoding='utf-8-sig') as file:
            afk = json.load(file)
        for user_id, data in afk.items():
            if data["display_name"] == (before.nick or before.display_name):
                data["display_name"] = after.nick or after.name
        with open('afk.json', 'w', encoding='utf-8') as file:
            json.dump(afk, file, indent=4, ensure_ascii=False)
            
@bot.event#加群組加入json
async def on_member_join(member):
    with open('afk.json', 'r', encoding='utf-8-sig') as file:
        afk = json.load(file)
    if member.guild.id == 972795227779772418:
        afk[str(member.id)]={
            "name":member.name,
            "display_name":member.display_name,
            "afk_time":0
            }
        with open('afk.json', 'w', encoding='utf-8-sig') as file:
            json.dump(afk, file, indent=4, ensure_ascii=False)

@bot.event#退出刪除
async def on_member_remove(member):
    with open('afk.json', 'r', encoding='utf-8-sig') as file:
        afk = json.load(file)
    for i in afk:
        if str(member.id) == i:
            afk.remove(i)
    with open('afk.json', 'w', encoding='utf-8-sig') as file:
            json.dump(afk, file, indent=4, ensure_ascii=False)

@bot.event#當退出or自動退出，清理歌單
async def on_voice_state_update(member, before, after):
    def clear_queue_and_current_song(guild_id):
        global queue,current_song,song_history,volume,song_status
        for i in [queue,current_song,song_history,song_status]:
            if guild_id in i:
                if isinstance(i[guild_id],list):
                    i[guild_id] = []
                elif isinstance(i[guild_id],dict):
                    i[guild_id] = {}
        volume[guild_id] = [0.5]

    if member == bot.user:
        if before.channel is not None and after.channel is None:
            clear_queue_and_current_song(member.guild.id)
    
    else:
        bot_voice_state = member.guild.voice_client
        if bot_voice_state is None or not bot_voice_state.channel:
            return
        
        if len(bot_voice_state.channel.members) == 1:
            await asyncio.sleep(180)
            
            if len(bot_voice_state.channel.members) == 1:
                await bot_voice_state.disconnect()
                clear_queue_and_current_song(member.guild.id)

bot.run(token='token')
