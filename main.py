import random
import asyncio
import os
import json
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

prefix = ">"
intents = discord.Intents.all()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

# Hàm tính toán cộng EXP và xử lý Lên Cấp
def add_xp(player, amount):
    player["xp"] += amount
    leveled_up = False
    while player["xp"] >= player["level"] * 100:
        player["xp"] -= player["level"] * 100
        player["level"] += 1
        leveled_up = True
    return leveled_up

DATA_GUILD_ID = 1514179127354069053
DATA_CHANNEL_ID = 1514179128004313212
player_cache = {}

@bot.event
async def on_ready():
    bot.add_view(UpgradeView())
    print(f"✅ Đăng nhập thành công: {bot.user}")

    channel = bot.get_channel(DATA_CHANNEL_ID)
    if channel is None:
        print("❌ Không tìm thấy kênh dữ liệu!")
        return

    player_cache.clear()
    async for msg in channel.history(limit=None, oldest_first=True):
        try:
            data = json.loads(msg.content)
            if "user_id" not in data:
                continue
            # Chuyển đổi dữ liệu cũ nếu còn sót lose_streak sang win_streak
            if "lose_streak" in data:
                data.pop("lose_streak")
            if "win_streak" not in data:
                data["win_streak"] = 0

            data["_message_id"] = msg.id
            player_cache[data["user_id"]] = data
        except Exception as e:
            print(f"Lỗi đọc dữ liệu: {e}")

    print(f"📂 Đã tải {len(player_cache)} người chơi vào hệ thống Cache.")

async def create_player(user_id):
    channel = bot.get_channel(DATA_CHANNEL_ID)
    data = {
        "user_id": user_id,
        "cash": 1000,
        "xp": 0,
        "level": 1,
        "luck": 0,
        "jackpot": 0,
        "win_streak": 0,
        "last_daily": ""
    }
    message = await channel.send(json.dumps(data))
    data["_message_id"] = message.id
    player_cache[user_id] = data
    return data

async def get_player(user_id):
    if user_id in player_cache:
        return player_cache[user_id]

    channel = bot.get_channel(DATA_CHANNEL_ID)
    async for msg in channel.history(limit=None, oldest_first=True):
        try:
            data = json.loads(msg.content)
            if data.get("user_id") == user_id:
                if "win_streak" not in data:
                    data["win_streak"] = 0
                data["_message_id"] = msg.id
                player_cache[user_id] = data
                return data
        except:
            continue
    return await create_player(user_id)

async def save_player(player):
    channel = bot.get_channel(DATA_CHANNEL_ID)
    message_id = player["_message_id"]
    message = await channel.fetch_message(message_id)
    
    save_data = dict(player)
    save_data.pop("_message_id")
    
    await message.edit(content=json.dumps(save_data))
    player_cache[player["user_id"]] = player

async def load_all_players():
    channel = bot.get_channel(DATA_CHANNEL_ID)
    player_cache.clear()
    async for msg in channel.history(limit=None, oldest_first=True):
        try:
            data = json.loads(msg.content)
            if "user_id" not in data:
                continue
            if "win_streak" not in data:
                data["win_streak"] = 0
            data["_message_id"] = msg.id
            player_cache[data["user_id"]] = data
        except:
            pass

