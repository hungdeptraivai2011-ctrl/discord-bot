import random
import asyncio
import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

prefix = ">"
intents = discord.Intents.all()

intents = discord.Intents.all()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

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

    print(f"✅ Đăng nhập: {bot.user}")

    channel = bot.get_channel(DATA_CHANNEL_ID)

    if channel is None:
        print("❌ Không tìm thấy kênh dữ liệu!")
        return

    player_cache.clear()

    async for msg in channel.history(limit=None):

        try:
            data = json.loads(msg.content)

            if "user_id" not in data:
                continue

            data["_message_id"] = msg.id

            player_cache[data["user_id"]] = data

        except:
            pass

    print(
        f"📂 Đã tải {len(player_cache)} người chơi"
    )


async def create_player(user_id):

    channel = bot.get_channel(DATA_CHANNEL_ID)

    data = {
        "user_id": user_id,
        "cash": 1000,
        "xp": 0,
        "level": 1,
        "luck": 0,
        "jackpot": 0,
        "lose_streak": 0
    }

    message = await channel.send(
        json.dumps(data)
    )

    data["_message_id"] = message.id

    player_cache[user_id] = data

    return data


async def get_player(user_id):

    if user_id in player_cache:
        return player_cache[user_id]

    return await create_player(user_id)


async def save_player(player):

    channel = bot.get_channel(DATA_CHANNEL_ID)

    message_id = player["_message_id"]

    message = await channel.fetch_message(
        message_id
    )

    save_data = dict(player)

    save_data.pop("_message_id")

    await message.edit(
        content=json.dumps(save_data)
    )

    player_cache[player["user_id"]] = player

@bot.event
async def on_ready():
    print(f"✅ Đăng nhập: {bot.user}")

@bot.command()
async def roll(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0!")

    player = await get_player(ctx.author.id)

    if player["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền!")

    leveled_up = add_xp(player, 10)

    if leveled_up:
        await ctx.send(
            f"🎉 {ctx.author.mention} đã lên Level {player['level']}!"
        )

    luck = player.get("luck", 0)
    jackpot = player.get("jackpot", 0)
    lose_streak = player.get("lose_streak", 0)

    # Tỉ lệ cơ bản
    win_rate = 45
    jackpot_rate = 2

    # Luck
    win_rate += luck * 0.5

    # Pity system
    win_rate += min(lose_streak * 3, 25)

    # Sắp hết tiền
    if player["cash"] <= 1000:
        win_rate += 15

    # Jackpot stat
    jackpot_rate += jackpot * 0.2

    msg = await ctx.send("🎲 Đang lắc xúc xắc...")

    frames = [
        "🎲 ⚪⚪⚪",
        "🎲 🔴⚪⚪",
        "🎲 🔴🔴⚪",
        "🎲 🔴🔴🔴"
    ]

    for frame in frames:
        await asyncio.sleep(0.8)
        await msg.edit(content=frame)

    roll_number = random.uniform(0, 100)

    # JACKPOT
    if roll_number <= jackpot_rate:
        reward = amount * 10

        player["cash"] += reward
        player["lose_streak"] = 0
        player["xp"] += 25

        await await save_player(player)

        return await msg.edit(
            content=
            f"💥 JACKPOT 💥\n\n"
            f"🎉 {ctx.author.mention}\n"
            f"💰 +{reward:,} Cash"
        )

    # THẮNG
    elif roll_number <= win_rate:
        multiplier = random.choice([
            1.2,
            1.5,
            2
        ])

        reward = int(amount * multiplier)

        player["cash"] += reward
        player["lose_streak"] = 0
        player["xp"] += 10

        await await save_player(player)

        return await msg.edit(
            content=
            f"🎉 THẮNG!\n\n"
            f"🎲 Hệ số: x{multiplier}\n"
            f"💰 +{reward:,} Cash"
        )

    # THUA
    else:
        player["cash"] -= amount

        if player["cash"] < 100:
            player["cash"] = 100

        player["lose_streak"] += 1
        player["xp"] += 5

        await await save_player(player)

        return await msg.edit(
            content=
            f"💀 THUA!\n\n"
            f"💸 -{amount:,} Cash\n"
            f"🔥 Chuỗi thua: {player['lose_streak']}"
        )

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "🎲 Cách dùng: `>roll <số tiền>`\n"
            "Ví dụ: `>roll 1000`"
        )

