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
async def roll(ctx, bet: str = None): # Đổi thành str để nhận chữ 'all'
    player = await get_player(ctx.author.id)
    
    if bet is None:
        return await ctx.send(f"🎲 **Cách dùng:** `>roll <số_tiền_hoặc_all>`\n*Ví dụ: `>roll 50k` hoặc `>roll all`*")
        
    # Xử lý quy đổi tiền cược (Đưa vào số cash hiện tại của player)
    try:
        bet_amount = parse_bet_amount(bet, player["cash"])
    except ValueError:
        return await ctx.send("❌ Số tiền cược không hợp lệ! Hãy nhập số hoặc chữ viết tắt (`100k`, `all`).")
        
    # Kiểm tra điều kiện đặt cược
    if bet_amount <= 0:
        return await ctx.send("❌ Số tiền đặt cược phải lớn hơn 0!")
        
    if player["cash"] < bet_amount:
        return await ctx.send(f"❌ Bạn không đủ tiền! Số dư hiện tại: **{player['cash']:,} Cash**.")

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
async def slot(ctx, bet: str = None):
    player = await get_player(ctx.author.id)
    
    if bet is None:
        return await ctx.send(f"🎲 **Cách dùng:** `>roll <số_tiền_hoặc_all>`\n*Ví dụ: `>roll 50k` hoặc `>roll all`*")
        
    # Xử lý quy đổi tiền cược (Đưa vào số cash hiện tại của player)
    try:
        bet_amount = parse_bet_amount(bet, player["cash"])
    except ValueError:
        return await ctx.send("❌ Số tiền cược không hợp lệ! Hãy nhập số hoặc chữ viết tắt (`100k`, `all`).")
        
    # Kiểm tra điều kiện đặt cược
    if bet_amount <= 0:
        return await ctx.send("❌ Số tiền đặt cược phải lớn hơn 0!")
        
    if player["cash"] < bet_amount:
        return await ctx.send(f"❌ Bạn không đủ tiền! Số dư hiện tại: **{player['cash']:,} Cash**.")

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

# ================= LỆNH ADMIN BUFF (GIỮ NGUYÊN GỐC - CHỈ THÊM CHỮ ALL) =================
@bot.command()
async def buff(ctx, target: str = None, amount: str = None):
    # 1. Kiểm tra quyền Admin
    if ctx.author.id not in ADMINS:
        return await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        
    if target is None:
        return await ctx.send(
            "👑 **Cách dùng lệnh Buff Admin:**\n"
            "🔹 `>buff all <số_lượng>` -> Tự buff tất cả chỉ số cho chính mình.\n"
            "🔹 `>buff @User <số_lượng>` -> Buff các chỉ số cho người được tag.\n"
            "*Ví dụ: `>buff all 50k` hoặc `>buff @NguyễnVănA 1m`*"
        )

    # --- XỬ LÝ CHỮ 'ALL' ĐỂ GIỮ NGUYÊN CHỨC NĂNG BAN ĐẦU ---
    # Nếu gõ 'all', hệ thống tự hiểu mục tiêu (target_member) chính là người dùng lệnh
    if target.lower() == "all":
        target_member = ctx.author
    else:
        # Nếu không phải 'all', kiểm tra lượt tag tên như cũ
        if not ctx.message.mentions:
            return await ctx.send("❌ Vui lòng tag (mention) người chơi cần buff hoặc gõ `all` để tự buff!")
        target_member = ctx.message.mentions[0]

    # Kiểm tra tham số số lượng nhập vào
    if amount is None:
        return await ctx.send("❌ Vui lòng nhập số lượng muốn buff!")

    # Quy đổi số lượng (Hỗ trợ gõ tắt 100k, 1m...)
    try:
        buff_value = parse_bet_amount(amount, 0)
    except ValueError:
        return await ctx.send("❌ Định dạng số lượng buff không hợp lệ!")

    # 2. CHẠY TIẾP CÁC CHỨC NĂNG BAN ĐẦU CỦA BẠN VỚI 'target_member'
    # (Đoạn này chạy tất cả logic buff chỉ số ban đầu của bạn cho target_member)
    player = await get_player(target_member.id)
    
    player["cash"] += buff_value
    player["luck"] += buff_value
    player["jackpot"] += buff_value
    player["win_streak"] += buff_value
    
    leveled_up = add_xp(player, buff_value)
    await save_player(player)
    
    if leveled_up:
        await ctx.send(f"🎉 {target_member.mention} đã thăng lên Level {player['level']}!")

    # Tạo Embed hiển thị kết quả ban đầu của bạn
    embed = discord.Embed(
        title="👑 ADMIN BUFF SYSTEM 👑",
        description=f"Admin đã kích hoạt quyền năng buff chỉ số cho {target_member.mention}!",
        color=discord.Color.purple()
    )
    embed.add_field(name="💰 Cash", value=f"+{buff_value:,}", inline=True)
    embed.add_field(name="📈 XP", value=f"+{buff_value:,}", inline=True)
    embed.add_field(name="🍀 Luck", value=f"+{buff_value:,}", inline=True)
    embed.add_field(name="🎰 Jackpot", value=f"+{buff_value:,}", inline=True)
    embed.add_field(name="🔥 Win Streak", value=f"+{buff_value:,}", inline=True)
    
    return await ctx.send(embed=embed)
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

