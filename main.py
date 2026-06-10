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
    
token = os.getenv("TOKEN")

if token is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    print("✅ TOKEN đã được tìm thấy!")
    bot.run(token)
