import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import json
import os
from datetime import datetime

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

data_file = "user_money.json"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user.name} đã sẵn sàng!')

#Add money
@slash.slash(name="add", 
             description="Thêm tiền cho người dùng", 
             options=[
                 create_option(
                     name="user",
                     description="Người dùng để thêm tiền",
                     option_type=6,
                     required=True
                 ),
                 create_option(
                     name="amount",
                     description="Số tiền cần thêm",
                     option_type=4,
                     required=True
                 )
             ])
async def addmoney(ctx: SlashContext, user: discord.Member, amount: int):
    try:
        guild_id = str(ctx.guild_id)
        user_id = str(user.id)
        data = load_data()

        if guild_id not in data:
            data[guild_id] = {}
        if user_id not in data[guild_id]:
            data[guild_id][user_id] = []

        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        data[guild_id][user_id].append({
            "amount": amount, 
            "timestamp": timestamp,
            "user_id": user_id,
            "user_name": user.name
        })
        save_data(data)

        formatted_amount = "{:,}".format(amount).replace(",", ".")
        await ctx.send(f'Đã thêm {formatted_amount} vnđ cho {user.name} vào {timestamp}.')
    except Exception as e:
        await ctx.send("Đã xảy ra lỗi khi thực hiện lệnh. Vui lòng thử lại sau.")
        print(f"Lỗi khi thực hiện lệnh addmoney: {e}")

#Subtract money
@slash.slash(name="subtract", 
             description="Trừ tiền của người dùng", 
             options=[
                 create_option(
                     name="user",
                     description="Người dùng để trừ tiền",
                     option_type=6,
                     required=True
                 ),
                 create_option(
                     name="amount",
                     description="Số tiền cần trừ",
                     option_type=4,
                     required=True
                 )
             ])
async def subtractmoney(ctx: SlashContext, user: discord.Member, amount: int):
    try:
        guild_id = str(ctx.guild_id)
        user_id = str(user.id)
        data = load_data()

        if guild_id not in data or user_id not in data[guild_id]:
            await ctx.send(f'{user.name} hiện có 0 vnđ.')
            return

        total_amount = sum(item['amount'] for item in data[guild_id][user_id])
        if total_amount < amount:
            await ctx.send(f'{user.name} không đủ số dư để trừ {amount} vnđ.')
            return

        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        data[guild_id][user_id].append({
            "amount": -amount, 
            "timestamp": timestamp,
            "user_id": user_id,
            "user_name": user.name
        })
        save_data(data)

        await ctx.send(f'Đã trừ {amount} vnđ của {user.name}.')
    except Exception as e:
        await ctx.send("Đã xảy ra lỗi khi thực hiện lệnh. Vui lòng thử lại sau.")
        print(f"Lỗi khi thực hiện lệnh subtractmoney: {e}")

#Check total money
@slash.slash(name="check", 
             description="Kiểm tra tổng tiền của người dùng", 
             options=[
                 create_option(
                     name="user",
                     description="Người dùng để kiểm tra tiền",
                     option_type=6,
                     required=True
                 )
             ])
async def checkmoney(ctx: SlashContext, user: discord.Member):
    try:
        guild_id = str(ctx.guild_id)
        user_id = str(user.id)
        data = load_data()

        if guild_id not in data or user_id not in data[guild_id]:
            await ctx.send(f'{user.name} hiện có 0 vnđ.')
            return

        total_amount = sum(item['amount'] for item in data[guild_id][user_id])
        formatted_total = "{:,}".format(total_amount).replace(",", ".")
        await ctx.send(f'{user.name} hiện có {formatted_total} vnđ.')
    except Exception as e:
        await ctx.send("Đã xảy ra lỗi khi thực hiện lệnh. Vui lòng thử lại sau.")
        print(f"Lỗi khi thực hiện lệnh checkmoney: {e}")

#Leaderboard by month/year and top...
@slash.slash(name="leaderboard", 
             description="Hiển thị bảng xếp hạng người dùng theo số tiền", 
             options=[
                 create_option(
                     name="time_period",
                     description="Chọn tháng và năm (MM/YYYY) hoặc toàn thời gian (all)",
                     option_type=3,
                     required=False
                 ),
                 create_option(
                     name="top",
                     description="Số lượng người dùng muốn hiển thị",
                     option_type=4,
                     required=False
                 )
             ])
async def leaderboard(ctx: SlashContext, time_period: str = "all", top: int = 10):
    try:
        await ctx.defer()
        
        guild_id = str(ctx.guild_id)
        data = load_data()

        if guild_id not in data:
            await ctx.send(f"Không có dữ liệu cho máy chủ này.")
            return

        user_totals = {}
        now = datetime.now()

        if time_period != "all":
            try:
                month, year = map(int, time_period.split('/'))
            except ValueError:
                await ctx.send(f"Định dạng không hợp lệ. Vui lòng sử dụng định dạng MM/YYYY.")
                return

        for user_id, transactions in data[guild_id].items():
            if time_period == "all":
                total = sum(item['amount'] for item in transactions)
                if total > 0:
                    user_totals[user_id] = total
            else:
                monthly_total = sum(
                    item['amount'] 
                    for item in transactions 
                    if datetime.strptime(item['timestamp'], "%d-%m-%Y %H:%M:%S").month == month and datetime.strptime(item['timestamp'], "%d-%m-%Y %H:%M:%S").year == year
                )
                if monthly_total > 0:
                    user_totals[user_id] = monthly_total

        sorted_users = sorted(user_totals.items(), key=lambda item: item[1], reverse=True)

        if not sorted_users:
            await ctx.send("Tháng này nghèo không có ai ủng hộ hết huhuhu!!")
            return

        leaderboard_message = f"Bảng xếp hạng ({'toàn thời gian' if time_period == 'all' else f'tháng {month}/{year}'}):\n"
        for i, (user_id, total_amount) in enumerate(sorted_users[:top], start=1):
            user = await ctx.guild.fetch_member(int(user_id))
            formatted_amount = "{:,}".format(total_amount).replace(",", ".")
            leaderboard_message += f"{i}. {user.name}: {formatted_amount} vnđ\n"

        await ctx.send(leaderboard_message)
    except Exception as e:
        await ctx.send("Đã xảy ra lỗi khi thực hiện lệnh. Vui lòng thử lại sau.")
        print(f"Lỗi khi thực hiện lệnh leaderboard: {e}")

#Token
bot.run('Token_Bot')