# ===== View xử lý nút bấm giật tiền của Cashrain =====
class CashRainView(discord.ui.View):
    def __init__(self, total_pool: int, max_claims: int, duration: float):
        super().__init__(timeout=duration)
        self.total_pool = total_pool
        self.max_claims = max_claims  # Nếu là 0 hoặc None tức là Cả Server được nhận
        self.claimed_users = {}       # Lưu user_id: số tiền nhận được
        self.remaining_pool = total_pool
        
    @discord.ui.button(label="💰 GIẬT TIỀN NGAY! 💰", style=discord.ButtonStyle.success, custom_id="claim_cashrain")
    async def claim_cashrain(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # 1. Kiểm tra xem user đã nhận chưa (Chế độ nào cũng chỉ được bấm 1 lần)
        if user_id in self.claimed_users:
            return await interaction.response.send_message("❌ Bạn đã nhặt tiền từ cơn mưa này rồi, đừng tham lam thế chứ!", ephemeral=True)
            
        # 2. Kiểm tra nếu là chế độ GIỚI HẠN NGƯỜI và đã hết lượt
        if self.max_claims > 0 and len(self.claimed_users) >= self.max_claims:
            button.disabled = True
            button.label = "💸 Đã bị giật sạch!"
            button.style = discord.ButtonStyle.secondary
            await interaction.message.edit(view=self)
            return await interaction.response.send_message("😢 Ôi không! Cơn mưa tiền đã bị mọi người nhặt hết sạch rồi!", ephemeral=True)
            
        # 3. Tính toán số tiền người chơi nhận được dựa theo chế độ
        if self.max_claims == 0:
            # CHẾ ĐỘ CẢ SERVER: Nhận ngẫu nhiên từ 1% đến 5% tổng hũ của Admin
            min_pick = max(1, int(self.total_pool * 0.01))
            max_pick = max(1, int(self.total_pool * 0.05))
            cash_received = random.randint(min_pick, max_pick)
            self.remaining_pool -= cash_received
        else:
            # CHẾ ĐỘ GIỚI HẠN: Chia hũ giảm dần kịch tính
            remaining_slots = self.max_claims - len(self.claimed_users)
            if remaining_slots == 1:
                cash_received = self.remaining_pool
            else:
                max_pick = int(self.remaining_pool / remaining_slots * 1.5)
                min_pick = max(1, int(self.remaining_pool / remaining_slots * 0.5))
                cash_received = random.randint(min_pick, max_pick)
                if cash_received > self.remaining_pool:
                    cash_received = self.remaining_pool
            self.remaining_pool -= cash_received

        # 4. Cập nhật vào Cache và Database của người chơi
        player = await get_player(user_id)
        player["cash"] += cash_received
        self.claimed_users[user_id] = cash_received
        await save_player(player)
        
        # 5. Phản hồi riêng tư cho người bấm nút
        await interaction.response.send_message(f"🎉 Bạn đã giật được **+{cash_received:,} Cash** từ cơn mưa tiền!", ephemeral=True)
        
        # 6. Kiểm tra nếu hết lượt ngay sau khi người này nhận (Chỉ áp dụng với chế độ giới hạn)
        if self.max_claims > 0 and len(self.claimed_users) >= self.max_claims:
            button.disabled = True
            button.label = "💸 Đã bị giật sạch!"
            button.style = discord.ButtonStyle.secondary
            
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.red()
            embed.description = "🌧️ **CƠN MƯA TIỀN ĐÃ KẾT THÚC!**\nToàn bộ số tiền đã được phát hết sạch!"
            
            # Liệt kê danh sách người ăn đậm nhất (Top 10 người)
            leaderboard = ""
            sorted_claims = sorted(self.claimed_users.items(), key=lambda x: x[1], reverse=True)
            for idx, (u_id, amt) in enumerate(sorted_claims[:10], 1):
                u = bot.get_user(u_id)
                u_name = u.mention if u else f"Người chơi {u_id}"
                leaderboard += f"{idx}. {u_name}: +{amt:,} Cash\n"
            if leaderboard:
                embed.add_field(name="🏆 Top nhận thưởng lớn nhất:", value=leaderboard, inline=False)
                
            await interaction.message.edit(embed=embed, view=self)

def parse_bet_amount(val_str: str, current_cash: int) -> int:
    """Quy đổi tiền cược từ chuỗi (100k, 2m, all) thành số nguyên int cụ thể."""
    if val_str is None:
        raise ValueError("Thiếu số tiền cược.")
        
    val_str = str(val_str).strip().lower()
    
    # Nếu người dùng chọn tất tay
    if val_str == "all":
        return current_cash
        
    multipliers = {'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000}
    
    if val_str[-1] in multipliers:
        unit = val_str[-1]
        number_part = val_str[:-1]
        try:
            return int(float(number_part) * multipliers[unit])
        except ValueError:
            raise ValueError("Định dạng tiền cược không hợp lệ.")
            
    return int(float(val_str))
    
@bot.command()
async def cashrain(ctx, total_pool: str = None, max_claims: str = None): # Chuyển total_pool thành str để không bị lỗi Discord
    # 1. Kiểm tra quyền Admin
    if ctx.author.id not in ADMINS:
        return await ctx.send("❌ Bạn không có thẩm quyền để tạo ra cơn mưa tiền!")
        
    # 2. Hướng dẫn sử dụng nếu thiếu tham số tổng tiền hũ
    if total_pool is None:
        return await ctx.send(
            "🌧️ **Cách dùng lệnh Cashrain:**\n"
            "🔹 `>cashrain <tổng_tiền>` -> **Cả Server cùng được nhận** ngẫu nhiên.\n"
            "🔹 `>cashrain <tổng_tiền> <số_người>` -> Chỉ giới hạn số lượng người nhanh tay nhất.\n"
            "*Ví dụ: `>cashrain 500k` hoặc `>cashrain 10m 5` hoặc `>cashrain 400000 10`*"
        )
        
    # --- XỬ LÝ CHUYỂN ĐỔI SỐ TIỀN HŨ ---
    try:
        pool_amount = parse_abbreviated_number(total_pool)
    except ValueError:
        return await ctx.send("❌ Định dạng số tiền tổng hũ không hợp lệ! Hãy nhập số thường hoặc viết tắt dạng `100k`, `2m`, `1.5m`...")

    if pool_amount <= 0:
        return await ctx.send("❌ Số tiền cược phải lớn hơn 0!")

    # --- XỬ LÝ THAM SỐ SỐ NGƯỜI TỐI ĐA NHẬN ---
    claims_limit = 0  # 0 nghĩa là vô hạn (Cả server)
    if max_claims is not None:
        try:
            # Người dùng cũng có thể nhập giới hạn người dạng số thường
            claims_limit = int(max_claims)
            if claims_limit <= 0:
                return await ctx.send("❌ Số lượng người nhận giới hạn phải lớn hơn 0!")
        except ValueError:
            return await ctx.send("❌ Số lượng người nhận giới hạn phải là một con số nguyên hợp lệ!")

    duration = 60.0  # Cơn mưa tồn tại trong 60 giây
    
    # --- TÍNH TOÁN THỜI GIAN ĐẾM NGƯỢC ---
    end_timestamp = int(datetime.now(timezone.utc).timestamp() + duration)
    countdown_tag = f"<t:{end_timestamp}:R>"

    # 3. Thiết lập thông tin Embed theo chế độ
    embed = discord.Embed(
        title="🌧️💸 CƠN MƯA TIỀN TỆ ĐÃ XUẤT HIỆN! 💸🌧️",
        description=f"Admin {ctx.author.mention} đang thả một cơn mưa tiền khổng lồ vào kênh chat!\nHãy nhanh tay nhấn vào nút dưới đây để nhặt tiền!",
        color=discord.Color.gold()
    )
    embed.add_field(name="💰 Tổng giá trị hũ tiền", value=f"**{pool_amount:,} Cash**", inline=True)
    
    if claims_limit == 0:
        embed.add_field(name="👥 Số suất nhận thưởng", value="**🌍 CẢ SERVER** (Mỗi người 1 lượt)", inline=True)
    else:
        embed.add_field(name="👥 Số suất nhận thưởng", value=f"**{claims_limit} người** nhanh tay nhất", inline=True)
        
    embed.add_field(name="⏳ Thời gian còn lại", value=f"Sự kiện sẽ kết thúc {countdown_tag}", inline=False)
    embed.set_footer(text="Hệ thống tự động chia ngẫu nhiên số tiền nhặt được!")
    
    # Khởi tạo View với pool_amount đã được ép kiểu thành số int thành công
    view = CashRainView(pool_amount, claims_limit, duration)
    
    # Gửi tin nhắn sự kiện kèm Nút Bấm công khai
    rain_msg = await ctx.send(content="@here 🎉 SỰ KIỆN CASHRAIN!", embed=embed, view=view)
    
    # Chờ hết thời gian chạy lệnh
    await asyncio.sleep(duration)
    
    # Sau khi hết thời gian, đóng nút lại nếu chưa bị đóng trước đó
    if not view.children[0].disabled:
        view.children[0].disabled = True
        view.children[0].label = "⏰ Đã hết thời gian!"
        view.children[0].style = discord.ButtonStyle.secondary
        
        embed.color = discord.Color.dark_gray()
        embed.description = "🌧️ **CƠN MƯA TIỀN ĐÃ KẾT THÚC!**\nThời gian nhặt tiền đã khép lại."
        embed.set_field_at(2, name="⏳ Thời gian còn lại", value="🔴 **Đã hết giờ!**", inline=False)
        
        # Sắp xếp và hiển thị bảng xếp hạng những người nhặt được nhiều nhất
        leaderboard = ""
        sorted_claims = sorted(view.claimed_users.items(), key=lambda x: x[1], reverse=True)
        for idx, (u_id, amt) in enumerate(sorted_claims[:10], 1):
            u = bot.get_user(u_id)
            u_name = u.mention if u else f"Người chơi {u_id}"
            leaderboard += f"{idx}. {u_name}: +{amt:,} Cash\n"
            
        if leaderboard:
            embed.add_field(name="🏆 Bảng vinh danh nhặt tiền (Top 10):", value=leaderboard, inline=False)
        else:
            embed.add_field(name="🏆 Kết quả:", value="Không có ai tham gia nhặt tiền trong đợt này.", inline=False)
            
        await rain_msg.edit(embed=embed, view=view)
        
if token is None:
    print("❌ Lỗi: Không tìm thấy biến TOKEN trong file .env!")
else:
    print("✅ Đang khởi chạy Bot bằng TOKEN tìm thấy...")
    bot.run(token)
