# -*- coding: utf-8 -*-
# Author: Eduardo Borges
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
import time

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
   968026956367015976,#狗
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
            "舞者之書": 45,
            "魔法戰士之書": 15,
            "空氣": 20,
            "50萬眾神幣":10,
            "75萬眾神幣":10
            },

    "大獎": {
            "500萬眾神幣:star:": 20,
            "免費附魔一次:star:": 20,
            "暗黑之書/徒手書/詩人書/忍書 四選一:star:": 45,
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

async def check_voice_channels():
 while True:
  with open('user.json', 'r') as user_file, open('date.json', 'r') as date_file, open('item.json', 'r') as item_file,open('shop.json', 'r', encoding='utf-8') as file,open('product.json','r',encoding='utf-8') as file1:
   data = json.load(user_file)
   Data = json.load(date_file)
   item = json.load (item_file)
   shop = json.load(file)
   goods = json.load(file1) 

  if datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei')).day != Data[0]["today"]:
   for entry in data:
    entry["voice"] = 0
    entry["stream"] = 0
    entry["chat"] = 0
    entry["buy"] = 0
   weighted_choices = [(item, item_info[2]) for item, item_info in shop_item.items()]
   for i in range(1,4):
        selected_item = random.choices(weighted_choices, weights=[w for _, w in weighted_choices])[0][0]
        weighted_choices = [(item, weight) for item, weight in weighted_choices if item != selected_item]
        shop[f"slot{i}"]["item"] = selected_item
        shop[f"slot{i}"]["price"] = shop_item.get(selected_item)[0]-random.randint(0,100)*shop_item.get(selected_item)[1]
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
   Data[0]["today"]= datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei')).day


  for guild in bot.guilds:
   for channel in guild.voice_channels:
    members_in_channel = [member for member in channel.members]
    if len(members_in_channel) > 1:
     for member in members_in_channel:
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
            entry["lvl"] = int(entry["gain"]/1500)
          elif entry["voice"] < 3000 and member.voice.self_deaf == False:
            entry["gain"] += 30
            entry["voice"] += 30
            entry["coin"] += 30
            entry["lvl"] = int(entry["gain"]/1500)

  with open('user.json', 'w') as user_file, open('date.json', 'w') as date_file , open('item.json', 'w') as item_file,open('shop.json', 'w' ,encoding='utf-8') as file,open('product.json', 'w',encoding='utf-8') as file1:
   json.dump(data, user_file, indent=4)
   json.dump(Data, date_file, indent=4)
   json.dump(item, item_file, indent=4)
   json.dump(shop, file, indent=4, ensure_ascii=False)
   json.dump(goods, file1, indent=4,ensure_ascii=False)
  await asyncio.sleep(60)

@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"載入 {len(slash)} 個 slash")
    await bot.change_presence(
    status=discord.Status.idle,
    activity=discord.Streaming(
        name="Sleeping Simulator💤",
        url="https://www.youtube.com/watch?v=uHgt8giw1LY",
        details="爆肝打code🥹",
        type=discord.ActivityType.streaming,
    )
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

@bot.tree.command(name='付款', description='給予玩家鮭魚幣')
@app_commands.describe(用戶="收款人ID",鮭魚幣="要給予的金幣")
async def trade(interaction: discord.Interaction, 用戶: str, 鮭魚幣: int):
 with open('user.json', 'r') as file:
  data = json.load(file)
 User = discord.utils.get(bot.users, name=用戶)     
 check = interaction.user.id
 if User==None:
   embed = discord.Embed(title="錯誤", description=f"錯誤原因如下:")
   embed.add_field(name="• 無法獲得用戶名", value='',inline=False)
   embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
   embed.color = discord.Colour.red()
   await interaction.response.send_message(embed=embed,ephemeral=True)
 else:
  User = str(discord.utils.get(bot.users, name=用戶).id)
  button=Button(label="確認",custom_id="yes",style = discord.ButtonStyle.green)
  button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
  async def button_callback(interaction):
   custom = interaction.data['custom_id']
   if custom == "yes" and interaction.user.id == check:
      await interaction.message.delete()
      button3=Button(label="接受",custom_id="accept",style = discord.ButtonStyle.green)
      button4=Button(label="拒絕",custom_id="reject",style = discord.ButtonStyle.red)
      async def button_callback(interaction):
       if interaction.user.id == int(User):
           if any(entry["user_id"] == str(interaction.user.id) for entry in data) and 鮭魚幣>0 and (any(entry["user_id"] == str(check) and entry["coin"] >= 鮭魚幣 for entry in data)):
            for entry in data:
              if entry["user_id"] == str(check):
               custom = interaction.data['custom_id']
               if custom == "accept":
                entry["coin"]-=鮭魚幣
                for entry in data:
                  if entry["user_id"] == User:
                    entry["coin"]+=鮭魚幣
                    await interaction.message.delete()
                    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="支付成功！")
                    embed.add_field(name="付款人", value=bot.get_user(int(check)).mention,inline=False)
                    embed.add_field(name="收款人", value=bot.get_user(int(User)).mention,inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/957718579887894558.webp")
                    embed.add_field(name="支付了", value=f' {鮭魚幣} 鮭魚幣',inline=True)
                    embed.color = discord.Colour.green()
                    await interaction.channel.send(embed=embed)

               else:
                    await interaction.message.delete()
                    embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description="")
                    embed.add_field(name=" 交易取消 ", value='',inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1084797643017945088.webp")
                    embed.color = discord.Colour.yellow()
                    await interaction.response.send_message(embed=embed)

               with open('user.json', 'w') as file:
                    json.dump(data, file, indent=4)

           else:
            await interaction.message.delete()
            embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
            embed.add_field(name="• 收款人尚未登記", value='',inline=False)
            embed.add_field(name="• 付款人尚未登記", value='',inline=False)
            embed.add_field(name="• 輸入的玩家id有誤", value='',inline=False)
            embed.add_field(name="• 鮭魚幣不能<0", value='',inline=False)
            embed.add_field(name="• 鮭魚幣不足", value='',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed,ephemeral=True)

      button3.callback = button_callback
      button4.callback = button_callback
      view=View()
      view.add_item(button3)
      view.add_item(button4)
      embed = discord.Embed(title="交易確認", description="")
      embed.add_field(name=f"{bot.get_user(int(User))}", value=f' 是否接受 {interaction.user.mention} 的 {鮭魚幣} 鮭魚幣?',inline=True)
      embed.color = discord.Colour.yellow()
      embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/852727060593770556.webp")
      await interaction.channel.send(embed=embed , view=view)


   elif custom == "no" and interaction.user.id == check:
     await interaction.message.delete()

  button.callback = button_callback
  button2.callback = button_callback
  view=View()
  view.add_item(button)
  view.add_item(button2)
  embed = discord.Embed(title="付款確認", description=f"是否要附 {鮭魚幣} 鮭魚幣給 {bot.get_user(int(User)).mention} ?")
  embed.color = discord.Colour.dark_blue()
  await interaction.response.send_message(embed=embed , view=view)

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



@bot.tree.command(name='用戶資訊1',description='確認你的資訊')
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
    history[str(interaction.user.id)] = [None]
    history[str(interaction.user.id)][0] = {f"prize{i}": None for i in range(1, 11)}
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
              entry["coin"] += coin
              tf=True
              embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{bot.get_user(int(User)).name}的資訊如下:")
              embed.add_field(name="鮭魚幣", value=entry["coin"],inline=False)
              embed.add_field(name="陽壽(?)", value=entry["fortune"],inline=False)
              embed.add_field(name="總共取得的鮭魚幣", value=entry["gain"],inline=False)
              embed.add_field(name="存活年數", value=entry["lvl"],inline=False)
              embed.add_field(name="今日講話取得的鮭魚幣\n", value=entry["chat"],inline=False)
              embed.add_field(name="今日通話取得的鮭魚幣 ", value=f'{entry["voice"]} / 3000',inline=True)
              embed.add_field(name="今日直播取得的鮭魚幣 ", value=f'{entry["stream"]} / 5000',inline=True)
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

@bot.tree.command(name='抽獎',description='消耗陽壽抽獎')
@app_commands.choices(選擇獎池=[
  app_commands.Choice(name="一般獎池", value="norm_p"),
  app_commands.Choice(name="王石獎池(5陽壽一抽)", value="xtal_p"),
  app_commands.Choice(name="道具卡10連抽(5陽壽)", value="item_p"),
  ])
@app_commands.describe(陽壽="要投入的陽壽",選擇獎池="選擇一個獎池")
async def lottery(interaction: discord.Interaction,選擇獎池:app_commands.Choice[str],陽壽:int):
 with open('user.json', 'r') as file , open('history.json', 'r', encoding='utf-8') as file1 , open('air.json', 'r') as file2 , open('item.json', 'r', encoding='utf-8') as file3,open('lottery.json', 'r') as file4,open("xtal_lottery.json", "r", encoding="utf-8-sig") as file5:
  xtal = json.load(file5)
  data = json.load(file)
  history = json.load(file1)
  air = json.load(file2)
  item = json.load(file3)
  lottery = json.load(file4)
 prize = None
 gold = False
 if str(interaction.user.id) not in item:
  item[str(interaction.user.id)] = [{"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]

 if any(entry["user_id"] == str(interaction.user.id) for entry in data):
  for entry in data:
   if entry["user_id"] == str(interaction.user.id):
    if (陽壽<1 or 陽壽>10 or entry["fortune"] < 陽壽) and 選擇獎池.value == "norm_p":
     embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
     embed.add_field(name="• 投入的陽壽<0", value='',inline=False)
     embed.add_field(name="• 投入的陽壽>10", value='',inline=False)
     embed.add_field(name="• 陽壽不足", value='',inline=False)
     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
     embed.color = discord.Colour.red()
     await interaction.response.send_message(embed=embed,ephemeral=True)
    elif 選擇獎池.value == "norm_p":
     if str(interaction.user.id) not in lottery:
         lottery[str(interaction.user.id)] = [{"lot":0,"total":0}]
     embed1 = discord.Embed(title=f"{interaction.user.display_name}抽到了：", description=prize)
     embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}你得到了：")
     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/747551295489179778.gif")
     embed.color = discord.Colour.dark_gray()
     if any(entry["user_id"] == str(interaction.user.id) for entry in data):
        for entry in data:
            if entry["user_id"] == str(interaction.user.id):
                 entry["fortune"]-=陽壽
     for i in range(0, 陽壽):
         lottery[str(interaction.user.id)][0]["lot"] += 1
         lottery[str(interaction.user.id)][0]["total"] += 1
         pool = random.choices(["一般", "普通", "大獎"], weights=[percent["一般"], percent["普通"], percent["大獎"]])[0]
         if lottery[str(interaction.user.id)][0]["lot"] == 50 or lottery[str(interaction.user.id)][0]["lot"] == 75:#50 75小保
             extra_percent = {
                "一般": 0,
                "大獎": 15,
                "普通": 85
            }
             pool = random.choices(["一般", "普通", "大獎"], weights=[extra_percent["一般"], extra_percent["普通"], extra_percent["大獎"]])[0]
             if pool == "大獎":
                 lottery[str(interaction.user.id)][0]["lot"] = 0
         if lottery[str(interaction.user.id)][0]["lot"] > 90:#91開始提升機率 100必中大獎
             extra_percent = {
                "一般": percent["一般"] - 95*10-(75-lottery[str(interaction.user.id)][0]["lot"]),
                "大獎": percent["普通"] + 1*10-(75-lottery[str(interaction.user.id)][0]["lot"]),
                "普通": percent["大獎"] - 5*10-(75-lottery[str(interaction.user.id)][0]["lot"])
            }
             pool = random.choices(["一般", "普通", "大獎"], weights=[extra_percent["一般"], extra_percent["普通"], extra_percent["大獎"]])[0]
             if pool == "大獎":
                 lottery[str(interaction.user.id)][0]["lot"] = 0
                 gold = True

         prize = random.choices(list(Prize_pools[pool].keys()), weights=list(Prize_pools[pool].values()))[0]
         embed.add_field(name=f':gift:{prize}', value='----------',inline=False)
         if any(entry["user_id"] == str(interaction.user.id) for entry in air):
          for entry in air:
           if entry["user_id"] == str(interaction.user.id):
            if prize == "空氣":
              entry["air"] +=1
         else:
          new_data={
           "user_id" : str(interaction.user.id),
           "air" : 0
          }
          air.append(new_data)
          if prize == "空氣" and any(entry["user_id"] == str(interaction.user.id) for entry in air):
            for entry in air:
             if entry["user_id"] == str(interaction.user.id):
              entry["air"] +=1

         if str(interaction.user.id) not in history:
             history[str(interaction.user.id)] = []
             for i in range(1, 101):
                 history[str(interaction.user.id)].append({f"prize{i}": None})

         if history[str(interaction.user.id)][99]["prize100"] is not None:
            for i in range(2, 101):
                history[str(interaction.user.id)][i-2][f"prize{i-1}"] = history[str(interaction.user.id)][i-1][f"prize{i}"]
            history[str(interaction.user.id)][99]["prize100"] = prize

         for i in range(1, 101):
            if  history[str(interaction.user.id)][i-1][f"prize{i}"] is None:
                history[str(interaction.user.id)][i-1][f"prize{i}"] = prize
                break

         if prize.startswith("鮭魚幣"):
           if any(entry["user_id"] == str(interaction.user.id) for entry in data):
             for entry in data:
              if entry["user_id"] == str(interaction.user.id):
                coins = int(prize.split("鮭魚幣")[1])
                entry["coin"] += coins
                entry["gain"] += coins
         elif prize != "空氣":
           embed1.add_field(name=prize, value='',inline=False)
        
     await bot.get_channel(1183431186161340466).send(embed=embed1)
     if gold == True:
         if 陽壽>1:
            await interaction.response.send_message('https://cdn.discordapp.com/attachments/815780487708540990/1198602167448244274/hqzyh-7kjbx.gif')
         else:
            await interaction.response.send_message('https://cdn.discordapp.com/attachments/815780487708540990/1198602203569590332/4dmly-jeaoz.gif')
         time.sleep(5.7)
         await interaction.edit_original_response(embed=embed,content='')
     else:
         await interaction.response.send_message(embed=embed)

    elif (陽壽 != 5 or entry["fortune"] < 陽壽 or item[str(interaction.user.id)][0]["lottery"] == True) and 選擇獎池.value == "item_p":
        embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
        embed.add_field(name="• 投入的陽壽只能是5", value='',inline=False)
        embed.add_field(name="• 陽壽不足", value='',inline=False)
        embed.add_field(name="• 你今天已經10連抽過了！", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.color = discord.Colour.red()
        await interaction.response.send_message(embed=embed,ephemeral=True)

    elif 選擇獎池.value == "item_p":
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
    elif ((陽壽 %5 != 0 and 陽壽/5 < 25 ) or entry["fortune"] < 陽壽) and 選擇獎池.value == "xtal_p":
        embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
        embed.add_field(name="• 投入的陽壽只能是5", value='',inline=False)
        embed.add_field(name="• 陽壽不足", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        await interaction.response.send_message(embed=embed,ephemeral=True)
    else:
        entry["fortune"] -= 陽壽
        weight = list(xtal.values())
        embed = discord.Embed(title="__𝗥𝗲𝘀𝘂𝗹𝘁__", description=f"{interaction.user.mention}你得到了：")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/747551295489179778.gif")
        embed.color = discord.Colour.dark_gray()
        embed1 = discord.Embed(title=f"{interaction.user.display_name}抽到了：", description="")
        for num in range(0, int(陽壽/5)):
            lott = random.choices(list(xtal.keys()), weights=weight)[0]
            embed.add_field(name=lott,value='',inline=False)
            embed1.add_field(name=lott,value='',inline=False)
        await interaction.response.send_message(embed=embed)    
        await bot.get_channel(1183431186161340466).send(embed=embed1)


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
@app_commands.describe(用戶名="要增加的人的名字",欲加的身分組名稱="要增加的身分組的名字",顯示身分組顏色="是否要顯示身分組顏色",啟用必中="額外消耗兩張迴轉卡")
async def role(interaction: discord.Interaction,用戶名:str,欲加的身分組名稱:str,顯示身分組顏色: app_commands.Choice[str], 啟用必中: app_commands.Choice[str]):
 with open('item.json', 'r') as file:
  item = json.load(file)
 test = discord.utils.get(interaction.user.guild.roles, name=欲加的身分組名稱)
 test1 = None
 if test != None:
     test1 = test.name
     if str(test.id) not in item:
        item[str(test.id)] = [{"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 if str(interaction.user.id) not in item:
     item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 if discord.utils.get(interaction.guild.members, name=用戶名) != None:
   if item[str(test.id)][0]["protect"] == False:
     User = discord.utils.get(interaction.guild.members, name=用戶名)
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

 else:
     embed = discord.Embed(title="錯誤", description="錯誤原因如下:")
     embed.add_field(name="• 找不到用戶名字", value='',inline=False)
     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
     embed.color = discord.Colour.red()
     await interaction.response.send_message(embed=embed,ephemeral=True)

 if 欲加的身分組名稱 == test1 and test1 not in do_not_role:
  role = discord.utils.get(interaction.guild.roles, name=欲加的身分組名稱)
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
       embed.add_field(name=f"{interaction.user.display_name} 你被加了 {role} 身分組", value='',inline=False)
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
async def nick(interaction:discord.Interaction,用戶名:str,暱稱:str, 啟用必中: app_commands.Choice[str]):
 with open('item.json', 'r') as file:
  item = json.load(file)
 if str(interaction.user.id) not in item:
  item[str(interaction.user.id)] = [{"trans": 0, "nick": 2, "role": 0, "add_role": 0,"protect":False,"lottery":False,"role_tem":None,"role_date":None}]
 test = discord.utils.get(interaction.user.guild.members, name=用戶名)
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

@bot.tree.command(name="每日商店查看",description="每日商店")
async def shop(interaction: discord.Interaction):
    with open('shop.json', 'r', encoding='utf-8') as file:
     shop = json.load(file)
    embed = discord.Embed(title="每日商店", description=f"{interaction.user.mention}今天的商品如下:")
    embed.color = discord.Colour.dark_blue()
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/980979727324053536.webp")
    for i in range(1,4):
        embed.add_field(name="----------", value=f'欄位{number_word.get(i)}:\n**道具名:** {shop[f"slot{i}"]["item"]}\n**價格:** {shop[f"slot{i}"]["price"]}',inline=False)
    embed.add_field(name="----------", value='',inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="每日商店購買",description="購買物品")
@app_commands.describe(欄位="商品的欄位")
async def shop_buy(interaction: discord.Interaction,欄位:int):
     with open('shop.json', 'r', encoding='utf-8') as file,open('user.json', 'r') as file1:
        shop = json.load(file)
        data = json.load(file1)
     find=False
     check = interaction.user.id
     if 欄位>3 or 欄位<1:
        embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
        embed.add_field(name="• 這個欄位無法購買", value='',inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
        embed.color = discord.Colour.red()
        await interaction.response.send_message(embed=embed,ephemeral=True)
     else:
        if any(entry["user_id"] == str(interaction.user.id) for entry in data):
            for entry in data:
                if entry["user_id"] == str(interaction.user.id):
                    find = True
                    break

        if find == False:
            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
            embed.add_field(name="• 用戶尚未登記(請先使用**/用戶資訊**)", value='',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif entry["coin"] < shop[f"slot{欄位}"]["price"]:
            print(entry["coin"],"   ",shop[f"slot{欄位}"]["price"])
            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
            embed.add_field(name="• 鮭魚幣不足", value='',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif entry["buy"] > 0:
            embed = discord.Embed(title="錯誤！", description="錯誤原因如下:")
            embed.add_field(name="• 一天只能買一次商品", value='',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = discord.Colour.red()
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            button=Button(label="確認",custom_id="yes",style = discord.ButtonStyle.green)
            button2=Button(label="取消",custom_id="no",style = discord.ButtonStyle.red)
            async def button_callback(interaction):
                 custom = interaction.data['custom_id']
                 if custom == "no" and check == interaction.user.id:
                     embed = discord.Embed(title="購買結果", description="")
                     embed.add_field(name="購買取消", value="",inline=False)
                     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
                     embed.color = discord.Colour.dark_blue()
                     await interaction.response.edit_message(content="",embed=embed,view=None)
                 if custom == "yes" and check == interaction.user.id:
                     entry["buy"] +=1
                     if shop[f"slot{欄位}"]["item"].find('陽壽') != -1:
                        fort = shop[f"slot{欄位}"]["item"][:shop[f"slot{欄位}"]["item"].find('陽壽')]
                        entry["fortune"] += int(fort)
                        entry["coin"] -= shop[f"slot{欄位}"]["price"]
                     else:
                        entry["coin"] -= shop[f"slot{欄位}"]["price"]
                        embed1 = discord.Embed(title=f"{interaction.user.display_name}買了：", description=shop[f"slot{欄位}"]["item"])
                        await bot.get_channel(1183431186161340466).send(embed=embed1)
                     embed = discord.Embed(title="購買結果", description="")
                     embed.add_field(name="購買成功！", value="你購買了",inline=False)
                     embed.add_field(name="商品", value=shop[f"slot{欄位}"]["item"],inline=False)
                     embed.add_field(name="價格", value=shop[f"slot{欄位}"]["price"],inline=False)
                     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1075897670029287455.gif")
                     embed.color = discord.Colour.green()
                     await interaction.response.edit_message(content="",embed=embed,view=None)

                     with open('shop.json', 'w' ,encoding='utf-8') as file,open('user.json', 'w') as file1:
                          json.dump(shop, file, indent=4, ensure_ascii=False)
                          json.dump(data, file1, indent=4)


            view = View()
            button.callback = button_callback
            button2.callback = button_callback
            view=View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title="購買確認", description='是否要購買這個商品?')
            embed.add_field(name="商品", value=shop[f"slot{欄位}"]["item"],inline=False)
            embed.add_field(name="價格", value=shop[f"slot{欄位}"]["price"],inline=False)
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/597781420408176650.webp')
            
            embed.color = discord.Colour.dark_blue()
            await interaction.response.send_message(embed=embed , view=view,ephemeral=True)

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

@bot.tree.command(name="板子",description=" ")
async def board(interaction:discord.Integration):
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

@bot.event#根據字數加分
async def on_message(message):
    with open('user.json', 'r') as file:
       data = json.load(file)
    coin = len(re.sub(re.compile(r'<:\w+:\d+>'), '', message.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), message.content))
    if any(entry["user_id"] == str(message.author.id) for entry in data):
      for entry in data:
        if entry["user_id"] == str(message.author.id):
           entry["coin"] += coin
           entry["gain"] += coin
           entry["chat"] += coin
           if (int(entry["gain"]/1500) != entry["lvl"]):
               entry["lvl"] = int(entry["gain"]/1500)
    with open('user.json', 'w') as file:
       json.dump(data, file, indent=4)

@bot.event#根據刪除的訊息扣分
async def on_message_delete(message):
    with open('user.json', 'r') as file:
       data = json.load(file)
    coin = len(re.sub(re.compile(r'<:\w+:\d+>'), '', message.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), message.content))
    if any(entry["user_id"] == str(message.author.id) for entry in data):
      for entry in data:
        if entry["user_id"] == str(message.author.id):
           entry["coin"] -= coin
           entry["gain"] -= coin
           entry["chat"] -= coin
           if (int(entry["gain"]/1500)!= entry["lvl"]):
                entry["lvl"] = int(entry["gain"]/1500)
    with open('user.json', 'w') as file:
       json.dump(data, file, indent=4)

@bot.event#根據編輯訊息改分
async def on_message_edit(before,after):
    with open('user.json', 'r') as file:
       data = json.load(file)
    beforelen = len(re.sub(re.compile(r'<:\w+:\d+>'), '', before.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), before.content))
    afterlen = len(re.sub(re.compile(r'<:\w+:\d+>'), '', after.content)) + len(re.findall(re.compile(r'<:\w+:\d+>'), after.content))

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

bot.run(token='token')
