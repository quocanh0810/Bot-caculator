import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from datetime import datetime
from utils.data_manager import load_data

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Leaderboard cog đã sẵn sàng")

    @commands.slash_command(name="leaderboard", description="Hiển thị bảng xếp hạng người dùng theo số tiền", options=[
        create_option(name="time_period", description="Chọn tháng và năm (MM/YYYY) hoặc toàn thời gian (all)", option_type=3, required=False),
        create_option(name="top", description="Số lượng người dùng muốn hiển thị", option_type=4, required=False)
    ])
    async def leaderboard(self, ctx: SlashContext, time_period: str = "all", top: int = 10):
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

def setup(bot):
    bot.add_cog(Leaderboard(bot))