@bot.command()
async def slot(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0!")

    player = await get_player(ctx.author.id)

    if player["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ Cash!")

    luck = player.get("luck", 0)
    jackpot = player.get("jackpot", 0)
    lose_streak = player.get("lose_streak", 0)

    emojis = ["🍒", "🍋", "🍇", "💎", "⭐"]

    msg = await ctx.send("🎰 Đang quay...")

    # Animation
    for _ in range(8):
        e1 = random.choice(emojis)
        e2 = random.choice(emojis)
        e3 = random.choice(emojis)

        await msg.edit(
            content=f"🎰 | {e1} | {e2} | {e3} |"
        )

        await asyncio.sleep(0.4)

    # Tỉ lệ
    jackpot_rate = 1 + (jackpot * 0.3)
    win_bonus = min(lose_streak * 2, 20)

    if player["cash"] <= 1000:
        win_bonus += 10

    rng = random.uniform(0, 100)

    # ⭐⭐⭐ JACKPOT
    if rng <= jackpot_rate:
        result = ["⭐", "⭐", "⭐"]
        reward = amount * 20

        player["cash"] += reward
        player["lose_streak"] = 0
        
        leveled_up = add_xp(player, 40)

    if leveled_up:
        await ctx.send(
            f"🎉 {ctx.author.mention} đã lên Level {player['level']}!"
        )

        await await save_player(player)

        return await msg.edit(
            content=
            f"💥 JACKPOT 💥\n"
            f"🎰 | ⭐ | ⭐ | ⭐ |\n\n"
            f"💰 +{reward:,} Cash"
        )

    # 💎💎💎
    elif rng <= 5 + win_bonus + luck:
        result = ["💎", "💎", "💎"]
        reward = amount * 10

        player["cash"] += reward
        player["lose_streak"] = 0
        player["xp"] += 25

        await await save_player(player)

        return await msg.edit(
            content=
            f"💎 SIÊU THẮNG 💎\n"
            f"🎰 | 💎 | 💎 | 💎 |\n\n"
            f"💰 +{reward:,} Cash"
        )

    # 🍒🍒🍒
    elif rng <= 15 + win_bonus + luck:
        result = ["🍒", "🍒", "🍒"]
        reward = amount * 5

        player["cash"] += reward
        player["lose_streak"] = 0
        player["xp"] += 15

        await await save_player(player)

        return await msg.edit(
            content=
            f"🎉 THẮNG LỚN!\n"
            f"🎰 | 🍒 | 🍒 | 🍒 |\n\n"
            f"💰 +{reward:,} Cash"
        )

    # 🍋🍋🍋
    elif rng <= 30 + win_bonus + luck:
        result = ["🍋", "🍋", "🍋"]
        reward = amount * 2

        player["cash"] += reward
        player["lose_streak"] = 0
        player["xp"] += 10

        await await save_player(player)

        return await msg.edit(
            content=
            f"✨ THẮNG!\n"
            f"🎰 | 🍋 | 🍋 | 🍋 |\n\n"
            f"💰 +{reward:,} Cash"
        )

    # THUA
    else:
        result = [
            random.choice(emojis),
            random.choice(emojis),
            random.choice(emojis)
        ]

        player["cash"] -= amount

        if player["cash"] < 100:
            player["cash"] = 100

        player["lose_streak"] += 1
        player["xp"] += 5

        await await save_player(player)

        return await msg.edit(
            content=
            f"💀 THUA!\n"
            f"🎰 | {result[0]} | {result[1]} | {result[2]} |\n\n"
            f"💸 -{amount:,} Cash\n"
            f"🔥 Chuỗi thua: {player['lose_streak']}"
        )

import discord
from discord.ext import commands

# ===== Buttons =====

class UpgradeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🍀 Nâng Luck",
        style=discord.ButtonStyle.green
    )
    async def upgrade_luck(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        player = get_player(interaction.user.id)

        cost = (player["luck"] + 1) * 1000

        if player["cash"] < cost:
            return await interaction.response.send_message(
                f"❌ Cần {cost:,} Cash",
                ephemeral=True
            )

        player["cash"] -= cost
        player["luck"] += 1

        save_player(interaction.user.id, player)

        await interaction.response.send_message(
            f"🍀 Luck đã tăng lên {player['luck']}",
            ephemeral=True
        )

    @discord.ui.button(
        label="💎 Nâng Jackpot",
        style=discord.ButtonStyle.blurple
    )
    async def upgrade_jackpot(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        player = get_player(interaction.user.id)

        cost = (player["jackpot"] + 1) * 2000

        if player["cash"] < cost:
            return await interaction.response.send_message(
                f"❌ Cần {cost:,} Cash",
                ephemeral=True
            )

        player["cash"] -= cost
        player["jackpot"] += 1

        save_player(interaction.user.id, player)

        await interaction.response.send_message(
            f"💎 Jackpot đã tăng lên {player['jackpot']}",
            ephemeral=True
        )


# ===== START COMMAND =====

@bot.command()
async def start(ctx):

    player = await get_player(ctx.author.id)

    need_xp = player["level"] * 100

    embed = discord.Embed(
        title="🎮 THÔNG TIN NGƯỜI CHƠI",
        color=discord.Color.gold()
    )

    embed.set_author(
        name=str(ctx.author),
        icon_url=ctx.author.display_avatar.url
    )

    embed.add_field(
        name="💰 Cash",
        value=f"{player['cash']:,}",
        inline=True
    )

    embed.add_field(
        name="⭐ Level",
        value=player["level"],
        inline=True
    )

    embed.add_field(
        name="📈 XP",
        value=f"{player['xp']}/{need_xp}",
        inline=True
    )

    embed.add_field(
        name="🍀 Luck",
        value=player["luck"],
        inline=True
    )

    embed.add_field(
        name="💎 Jackpot",
        value=player["jackpot"],
        inline=True
    )

    embed.add_field(
        name="🔥 Chuỗi thua",
        value=player["lose_streak"],
        inline=True
    )

    embed.set_footer(
        text="Nhấn nút bên dưới để nâng cấp chỉ số"
    )

    await ctx.send(
        embed=embed,
        view=UpgradeView()
    )

def get_rank(level):

    if level >= 100:
        return "👑 Huyền Thoại"

    elif level >= 75:
        return "💎 Đại Cao Thủ"

    elif level >= 50:
        return "🔥 Cao Thủ"

    elif level >= 25:
        return "⚔️ Chiến Binh"

    elif level >= 10:
        return "⭐ Kẻ Phiêu Lưu"

    return "🌱 Tân Thủ"

@bot.command()
async def profile(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    if member.bot:
        return await ctx.send(
            "❌ Không thể xem hồ sơ của bot."
        )

    player = get_player(member.id)

    need_xp = player["level"] * 100

    embed = discord.Embed(
        title=f"👤 Hồ sơ của {member.display_name}",
        color=discord.Color.blue()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.add_field(
        name="💰 Cash",
        value=f"{player['cash']:,}",
        inline=True
    )

    embed.add_field(
        name="⭐ Level",
        value=player["level"],
        inline=True
    )

    embed.add_field(
        name="📈 XP",
        value=f"{player['xp']}/{need_xp}",
        inline=True
    )

    embed.add_field(
        name="🍀 Luck",
        value=player["luck"],
        inline=True
    )

    embed.add_field(
        name="💎 Jackpot",
        value=player["jackpot"],
        inline=True
    )

    embed.add_field(
        name="🔥 Chuỗi thua",
        value=player["lose_streak"],
        inline=True
    )

    # Thống kê phụ
    embed.add_field(
        name="🏆 Danh hiệu",
        value=get_rank(player["level"]),
        inline=False
    )

    embed.set_footer(
        text=f"ID: {member.id}"
    )

    await ctx.send(embed=embed)

@bot.command()
async def toplvl(ctx):

    sorted_players = sorted(
        players.items(),
        key=lambda x: (
            x[1]["level"],
            x[1]["xp"]
        ),
        reverse=True
    )

    text = ""

    for index, (user_id, data) in enumerate(
        sorted_players[:10],
        start=1
    ):

        user = bot.get_user(int(user_id))

        if user:
            name = user.name
        else:
            name = f"User {user_id}"

        text += (
            f"{index}. {name} "
            f"(Lv.{data['level']})\n"
        )

    embed = discord.Embed(
        title="🏆 TOP LEVEL",
        description=text,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

ADMINS = [1195361246195757118]

@bot.command()
async def buff(ctx, stat=None, target=None, amount=None):

    if ctx.author.id not in ADMINS:
        return await ctx.send(
            "❌ Bạn không có quyền dùng lệnh này!"
        )

    if stat is None:
        return await ctx.send(
            "Cách dùng:\n"
            ">buff cash @user 1000\n"
            ">buff luck @user 5\n"
            ">buff level @user 1"
        )

    # Tự buff
    if amount is None:

        try:
            value = int(target)

        except:
            return await ctx.send("❌ Giá trị không hợp lệ!")

        member = ctx.author

    else:

        if not ctx.message.mentions:
            return await ctx.send(
                "❌ Vui lòng mention người chơi!"
            )

        member = ctx.message.mentions[0]

        try:
            value = int(amount)

        except:
            return await ctx.send("❌ Giá trị không hợp lệ!")

    if member.bot:
        return await ctx.send(
            "❌ Không thể buff bot!"
        )

    player = await get_player(member.id)

    valid_stats = [
        "cash",
        "xp",
        "level",
        "luck",
        "jackpot",
        "lose_streak"
    ]

    if stat.lower() not in valid_stats:
        return await ctx.send(
            f"❌ Chỉ số hợp lệ:\n"
            f"{', '.join(valid_stats)}"
        )

    player[stat.lower()] += value

    if player[stat.lower()] < 0:
        player[stat.lower()] = 0

    await save_player(player)

    embed = discord.Embed(
        title="🛠️ ADMIN BUFF",
        color=discord.Color.green()
    )

    embed.add_field(
        name="👤 Người nhận",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="📊 Chỉ số",
        value=stat,
        inline=True
    )

    embed.add_field(
        name="➕ Giá trị",
        value=value,
        inline=True
    )

    embed.add_field(
        name="📈 Sau buff",
        value=player[stat.lower()],
        inline=False
    )

    await ctx.send(embed=embed)

token = os.getenv("TOKEN")

if token is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    print("✅ TOKEN đã được tìm thấy!")
    bot.run(token)
