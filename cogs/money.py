import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from datetime import datetime
from utils.data_manager import load_data, save_data

class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Money cog đã sẵn sàng")

    @commands.slash_command(name="add", description="Thêm tiền cho người dùng", options=[
        create_option(name="user", description="Người dùng để thêm tiền", option_type=6, required=True),
        create_option(name="amount", description="Số tiền cần thêm", option_type=4, required=True)
    ])
    async def addmoney(self, ctx: SlashContext, user: discord.Member, amount: int):
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

    @commands.slash_command(name="subtract", description="Trừ tiền của người dùng", options=[
        create_option(name="user", description="Người dùng để trừ tiền", option_type=6, required=True),
        create_option(name="amount", description="Số tiền cần trừ", option_type=4, required=True)
    ])
    async def subtractmoney(self, ctx: SlashContext, user: discord.Member, amount: int):
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

    @commands.slash_command(name="check", description="Kiểm tra tổng tiền của người dùng", options=[
        create_option(name="user", description="Người dùng để kiểm tra tiền", option_type=6, required=True)
    ])
    async def checkmoney(self, ctx: SlashContext, user: discord.Member):
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

def setup(bot):
    bot.add_cog(Money(bot))