# ================= LỆNH ROLL =================
@bot.command()
async def roll(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Số tiền cược phải lớn hơn 0!")

    player = await get_player(ctx.author.id)
    if player["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền để đặt cược!")

    # BẮT ĐẦU TRỪ TIỀN CƯỢC TRƯỚC KHI QUAY
    player["cash"] -= amount

    luck = player.get("luck", 0)
    jackpot = player.get("jackpot", 0)
    win_streak = player.get("win_streak", 0)

    # Thiết lập tỷ lệ
    win_rate = 45 + (luck * 0.5)
    jackpot_rate = 2 + (jackpot * 0.2)

    # Cơ chế cứu trợ bí mật khi sắp cạn ví
    if player["cash"] <= 1000:
        win_rate += 15

    msg = await ctx.send("🎲 Đang lắc xúc xắc...")
    frames = ["🎲 ⚪⚪⚪", "🎲 🔴⚪⚪", "🎲 🔴🔴⚪", "🎲 🔴🔴🔴"]
    for frame in frames:
        await asyncio.sleep(0.6)
        await msg.edit(content=frame)

    roll_number = random.uniform(0, 100)

    # 1. TRÚNG JACKPOT
    if roll_number <= jackpot_rate:
        reward = amount * 10
        player["cash"] += reward
        player["win_streak"] += 1
        
        # Tính toán EXP thưởng chuỗi thắng
        base_xp = 25
        bonus_xp = player["win_streak"] * 5 if player["win_streak"] >= 3 else 0
        total_xp = base_xp + bonus_xp
        
        leveled_up = add_xp(player, total_xp)
        await save_player(player)

        if leveled_up:
            await ctx.send(f"🎉 {ctx.author.mention} đã xuất sắc thăng lên Level {player['level']}!")

        streak_text = f"🔥 Chuỗi thắng: {player['win_streak']} (Bonus +{bonus_xp} EXP)" if player["win_streak"] >= 3 else ""
        return await msg.edit(
            content=f"💥 **JACKPOT** 💥\n\n🎉 {ctx.author.mention}\n💰 +{reward:,} Cash\n✨ +{total_xp} EXP {streak_text}"
        )

    # 2. TRÚNG GIẢI THẮNG THƯỜNG
    elif roll_number <= win_rate:
        multiplier = random.choice([1.2, 1.5, 2.0])
        reward = int(amount * multiplier)
        
        player["cash"] += reward
        player["win_streak"] += 1

        # Tính toán EXP thưởng chuỗi thắng
        base_xp = 25
        bonus_xp = player["win_streak"] * 5 if player["win_streak"] >= 3 else 0
        total_xp = base_xp + bonus_xp

        leveled_up = add_xp(player, total_xp)
        await save_player(player)

        if leveled_up:
            await ctx.send(f"🎉 {ctx.author.mention} đã xuất sắc thăng lên Level {player['level']}!")

        streak_text = f"🔥 Chuỗi thắng: {player['win_streak']} (Bonus +{bonus_xp} EXP)" if player["win_streak"] >= 3 else ""
        return await msg.edit(
            content=f"🎉 **THẮNG!**\n\n🎲 Hệ số: x{multiplier}\n💰 +{reward:,} Cash\n✨ +{total_xp} EXP {streak_text}"
        )

    # 3. THUA CUỘC
    else:
        player["win_streak"] = 0  # Gãy chuỗi, reset về 0
        
        # Bảo hiểm phá sản tối thiểu 100 xu
        if player["cash"] < 100:
            player["cash"] = 100

        # Thua vẫn được nhận 15 EXP an ủi
        leveled_up = add_xp(player, 15)
        await save_player(player)

        if leveled_up:
            await ctx.send(f"🎉 {ctx.author.mention} đã xuất sắc thăng lên Level {player['level']}!")

        return await msg.edit(
            content=f"💀 **THUA CUỘC!**\n\n💸 Bạn đã mất sạch {amount:,} Cash tiền cược.\n📉 Chuỗi thắng bị bẻ gãy!"
        )

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("🎲 Cách dùng: `>roll <số tiền>`\nVí dụ: `>roll 1000`")

# ================= LỆNH SLOT =================
@bot.command()
async def slot(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Số tiền cược phải lớn hơn 0!")

    player = await get_player(ctx.author.id)
    if player["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ Cash để đặt cược!")

    # BẮT ĐẦU TRỪ TIỀN CƯỢC TRƯỚC KHI QUAY
    player["cash"] -= amount

    luck = player.get("luck", 0)
    jackpot = player.get("jackpot", 0)
    
    emojis = ["🍒", "🍋", "🍇", "💎", "⭐"]
    msg = await ctx.send("🎰 Đang quay hũ...")

    # Hiệu ứng chạy màn hình Slot
    for _ in range(6):
        e1, e2, e3 = random.choices(emojis, k=3)
        await msg.edit(content=f"🎰 | {e1} | {e2} | {e3} |")
        await asyncio.sleep(0.3)

    jackpot_rate = 1 + (jackpot * 0.3)
    win_bonus = 0
    if player["cash"] <= 1000:
        win_bonus += 10

    rng = random.uniform(0, 100)

    # 1. ⭐⭐⭐ SLOT JACKPOT
    if rng <= jackpot_rate:
        result = ["⭐", "⭐", "⭐"]
        reward = amount * 20
        player["cash"] += reward
        player["win_streak"] += 1

        base_xp = 40
        bonus_xp = player["win_streak"] * 5 if player["win_streak"] >= 3 else 0
        total_xp = base_xp + bonus_xp

        leveled_up = add_xp(player, total_xp)
        await save_player(player)

        if leveled_up:
            await ctx.send(f"🎉 {ctx.author.mention} đã xuất sắc thăng lên Level {player['level']}!")

        streak_text = f"🔥 Chuỗi thắng: {player['win_streak']} (Bonus +{bonus_xp} EXP)" if player["win_streak"] >= 3 else ""
        return await msg.edit(
            content=f"💥 **JACKPOT TRÚNG LỚN** 💥\n🎰 | ⭐ | ⭐ | ⭐ |\n\n💰 +{reward:,} Cash\n✨ +{total_xp} EXP {streak_text}"
        )

    # 2. 💎💎💎 SIÊU THẮNG
    elif rng <= 5 + win_bonus + luck:
        result = ["💎", "💎", "💎"]
        reward = amount * 10
        player["cash"] += reward
        player["win_streak"] += 1

        base_xp = 25
        bonus_xp = player["win_streak"] * 5 if player["win_streak"] >= 3 else 0
        total_xp = base_xp + bonus_xp

        leveled_up = add_xp(player, total_xp)
        await save_player(player)

        streak_text = f"🔥 Chuỗi thắng: {player['win_streak']} (Bonus +{bonus_xp} EXP)" if player["win_streak"] >= 3 else ""
        return await msg.edit(
            content=f"💎 **SIÊU THẮNG** 💎\n🎰 | 💎 | 💎 | 💎 |\n\n💰 +{reward:,} Cash\n✨ +{total_xp} EXP {streak_text}"
        )

    # 3. 🍒🍒🍒 THẮNG LỚN
    elif rng <= 15 + win_bonus + luck:
        result = ["🍒", "🍒", "🍒"]
        reward = amount * 5
        player["cash"] += reward
        player["win_streak"] += 1

        base_xp = 15
        bonus_xp = player["win_streak"] * 5 if player["win_streak"] >= 3 else 0
        total_xp = base_xp + bonus_xp

        leveled_up = add_xp(player, total_xp)
        await save_player(player)

        streak_text = f"🔥 Chuỗi thắng: {player['win_streak']} (Bonus +{bonus_xp} EXP)" if player["win_streak"] >= 3 else ""
        return await msg.edit(
            content=f"🎉 **THẮNG LỚN!**\n🎰 | 🍒 | 🍒 | 🍒 |\n\n💰 +{reward:,} Cash\n✨ +{total_xp} EXP {streak_text}"
        )

    # 4. 🍋🍋🍋 THẮNG THƯỜNG
    elif rng <= 30 + win_bonus + luck:
        result = ["🍋", "🍋", "🍋"]
        reward = amount * 2
        player["cash"] += reward
        player["win_streak"] += 1

        base_xp = 10
        bonus_xp = player["win_streak"] * 5 if player["win_streak"] >= 3 else 0
        total_xp = base_xp + bonus_xp

        leveled_up = add_xp(player, total_xp)
        await save_player(player)

        streak_text = f"🔥 Chuỗi thắng: {player['win_streak']} (Bonus +{bonus_xp} EXP)" if player["win_streak"] >= 3 else ""
        return await msg.edit(
            content=f"✨ **THẮNG!**\n🎰 | 🍋 | 🍋 | 🍋 |\n\n💰 +{reward:,} Cash\n✨ +{total_xp} EXP {streak_text}"
        )

    # 5. THUA CUỘC
    else:
        result = random.choices(emojis, k=3)
        player["win_streak"] = 0  # Reset chuỗi thắng về 0
        
        if player["cash"] < 100:
            player["cash"] = 100

        leveled_up = add_xp(player, 10)
        await save_player(player)

        if leveled_up:
            await ctx.send(f"🎉 {ctx.author.mention} đã xuất sắc thăng lên Level {player['level']}!")

        return await msg.edit(
            content=f"💀 **THUA CUỘC!**\n🎰 | {result[0]} | {result[1]} | {result[2]} |\n\n💸 Mất sạch {amount:,} Cash.\n📉 Chuỗi thắng quay về 0."
        )

# ===== Hệ thống Nút Bấm Nâng Cấp =====
class UpgradeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🍀 Nâng Luck", style=discord.ButtonStyle.green, custom_id="upgrade_luck")
    async def upgrade_luck(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await get_player(interaction.user.id)
        cost = (player["luck"] + 1) * 1000

        if player["cash"] < cost:
            return await interaction.response.send_message(f"❌ Bạn không đủ tiền! Cần {cost:,} Cash", ephemeral=True)

        player["cash"] -= cost
        player["luck"] += 1
        await save_player(player)
        await interaction.response.send_message(f"🍀 Nâng cấp thành công! Chỉ số Luck hiện tại: {player['luck']}", ephemeral=True)

    @discord.ui.button(label="💎 Nâng Jackpot", style=discord.ButtonStyle.blurple, custom_id="upgrade_jackpot")
    async def upgrade_jackpot(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await get_player(interaction.user.id)
        cost = (player["jackpot"] + 1) * 2000

        if player["cash"] < cost:
            return await interaction.response.send_message(f"❌ Bạn không đủ tiền! Cần {cost:,} Cash", ephemeral=True)

        player["cash"] -= cost
        player["jackpot"] += 1
        await save_player(player)
        await interaction.response.send_message(f"💎 Nâng cấp thành công! Chỉ số Jackpot hiện tại: {player['jackpot']}", ephemeral=True)

# ===== CÁC LỆNH HIỂN THỊ & ADMIN =====
@bot.command()
async def start(ctx):
    player = await get_player(ctx.author.id)
    need_xp = player["level"] * 100

    embed = discord.Embed(title="🎮 THÔNG TIN NGƯỜI CHƠI", color=discord.Color.gold())
    embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
    embed.add_field(name="💰 Cash", value=f"{player['cash']:,}", inline=True)
    embed.add_field(name="⭐ Level", value=player["level"], inline=True)
    embed.add_field(name="📈 XP", value=f"{player['xp']}/{need_xp}", inline=True)
    embed.add_field(name="🍀 Luck", value=player["luck"], inline=True)
    embed.add_field(name="💎 Jackpot Thêm", value=player["jackpot"], inline=True)
    embed.add_field(name="🔥 Chuỗi Thắng", value=player.get("win_streak", 0), inline=True)
    embed.set_footer(text="Nhấn nút bên dưới để tiến hành gia tăng sức mạnh")

    await ctx.send(embed=embed, view=UpgradeView())

def get_rank(level):
    if level >= 100: return "👑 Huyền Thoại"
    elif level >= 75: return "💎 Đại Cao Thủ"
    elif level >= 50: return "🔥 Cao Thủ"
    elif level >= 25: return "⚔️ Chiến Binh"
    elif level >= 10: return "⭐ Kẻ Phiêu Lưu"
    return "🌱 Tân Thủ"

@bot.command()
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    if member.bot:
        return await ctx.send("❌ Không thể xem hồ sơ của hệ thống Bot.")

    player = await get_player(member.id)
    need_xp = player["level"] * 100

    embed = discord.Embed(title=f"👤 Hồ sơ của {member.display_name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="💰 Cash", value=f"{player['cash']:,}", inline=True)
    embed.add_field(name="⭐ Level", value=player["level"], inline=True)
    embed.add_field(name="📈 XP", value=f"{player['xp']}/{need_xp}", inline=True)
    embed.add_field(name="🍀 Luck", value=player["luck"], inline=True)
    embed.add_field(name="💎 Jackpot", value=player["jackpot"], inline=True)
    embed.add_field(name="🔥 Chuỗi Thắng", value=player.get("win_streak", 0), inline=True)
    embed.add_field(name="🏆 Danh hiệu", value=get_rank(player["level"]), inline=False)
    embed.set_footer(text=f"ID Người dùng: {member.id}")

    await ctx.send(embed=embed)

@bot.command()
async def toplvl(ctx):
    await load_all_players()
    sorted_players = sorted(player_cache.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)

    text = ""
    for index, (user_id, data) in enumerate(sorted_players[:10], start=1):
        user = bot.get_user(int(user_id))
        name = user.name if user else f"Người chơi {user_id}"
        text += f"{index}. **{name}** (Lv.{data['level']} - 🔥 Chuỗi: {data.get('win_streak', 0)})\n"

    embed = discord.Embed(title="🏆 BẢNG XẾP HẠNG CAO THỦ (LEVEL)", description=text, color=discord.Color.gold())
    await ctx.send(embed=embed)

ADMINS = [1195361246195757118, 1335606447144173610]

@bot.command()
async def buff(ctx, stat=None, target=None, amount=None):
    if ctx.author.id not in ADMINS:
        return await ctx.send("❌ Bạn không có thẩm quyền sử dụng lệnh này!")

    if stat is None:
        return await ctx.send("Cách dùng:\n`>buff cash @user 1000`\n`>buff win_streak @user 5`")

    if amount is None:
        try: value = int(target)
        except: return await ctx.send("❌ Giá trị không hợp lệ!")
        member = ctx.author
    else:
        if not ctx.message.mentions:
            return await ctx.send("❌ Vui lòng gắn thẻ (mention) người nhận!")
        member = ctx.message.mentions[0]
        try: value = int(amount)
        except: return await ctx.send("❌ Giá trị không hợp lệ!")

    if member.bot:
        return await ctx.send("❌ Không thể can thiệp chỉ số của Bot!")

    player = await get_player(member.id)
    
    # Cập nhật mảng chỉ số hợp lệ sau khi đổi sang win_streak
    valid_stats = ["cash", "xp", "level", "luck", "jackpot", "win_streak"]

    if stat.lower() not in valid_stats:
        return await ctx.send(f"❌ Chỉ số hợp lệ bao gồm: {', '.join(valid_stats)}")

    player[stat.lower()] += value
    if player[stat.lower()] < 0:
        player[stat.lower()] = 0

    await save_player(player)

    embed = discord.Embed(title="🛠️ HỆ THỐNG ADMIN BUFF", color=discord.Color.green())
    embed.add_field(name="👤 Người nhận", value=member.mention, inline=False)
    embed.add_field(name="📊 Chỉ số điều chỉnh", value=stat, inline=True)
    embed.add_field(name="➕ Lượng điều chỉnh", value=value, inline=True)
    embed.add_field(name="📈 Trạng thái hiện tại", value=player[stat.lower()], inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def reset(ctx, member: discord.Member = None):
    if ctx.author.id not in ADMINS:
        return await ctx.send("❌ Bạn không có quyền hạn dùng lệnh này!")

    if member is None:
        return await ctx.send("Cách dùng: `>reset @user`")

    if member.bot:
        return await ctx.send("❌ Không thể đặt lại dữ liệu của Bot!")

    player = await get_player(member.id)
    player["cash"] = 1000
    player["xp"] = 0
    player["level"] = 1
    player["luck"] = 0
    player["jackpot"] = 0
    player["win_streak"] = 0
    player["last_daily"] = ""

    await save_player(player)

    embed = discord.Embed(title="🔄 THIẾT LẬP LẠI NGƯỜI CHƠI", color=discord.Color.red())
    embed.add_field(name="👤 Đối tượng", value=member.mention, inline=False)
    embed.add_field(name="💰 Cash", value="1,000", inline=True)
    embed.add_field(name="⭐ Level", value="1", inline=True)
    embed.add_field(name="🔥 Chuỗi thắng", value="0", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    player = await get_player(ctx.author.id)
    
    # Lấy thời gian hiện tại (Múi giờ UTC)
    now = datetime.now(timezone.utc)
    
    # KIỂM TRA QUYỀN ADMIN: Nếu không phải Admin thì mới bị check 12 giờ
    if ctx.author.id not in ADMINS:
        last_daily_str = player.get("last_daily", "")
        
        if last_daily_str:
            last_daily_time = datetime.fromisoformat(last_daily_str)
            time_passed = now - last_daily_time
            
            # Nếu chưa đủ 12 giờ
            if time_passed < timedelta(hours=12):
                time_remaining = timedelta(hours=12) - time_passed
                hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                return await ctx.send(
                    f"❌ **{ctx.author.display_name}** ơi, bạn đã điểm danh rồi!\n"
                    f"⏳ Hãy quay lại sau: **{hours} giờ {minutes} phút {seconds} giây** nữa nhé."
                )

    # Thưởng tiền và EXP khi điểm danh thành công
    daily_cash = 500  
    daily_xp = 30     
    
    player["cash"] += daily_cash
    
    # Cập nhật thời gian điểm danh mới (Admin dùng thì vẫn cập nhật nhưng ván sau không bị check)
    player["last_daily"] = now.isoformat()
    
    # Cộng EXP và kiểm tra lên cấp
    leveled_up = add_xp(player, daily_xp)
    await save_player(player)
    
    if leveled_up:
        await ctx.send(f"🎉 {ctx.author.mention} đã xuất sắc thăng lên Level {player['level']}!")

    # Tạo giao diện thông báo
    embed = discord.Embed(
        title="☀️ ĐIỂM DANH HÀNG NGÀY",
        description=f"Chúc mừng **{ctx.author.display_name}** đã điểm danh thành công!",
        color=discord.Color.green()
    )
    
    # Thêm dòng đánh dấu nếu là Admin đang "hack" lệnh
    if ctx.author.id in ADMINS:
        embed.description += "\n👑 *(Chế độ Admin: Đã bỏ qua giới hạn 12 giờ)*"

    embed.add_field(name="💰 Tiền thưởng", value=f"+{daily_cash:,} Cash", inline=True)
    embed.add_field(name="📈 Kinh nghiệm", value=f"+{daily_xp} EXP", inline=True)
    embed.add_field(name="💳 Ví hiện tại", value=f"{player['cash']:,} Cash", inline=False)
    embed.set_footer(text="Hẹn gặp lại bạn sau 12 giờ nữa!")
    
    await ctx.send(embed=embed)
    
if token is None:
    print("❌ Lỗi: Không tìm thấy biến TOKEN trong file .env!")
else:
    print("✅ Đang khởi chạy Bot bằng TOKEN tìm thấy...")
    bot.run(token)
