import random
import asyncio
import os
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

players = {}

def get_player(user_id):
    user_id = str(user_id)

    if user_id not in players:
        players[user_id] = {
            "cash": 1000,
            "xp": 0,
            "level": 1,
            "luck": 0,
            "jackpot": 0,
            "lose_streak": 0
        }

    return players[user_id]


def save_player(player):
    pass

@bot.command()
async def roll(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Số tiền phải lớn hơn 0!")

    player = get_player(ctx.author.id)

    if player["cash"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền!")

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

        save_player(player)

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

        save_player(player)

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

        save_player(player)

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

    player = get_player(ctx.author.id)

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
        player["xp"] += 40

        save_player(player)

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

        save_player(player)

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

        save_player(player)

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

        save_player(player)

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

        save_player(player)

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

    player = get_player(ctx.author.id)

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

token = os.getenv("TOKEN")

if token is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    print("✅ TOKEN đã được tìm thấy!")
    bot.run(token)
