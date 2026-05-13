import discord
from discord.ext import commands
from colorama import Fore, Back, Style
from deep_translator import GoogleTranslator
from langdetect import detect
import datetime
import random as rand
import asyncio
import json
import re
import os
import time
import platform
import aiohttp
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

prefix = ">"
intents = discord.Intents.all()

intents = discord.Intents.all()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

mute_end_times = {}

#BAN_REASON_FILE = "ban_reasons.json"


#def load_ban_reasons():
#    if not os.path.exists(BAN_REASON_FILE):
#        return {}
#    with open(BAN_REASON_FILE, "r", encoding="utf-8") as f:
#        return json.load(f)


#def save_ban_reasons(data):
#    with open(BAN_REASON_FILE, "w", encoding="utf-8") as f:
#        json.dump(data, f, ensure_ascii=False, indent=4)


bot.remove_command("help")

YOUR_USER_ID = 1209454073913286667

@bot.event
async def on_ready():
    print(f"Online: {bot.user}")

@bot.event
async def on_ready():
    prfx = (
        Back.BLACK
        + Fore.GREEN
        + time.strftime("%H:%M:%S UTC", time.gmtime())
        + Back.RESET
        + Fore.WHITE
        + Style.BRIGHT
    )
    print(prfx + " Logged in as " + Fore.YELLOW + bot.user.name)
    print(prfx + " Bot ID " + Fore.YELLOW + str(bot.user.id))
    print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
    print(prfx + " Python Version " + Fore.YELLOW + platform.python_version())

    activity = discord.Game(name=">help")
    await bot.change_presence(status=discord.Status.idle, activity=activity)

    print(f"✅ Bot đang chạy dưới tài khoản: {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            description=f"⚠️ | **Lệnh** `{ctx.message.content}` **không tồn tại!**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

        print(f"🚫 Lỗi: Lệnh `{ctx.message.content}` không tồn tại.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ **Lỗi: Thiếu đối số yêu cầu cho lệnh** `{ctx.command}`.")
        print(f"🚫 Lỗi: Thiếu đối số yêu cầu cho lệnh {ctx.command}.")
    else:
        print(f"🚫 Lỗi không xác định: {error}")


@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"**🏓 Pong! Độ trễ hiện tại là** `{latency}ms`")


@bot.command()
async def hello(ctx):
    await ctx.send("hello!")


@bot.command()
async def server(ctx):
    await ctx.send("**Server của tôi:**\nhttps://discord.gg/cJ3eBMvkby")


@bot.command()
async def emoji(ctx):
    await ctx.send(
        "**Emoji của server NMTH:fruit🍎:**\n<:1storage:1208787725130670161> <:2xMastery:1208787612517535754> <:2xbossdrops:1209165084937687120> <:Barrier:1209158054113837096> <:Blizzard:1208646126836916254> <:Buddha:1208792253552656474> <:Chop:1208653616282337310> <:Dark:1208643837921202237> <:Diamond:1209159386686169088> <:Dough:1208786630232510474> <:Dragon:1208348855461089291> <:Falcon:1208343215833616424> <:Fastboats:1209165789626892308> <:Ghost:1209159870025039962> <:Ice:1208643807533473843> <:Light:1208643771563114628> <:Magma:1209162494849843221> <:Mammoth:1208643182653612093> <:Notifier:1209164431880228946> <:Pain:1209160912800321639> <:Rumble:1208334069306228796> <:Sand:1209156856853954570> <:Shadow:1208792040305860678> <:Sound:1208784468425572372> <:Spike:1208653764534468630> <:Spin:1208342275546157076> <:Spirit:1208349332462641184> <:Spring:1208342621920039043> <:Trex:1208323184655605800> <:Yoru:1208787648878215169> <:bom:1208653481464963132> <:bot:1212768062995169291> <:control:1209142409011658772> <:error:1210244771705131028> <:flame:1208645411036725258> <:gravity:1208338702078582785> <:kitsune:1208348433061253130> <:leopard:1208347710328148038> <:love:1209160241347039262> <:offerrequest:1208789371826864178> <:phoenix:1208338189673299998> <:portal:1208643734405779466> <:quake:1208647391910174770> <:rocket:1208339485054734427> <:rubber:1208652258653507585> <:serverbooster:1212767951271235614> <:smoke:1208651122462560347> <:spider:1208647140918951956> <:venom:1208334042991431680> <:verify:1212767768836050944>"
    )


@bot.command()
async def meo(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
            if resp.status != 200:
                await ctx.send("**😿 Không lấy được ảnh mèo!**")
                return
            data = await resp.json()
            image_url = data[0]["url"]

            pink = discord.Color.from_rgb(255, 105, 180)
            embed = discord.Embed(title="**🌸 Mèo cute:**", color=pink)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)


# @bot.command()
# async def meo(ctx):
#     image_urls = [
#     "https://tse1.mm.bing.net/th?id=OIP.HqHq_40zUO40sXt-I1LpVAHaJQ&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.Y9MaxiVxV-8HnzG7MuNC3wHaE8&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.5ugk7qGj0hcpwsfY0QMl3AHaHa&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.gc53sbg6ZQK7Bw9AgfnUMQHaL2&pid=Api&P=0&h=220",
#     "https://tse4.explicit.bing.net/th?id=OIP.kp8cgwjkuj2cqMF71u93MAHaEK&pid=Api&P=0&h=220",
#     "https://tse3.explicit.bing.net/th?id=OIP.74s89yGiTJ9Y-ptW-msSwAHaHa&pid=Api&P=0&h=220",
#     "https://tse1.mm.bing.net/th?id=OIP.KdRE7KHqL-46M8nrvOX2CgHaHa&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.RVd_tWA4X6z1D6PkcaQSawHaFk&pid=Api&P=0&h=220",
#     "https://tse4.mm.bing.net/th?id=OIP.QEZ5ajvXDiiBpvQzf2XyHwHaHa&pid=Api&P=0&h=220",
#     "https://tse3.mm.bing.net/th?id=OIP.Fb9TlA92Z8VTbWXSNfvWIAHaHa&pid=Api&P=0&h=220",
#     "https://tse1.mm.bing.net/th?id=OIP.qdq4A5NN-sndDV9lvxNZOwHaHH&pid=Api&P=0&h=220",
#     "https://tse3.mm.bing.net/th?id=OIP.ctIStdz_4ZGcT5GCzx0ttgHaNK&pid=Api&P=0&h=220",
#     "https://tse3.explicit.bing.net/th?id=OIP.iMG3CK7nCkVlcLXGG5dqXwHaJ4&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.Cdm86CJYnCUROjPy9iXs1AHaE8&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.Kx9JN7Lg8gie0QNxzkoqzAHaIC&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.bhFafTC6FKECib5E-_e74gHaHa&pid=Api&P=0&h=220",
#     "https://tse2.mm.bing.net/th?id=OIP.E1bMqGOkt1lb3b5JftaOzgHaHa&pid=Api&P=0&h=220",
#     "https://tse2.explicit.bing.net/th?id=OIP.SUJl86Owb7cfRlLFK-p2QgHaE_&pid=Api&P=0&h=220",
#     "https://tse3.mm.bing.net/th?id=OIP.AquKN4BupIn-P8h7rz-F1wHaEo&pid=Api&P=0&h=220",
#     "https://tse3.explicit.bing.net/th?id=OIP.s3IqxnvKmSV8QJcAvupC7gHaH5&pid=Api&P=0&h=220",
#     "https://tse1.explicit.bing.net/th?id=OIP.-eh5biFTbFG2w9IznNK_MQHaHa&pid=Api&P=0&h=220",
#     "https://tse1.explicit.bing.net/th?id=OIP.QgSiaFLQIfJEPFD-gvgTpwHaHa&pid=Api&P=0&h=220",
#     "https://tse4.explicit.bing.net/th?id=OIP.z-qNGKYdV95LU3UiVBlgrAHaHa&pid=Api&P=0&h=220",
#     "https://tse4.explicit.bing.net/th?id=OIP.SggdzJqd1MzO1WKVDdnzTgHaHa&pid=Api&P=0&h=220",
#     ]

#     rand_image_url = rand.choice(image_urls)

#     if not rand_image_url.startswith("http"):
#         await ctx.send("Đã xảy ra lỗi!")
#         return

#     color = discord.Color.from_rgb(255, 192, 203)

#     embed = discord.Embed(description=f"**ẢNH MÈO CUTE:**\n[url hình ảnh]({rand_image_url})", color=color)
#     embed.set_image(url=rand_image_url)
#     await ctx.channel.send(embed=embed)


@bot.command()
async def meme_meo(ctx):
    image_urls = [
        "https://tse3.mm.bing.net/th?id=OIP.Xbb_OlRghca9FxXkE0TkXAHaHa&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.L-2nxCsFweG-j0By__eWcQHaHa&pid=Api&P=0&h=220",
        "https://tse2.mm.bing.net/th?id=OIP.zhpsSsHvGayykko1u8g4WQHaHa&pid=Api&P=0&h=220",
        "https://tse2.mm.bing.net/th?id=OIP.iyvL213ywB4-nT-pGg2rJwHaH1&pid=Api&P=0&h=220",
        "https://tse4.mm.bing.net/th?id=OIP.6HbiXpf4y8ZNQ98XLp5voQHaHW&pid=Api&P=0&h=220",
        "https://tse2.mm.bing.net/th?id=OIP.f0vsnHEfLeap1OGbPz4-9QHaEK&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.WhN53Mqscsjoq4kLFzOVAAHaHU&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.U0D5JdoPkQMi4jhiriSVsgHaHa&pid=Api&P=0&h=220",
        "https://tse4.mm.bing.net/th?id=OIP.O9gRcOnWiTxaUbJwz7PTjwHaG9&pid=Api&P=0&h=220",
        "https://tse2.explicit.bing.net/th?id=OIP.gxGhO9ozyQy1ZGS56ylcQwHaGc&pid=Api&P=0&h=220",
        "https://tse1.explicit.bing.net/th?id=OIP._H51bAVwITjfp3EdDpN-KQHaIk&pid=Api&P=0&h=220",
        "https://tse4.explicit.bing.net/th?id=OIP.bvgvfalKJGM4rU-nDAJ3aQHaHa&pid=Api&P=0&h=220",
        "https://tse1.mm.bing.net/th?id=OIP.MznlTA5WLv2iHbQgr20wYgHaHW&pid=Api&P=0&h=220",
        "https://tse1.explicit.bing.net/th?id=OIP.5Qs3VrjcxI3NUM0a37dTiAHaFs&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.9K9S3A8Om-W1-FFAQwECoAHaHd&pid=Api&P=0&h=220",
        "https://tse1.mm.bing.net/th?id=OIP.epd8xKtf7IzcQ5P2zlpxBQHaHS&pid=Api&P=0&h=220",
        "https://tse4.mm.bing.net/th?id=OIP.pWzUbkkg5E0FmgDZnuQJyQHaHY&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.gJMQDAgX5Bw-izGSoxSJxwHaHa&pid=Api&P=0&h=220",
        "https://tse1.mm.bing.net/th?id=OIP.OWWxR1BzDRMPmjBsC5SWZQAAAA&pid=Api&P=0&h=220",
        "https://tse4.mm.bing.net/th?id=OIP.nX9W2L3ZScudwlqKK1URKwHaIQ&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.0l44ygI2BYKBhRH1_8IDWgHaHa&pid=Api&P=0&h=220",
        "https://tse2.mm.bing.net/th?id=OIP.GH0IdOqnJK0z_KyyJRy8mQHaEy&pid=Api&P=0&h=220",
        "https://tse1.mm.bing.net/th?id=OIP.OwvygjRCgg8_golq3DY83AHaNL&pid=Api&P=0&h=220",
        "https://tse2.mm.bing.net/th?id=OIP.Xm_23eXEvGy8I_OfUwRf0gHaHa&pid=Api&P=0&h=220",
        "https://tse3.mm.bing.net/th?id=OIP.6p7tR-DtumgnM3HJ3Rf1hAHaHa&pid=Api&P=0&h=220",
        "https://tse1.mm.bing.net/th?id=OIP.UIZr2cIWcsepLhMH2vbCSQHaHa&pid=Api&P=0&h=220",
    ]

    rand_image_url = rand.choice(image_urls)

    pink_color = discord.Color.from_rgb(255, 192, 203)

    embed = discord.Embed(
        description=f"**MEME MÈO HAY:**\n[Link hình ảnh]({rand_image_url})",
        color=pink_color,
    ).set_image(url=rand_image_url)

    await ctx.channel.send(embed=embed)


@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="Ko có lý do"):
    if ctx.author.id != YOUR_USER_ID and not ctx.author.guild_permissions.kick_members:
        await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None:
        await ctx.send(
            "```>kick 'member' 'reason'\n       ^^^^^^   ^^^^^\n^ là chỗ cần điền```"
        )
        return

    if member.bot:
        await ctx.send("**Lệnh này không thể kick bot!**")
        return

    bot_top_role = ctx.guild.me.top_role
    if bot_top_role.position <= member.top_role.position:
        await ctx.send("**Bot không thể kick thành viên này!**")
        return

    try:
        await ctx.send(f"{member.mention} **đã bị đá** | reason: {reason}")
        await member.send(f"Bạn đã bị **đá** khỏi **Server** | reason: {reason}")
        await member.kick(reason=reason)
    except discord.Forbidden:
        await ctx.send(
            "**Tôi không thể gửi tin nhắn cho thành viên này. Tuy nhiên, họ vẫn bị kick khỏi server.**"
        )
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def add_role(ctx, member: discord.Member = None, *, role: discord.Role = None):
    if ctx.author.id != YOUR_USER_ID and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None or role is None:
        await ctx.send(
            "```>app_role 'member' 'role'\n           ^^^^^^   ^^^^\n^ là chỗ cần điền```"
        )
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"{member.mention} **đã được thêm role**")
    except discord.Forbidden:
        await ctx.send("**Bot không có đủ quyền hạn để thêm role cho thành viên!**")
    except discord.HTTPException:
        await ctx.send("**Đã xảy ra lỗi khi thêm role cho thành viên!**")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


@bot.command()
async def remove_role(ctx, member: discord.Member = None, *, role: discord.Role = None):
    if ctx.author.id != YOUR_USER_ID and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None or role is None:
        await ctx.send(
            "```>remove_role 'member' 'role'\n              ^^^^^^   ^^^^\n^ là chỗ cần điền```"
        )
        return

    try:
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} **đã bị xóa role**")
    except discord.Forbidden:
        await ctx.send("**Bot không có đủ quyền hạn để xóa role của thành viên!**")
    except discord.HTTPException:
        await ctx.send("**Đã xảy ra lỗi khi xóa role của thành viên!**")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


# @bot.command()
# async def help(message):
#     embed = discord.Embed(
#         title="**COMMAND SUPPORT:**",
#         description=(
#             "------------------------------------------------\n"
#             "=> __***Lệnh dành cho `Member` và `Administrator`:***__\n"
#             "* `>meo`\n * **random ảnh mèo**\n"
#             "* `>meme_meo`\n * **random meme mèo**\n"
#             "* `>ping`\n - **kiểm tra độ trễ giữa máy chủ Discord và máy tính**\n"
#             "* `>tinh 'số thứ nhất' 'số thứ hai'`\n * **Máy tính toán**\n"
#             "* `>random 'member' 'phần thưởng'`\n * **member: Thành viên muốn random**\n - **phần thưởng: Món quà muốn tặng (ko cần cũng được)**\n"
#             "* `>translate 'ngôn ngữ đầu vào' 'ngôn ngữ đầu ra' 'văn bản`'\n * **ngôn ngữ đầu vào: Ngôn ngữ chính**\n - **ngôn ngữ đầu ra: Ngôn ngữ cần dịch**\n - **văn bản: Văn bản muốn dịch**\n"
#             "* `>languages`\n * **hỗ trợ ngôn ngữ cho lệnh traslate**\n"
#             "------------------------------------------------\n"
#             "=> __***Lệnh dành cho `Administrator`:***__\n"
#             "* `>userinfo 'member'`\n * **member: Thành viên muốn xem thông tin**\n    **(nếu ko có thành viên muốn xem thông thì thông tin sẽ là người dùng lệnh)**\n"
#             "* `>kick 'member' 'reason'`\n * **member: Tên thành viên muốn kick**\n - **reason: Lý do kick**\n"
#             "* `>ban 'member' 'reason'`\n * **member: Tên thành viên muốn ban**\n - **reason: Lý do ban**\n"
#             "* `>unban 'member' 'reason'`\n * **member: Tên thành viên muốn unban**\n - **reason: Lý do unban**\n"
#             "* `>add_role 'member' 'role'`\n * **member: Tên thành viên muốn app role**\n - **role: Role muốn thêm**\n"
#             "* `>remove_role 'member' 'role'`\n * **member: Tên thành viên muốn remove role**\n - **role: Role muốn xóa**"
#         ),
#         color=0x808080
#     )
#     await message.send(embed=embed)


@bot.command()
async def help(message):
    embed_pages = [
        (
            "**COMMAND SUPPORT:**\n"
            "------------------------------------------------\n"
            "=> __***Lệnh dành cho `Member` và `Administrator`:***__\n"
            "* :one: `>meo`\n * **random ảnh mèo**\n"
            "* :two: `>meme_meo`\n * **random meme mèo**\n"
            "* :three: `>ping`\n - **kiểm tra độ trễ giữa máy chủ Discord và máy tính**\n"
            "* :four: `>tinh 'số thứ nhất' 'số thứ hai'`\n * **Máy tính toán**\n"
            "* :five: `>random 'member' 'phần thưởng'`\n * **member: Thành viên muốn random**\n - **phần thưởng: Món quà muốn tặng (ko cần cũng được)**\n"
            "* :six: `>translate 'ngôn ngữ đầu vào' 'ngôn ngữ đầu ra' 'văn bản`'\n * **ngôn ngữ đầu vào: Ngôn ngữ chính**\n - **ngôn ngữ đầu ra: Ngôn ngữ cần dịch**\n - **văn bản: Văn bản muốn dịch**\n"
            "* :seven: `>languages`\n * **hỗ trợ ngôn ngữ cho lệnh traslate**\n"
            "### 1/2"
        ),
        (
            "=> __***Lệnh dành cho `Administrator`:***__\n"
            "* :one: `>userinfo 'member'`\n * **member: Thành viên muốn xem thông tin**\n    **(nếu ko có thành viên muốn xem thông thì thông tin sẽ là người dùng lệnh)**\n"
            "* :two: `>kick 'member' 'reason'`\n * **member: Tên thành viên muốn kick**\n - **reason: Lý do kick**\n"
            "* :three: `>ban 'member' 'reason'`\n * **member: Tên thành viên muốn ban**\n - **reason: Lý do ban**\n"
            "* :four: `>unban 'member' 'reason'`\n * **member: Tên thành viên muốn unban**\n - **reason: Lý do unban**\n"
            "* :five: `>add_role 'member' 'role'`\n * **member: Tên thành viên muốn app role**\n - **role: Role muốn thêm**\n"
            "* :six: `>remove_role 'member' 'role'`\n * **member: Tên thành viên muốn remove role**\n - **role: Role muốn xóa**\n"
            "### 2/2"
        ),
    ]

    page_reactions = ["⬅️", "➡️"]
    current_page = 0

    msg = await message.send(
        embed=discord.Embed(description=embed_pages[current_page], color=0x808080)
    )

    for reaction in page_reactions:
        await msg.add_reaction(reaction)

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in page_reactions

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)

            if str(reaction.emoji) == "➡️" and current_page < len(embed_pages) - 1:
                current_page += 1
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
            elif str(reaction.emoji) == "⬅️" and current_page == 0:
                current_page = len(embed_pages) - 1

            await msg.edit(
                embed=discord.Embed(
                    description=embed_pages[current_page], color=0x808080
                )
            )
            await msg.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            break


@bot.command()
async def fake(ctx, user: discord.Member, *, message: str):
    try:
        if (
            ctx.author.id != YOUR_USER_ID
            and not ctx.author.guild_permissions.administrator
        ):
            await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
            return

        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name=user.display_name)

        await webhook.send(
            content=message, username=user.display_name, avatar_url=user.avatar.url
        )

        await webhook.delete()

    except discord.Forbidden:
        await ctx.send("**Bot không có quyền tạo webhook trong kênh này!**")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {str(e)}")


@fake.error
async def fake_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Bạn phải chỉ định một người dùng và tin nhắn!**")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("**Không tìm thấy người dùng!**")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("**Bot không có quyền thực hiện hành động này!**")
    else:
        await ctx.send(f"Đã xảy ra lỗi: {str(error)}")


@bot.command()
async def tinh(ctx, a: str = None, b: str = None):
    try:
        if a is None or b is None:
            await ctx.send(
                "```>tinh 'số thứ nhất' 'số thứ hai'\n       ^^^^^^^^^^^   ^^^^^^^^^^\nđiền các số để tính trên ^\nYÊU CẦU KO ĐIỀN CHỮ```"
            )
            return

        if not (a.isdigit() and b.isdigit()):
            await ctx.send("**Vui lòng nhập vào hai số nguyên!**")
            return

        a = int(a)
        b = int(b)

        sum_result = a + b
        difference_result = a - b
        product_result = a * b
        if b != 0:
            division_result = a / b
        else:
            division_result = "**Không thể chia cho 0**"

        embed = discord.Embed(title="Kết quả", color=0x00FF00)
        embed.add_field(name="a + b", value=f"{a} + {b} = {sum_result}", inline=False)
        embed.add_field(
            name="a - b", value=f"{a} - {b} = {difference_result}", inline=False
        )
        embed.add_field(
            name="a * b", value=f"{a} * {b} = {product_result}", inline=False
        )
        embed.add_field(
            name="a / b", value=f"{a} / {b} = {division_result}", inline=False
        )

        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


@bot.command()
async def clear(ctx, amount: int = None):
    if (
        ctx.author.id != YOUR_USER_ID
        and not ctx.author.guild_permissions.manage_messages
    ):
        await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
        return

    if amount is None:
        await ctx.send(
            "```>clear 'số lượng'\n        ^^^^^^^^\nđiền số tin nhắn cần xóa trên ^```"
        )
        return

    if amount < 1:
        await ctx.send("**Số lượng tin nhắn phải lớn hơn 0!**")
        return

    try:
        await ctx.message.delete()
        deleted = await ctx.channel.purge(
            limit=amount, check=lambda msg: not msg.pinned
        )
        await ctx.send(f"**Đã xóa {len(deleted)} tin nhắn!**", delete_after=5)
    except discord.Forbidden:
        await ctx.send("**Bot không có quyền xóa tin nhắn trong kênh này!**")
    except Exception as e:
        await ctx.send(f"**Đã xảy ra lỗi: {e}**")
        print(f"**Đã xảy ra lỗi: {e}**")


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("**Vui lòng nhập số lượng tin nhắn hợp lệ!**")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "```>clear 'số lượng'\n        ^^^^^^^^\nđiền số tin nhắn cần xóa trên ^```"
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("**Bạn không có quyền để xóa tin nhắn!**")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("**Bot không có quyền để xóa tin nhắn!**")


@bot.command()
async def script(ctx):
    select = discord.ui.Select(
        placeholder="Chọn một script",
        options=[
            discord.SelectOption(label="TỔNG HỢP", value="option1"),
            discord.SelectOption(label="HOHO HUB", value="option2"),
            discord.SelectOption(label="MASTER HUB(TIẾNG VIỆT)", value="option3"),
            discord.SelectOption(label="MINGAMINGPREMIUMVIETSUB HUB", value="option4"),
            discord.SelectOption(label="NIGHT HUB", value="option5"),
            discord.SelectOption(label="REDz HUB", value="option6"),
            discord.SelectOption(label="W-AZURE TRUE V2", value="option7"),
            discord.SelectOption(label="MTIEN HUB", value="option8"),
            discord.SelectOption(label="ANNIE HUB", value="option9"),
            discord.SelectOption(label="XERO HUB", value="option10"),
            discord.SelectOption(label="ZEN HUB", value="option11"),
            discord.SelectOption(label="ZEKROM HUB", value="option12"),
            discord.SelectOption(label="PAYBACK HUB", value="option13"),
            discord.SelectOption(label="HACKER HUB", value="option14"),
            discord.SelectOption(label="ADEL HUB", value="option15"),
            discord.SelectOption(label="COKKA HUB", value="option16"),
            discord.SelectOption(label="ACKERMAN HUB", value="option17"),
            discord.SelectOption(label="MTRIET HUB", value="option18"),
            discord.SelectOption(label="ART DONATION", value="option19"),
            discord.SelectOption(label="MARU", value="option20"),
            discord.SelectOption(label="APPLE HUB", value="option21"),
            discord.SelectOption(label="BANANA HUB", value="option22"),
        ],
    )

    select.callback = lambda interaction: CustomMenu.select_callback(
        select, interaction
    )

    view = discord.ui.View()
    view.add_item(select)

    await ctx.send(
        "**Nhấp vào menu để chọn tùy chọn script `hack blox fruit`:**", view=view
    )

    try:
        pass
    except Exception as e:
        await ctx.send(f"**Đã xảy ra lỗi: {e}**")
        print(f"**Đã xảy ra lỗi: {e}**")


class CustomMenu:
    @staticmethod
    async def select_callback(select, interaction):
        selected_value = interaction.data["values"][0]
        if selected_value == "option1":
            await interaction.response.send_message(
                "**TỔNG HỢP:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/m1M-Plqer819/any/main/skdpo.lua'))();\n```",
                ephemeral=True,
            )
        elif selected_value == "option2":
            await interaction.response.send_message(
                "**HOHO HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/acsu123/HOHO_H/main/Loading_UI'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option3":
            await interaction.response.send_message(
                "**MASTER HUB(TIỂNG VIỆT):**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/onepicesenpai/onepicesenpai/main/onichanokaka'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option4":
            await interaction.response.send_message(
                "**MINGAMINGPREMIUMVIETSUB HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/Basicallyy/Basicallyy/main/MinGamingPremiumVietSub.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option5":
            await interaction.response.send_message(
                "**NIGHT HUB:**\n```lua\ngetgenv().FixLag = false\nloadstring(game:HttpGet('https://raw.githubusercontent.com/NIGHTHUBONTOP/Main/main/LoaderScript.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option6":
            await interaction.response.send_message(
                "**REDz HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/REDzHUB/BloxFruits/main/redz9999'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option7":
            await interaction.response.send_message(
                "**W-AZURE TRUE V2:**\n```lua\ngetgenv().Team = 'Pirates'\nloadstring(game:HttpGet('https://api.luarmor.net/files/v3/loaders/3b2169cf53bc6104dabe8e19562e5cc2.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option8":
            await interaction.response.send_message(
                "**MTIEN HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/ImTienNguyenZ/MTienHub/main/Loader.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option9":
            await interaction.response.send_message(
                "**ANNIE HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/1stMars/Annie/main/1st.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option10":
            await interaction.response.send_message(
                "**XERO HUB:**\n```lua\ngetgenv().Team = 'Marines' -- Pirates/Marines\nloadstring(game:HttpGet('https://raw.githubusercontent.com/verudous/XeroHub/main/main.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option11":
            await interaction.response.send_message(
                "**ZEN HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/Zenhubtop/zenhubnextgen/main/Loader', true))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option12":
            await interaction.response.send_message(
                "**ZEKROM HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/ahmadsgamer2/ZekromHub-X/main/Zekrom-Hub-X-exe'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option13":
            await interaction.response.send_message(
                "**PAYBACK HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/ScriptBlox/Script/main/PayBack.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option14":
            await interaction.response.send_message(
                "**HACKER HUB**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/Binintrozza/Testinghel/main/HECKER'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option15":
            await interaction.response.send_message(
                "**ADEL HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/AdelOnTheTop/Adel-Hub/main/Main.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option16":
            await interaction.response.send_message(
                "**COKKA HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/UserDevEthical/Loadstring/main/CokkaHub.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option17":
            await interaction.response.send_message(
                "**ACKERMAN HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/ToTaiVn/AckermanXSimple/main/AckermanHubBest'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option18":
            await interaction.response.send_message(
                "**MTRIET HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/Minhtriettt/Free-Script/main/MTriet-Hub.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option19":
            await interaction.response.send_message(
                "**ART DONATION:**\n```lua\nloadstring(game:HttpGet('https://scriptblox.com/raw/starving-artists-(DONATION-GAME)-Pixel-artist-OPEN-SOURCE-7688'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option20":
            await interaction.response.send_message(
                "**MARU:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/BestScriptEverr/Main-/main/UnknownHubV3'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option21":
            await interaction.response.send_message(
                "**APPLE HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/ImTienNguyenZ/AppleHubOnTop/main/Loader.lua'))()\n```",
                ephemeral=True,
            )
        elif selected_value == "option22":
            await interaction.response.send_message(
                "**BANANA HUB:**\n```lua\nloadstring(game:HttpGet('https://raw.githubusercontent.com/Nghia11n/Banana-Hub/main/bananahub.lua'))()\n```",
                ephemeral=True,
            )


@bot.command()
async def random(ctx, members: commands.Greedy[discord.Member], *, prize: str = None):
    if members:
        selected_member = rand.choice(members)

        message = f"🎲 Thành viên được chọn: {selected_member.mention}"
        if prize:
            message += f"\n🎁 Phần thưởng: {prize}"

        await ctx.send(message)
    else:
        await ctx.send("Vui lòng cung cấp ít nhất hai thành viên để chọn!")


async def handle_greetings(message):
    if message.content.lower() == "hello":
        await message.channel.send(f"Xin chào {message.author.name}!")
    elif message.content.lower() == "hi":
        await message.channel.send(f"Chào {message.author.name}!")
    elif message.content == "<@1231981029712072765>":
        color = 0x1ABAFF
        embed = discord.Embed(color=color)
        embed.add_field(
            name=":wave: **Xin chào {}**".format(message.author.name),
            value="🤖 **Tôi là Bot Discord của bạn và sẵn sàng để phục vụ!**\n🔖 **Prefix của tôi là `>`**\nℹ️ **Để khám phá các tính năng và lệnh của tôi, hãy sử dụng `{}help`** 💡\n🎮 **Bạn có thể tham khảo và chơi trò chơi của tôi, hãy sử dụng lệnh `>game`**".format(
                prefix
            ),
        )
        await message.channel.send(embed=embed)
    elif message.content.lower() == "sex":
        await message.channel.send(f"não bọn mày toàn sex với vú ko à?")


@bot.event
async def on_message(message):
    if not message.author.bot:
        await handle_greetings(message)
    await bot.process_commands(message)


@bot.command(aliases=["uinfo", "whois"])
async def userinfo(ctx, member: discord.Member = None):

    if ctx.author.id != YOUR_USER_ID and not ctx.author.guild_permissions.manage_guild:
        await ctx.send("**❌ | Bạn không có quyền sử dụng lệnh này.**")
        return

    if member is None:
        member = ctx.author

    roles = [role.mention for role in member.roles[1:]]

    message_count = 0
    async for msg in ctx.channel.history(limit=500):
        if msg.author == member:
            message_count += 1

    loading = await ctx.send("**⏳ | Đang tải thông tin người dùng...**")

    embed = discord.Embed(
        title="**👤 THÔNG TIN NGƯỜI DÙNG**",
        description=(
            f"**📌 Hồ sơ của** {member.mention}\n"
            f"━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.green(),
        timestamp=ctx.message.created_at
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="**🆔 ID**",
        value=f"`{member.id}`",
        inline=True
    )

    embed.add_field(
        name="**📛 Tên người dùng**",
        value=f"`{member.name}#{member.discriminator}`",
        inline=True
    )

    embed.add_field(
        name="**🏷️ Biệt danh**",
        value=f"`{member.display_name}`",
        inline=True
    )

    embed.add_field(
        name="**📅 Tạo tài khoản**",
        value=member.created_at.strftime("%d/%m/%Y • %H:%M"),
        inline=False
    )

    embed.add_field(
        name="**📥 Tham gia server**",
        value=member.joined_at.strftime("%d/%m/%Y • %H:%M"),
        inline=False
    )

    embed.add_field(
        name="**💬 Tin nhắn gần đây**",
        value=f"`{message_count}` tin nhắn",
        inline=True
    )

    embed.add_field(
        name="**🤖 Bot**",
        value="✅ Có" if member.bot else "❌ Không",
        inline=True
    )

    embed.add_field(
        name="**⭐ Vai trò cao nhất**",
        value=member.top_role.mention,
        inline=False
    )

    embed.add_field(
        name=f"**🎭 Danh sách role** [{len(roles)}]",
        value=", ".join(roles) if roles else "Không có role",
        inline=False
    )

    embed.set_footer(
        text=f"Yêu cầu bởi {ctx.author}",
        icon_url=ctx.author.display_avatar.url
    )

    await loading.delete()
    await ctx.send(embed=embed)

# GAME

# game 1: Trivia
players = {}
current_question = None

questions = {
    "Thủ đô của Việt Nam là gì?": "Hà Nội",
    "Người sáng lập Microsoft là ai?": "Bill Gates",
    "Thủ đô của Pháp là gì?": "Paris",
    "Ai đã viết 'Giết con chim nhại'?": "Harper Lee",
    "Hành tinh nhỏ nhất trong hệ mặt trời của chúng ta là gì?": "Sao Thủy",
    "Thủ đô của Nhật Bản là gì?": "Tokyo",
    "Người phát minh ra bóng đèn là ai?": "Thomas Edison",
    "Núi cao nhất thế giới là gì?": "Everest",
    "Ai đã vẽ bức tranh 'Mona Lisa'?": "Leonardo da Vinci",
    "Công trình nổi tiếng nhất ở Ai Cập là gì?": "Kim Tự Tháp Giza",
    "Đại dương lớn nhất trên Trái Đất là gì?": "Thái Bình Dương",
    "Nhà văn nào đã viết 'Chiến tranh và hòa bình'?": "Leo Tolstoy",
}


@bot.command()
async def trivia(ctx, *args: discord.Member):
    global current_question

    if ctx.author not in players:
        players[ctx.author] = 0

    invited_players = [ctx.author] + list(args)
    for player in invited_players:
        if player not in players:
            players[player] = 0

    if current_question:
        embed = discord.Embed(
            title="Trò chơi đã bắt đầu!",
            description="Một câu hỏi đã được đặt ra. Hãy trả lời trước khi bắt đầu câu hỏi mới.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    if len(invited_players) > 1:
        embed = discord.Embed(
            title="Lời mời trò chơi Trivia",
            description="Bạn đã được mời tham gia trò chơi trivia. Hãy phản hồi 'chấp nhận' để tham gia.",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)

        def check(m):
            return (
                m.author in invited_players
                and m.channel == ctx.channel
                and m.content.lower() == "chấp nhận"
            )

        try:
            for player in invited_players:
                await ctx.send(
                    f"{player.mention}, bạn có chấp nhận tham gia trò chơi không? Trả lời 'chấp nhận' để tham gia."
                )
                await bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("Không có ai chấp nhận lời mời. Trò chơi không thể bắt đầu!")
            return

    current_question = rand.choice(list(questions.keys()))
    embed = discord.Embed(
        title="Câu hỏi Trivia",
        description=f"**Câu hỏi:** {current_question}",
        color=0x00FF00,
    )
    question_message = await ctx.send(embed=embed)

    remaining = 30

    async def countdown_timer():
        nonlocal remaining
        for remaining in range(30, 0, -1):
            await asyncio.sleep(1)
            embed.description = f"**Câu hỏi:** {current_question}\n\nThời gian còn lại: {remaining} giây"
            await question_message.edit(embed=embed)
        embed.description = f"**Câu hỏi:** {current_question}\n\nThời gian đã hết!"
        await question_message.edit(embed=embed)

    countdown_task = asyncio.create_task(countdown_timer())

    def check_answer(m):
        return m.author in invited_players and m.channel == ctx.channel

    try:
        answer = await bot.wait_for("message", check=check_answer, timeout=30.0)
        correct_answer = questions[current_question]
        countdown_task.cancel()

        if answer.content.lower() == correct_answer.lower():
            players[answer.author] += 1
            embed = discord.Embed(
                title="Chúc mừng!",
                description=f"**{answer.author}**, bạn đã trả lời đúng! Thời gian còn lại: {remaining} giây",
                color=0x00FF00,
            )
        else:
            embed = discord.Embed(
                title="Rất tiếc",
                description=f"**{answer.author}**, câu trả lời đúng là: **{correct_answer}**",
                color=0xFF0000,
            )

        await ctx.send(embed=embed)
    except asyncio.TimeoutError:
        await ctx.send(
            f"**Thời gian đã hết! Câu trả lời đúng là: {questions[current_question]}**"
        )
    finally:
        current_question = None


@bot.command()
async def score(ctx):
    if not players:
        embed = discord.Embed(
            title="Bảng điểm", description="Chưa có ai ghi điểm.", color=0xFF0000
        )
        await ctx.send(embed=embed)
    else:
        scores = "\n".join(
            [f"**{player}:** {score}" for player, score in players.items()]
        )
        embed = discord.Embed(
            title="Bảng điểm hiện tại", description=scores, color=0x00FF00
        )
        await ctx.send(embed=embed)


@bot.command()
async def endgame(ctx):
    if not players:
        embed = discord.Embed(
            title="Trò chơi kết thúc",
            description="Trò chơi chưa có ai tham gia.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
    else:
        winner = max(players, key=players.get)
        embed = discord.Embed(
            title="Trò chơi kết thúc",
            description=f"Người thắng cuộc là: **{winner}** với **{players[winner]}** điểm.",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)
    players.clear()


# Game 2: Lăn xúc xắc
@bot.command()
async def roll(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("Số mặt của xúc xắc phải lớn hơn 1.")
        return

    user_dice = rand.randint(1, sides)
    bot_dice = rand.randint(1, sides)

    if user_dice > bot_dice:
        result = "Bạn thắng!"
        color = discord.Colour.green()
    elif user_dice < bot_dice:
        result = "Tôi thắng!"
        color = discord.Colour.red()
    else:
        result = "Hòa!"
        color = discord.Colour.gold()

    embed = discord.Embed(title=f"Lăn Xúc Xắc {sides} Mặt 🎲", color=color)
    embed.add_field(
        name="Lựa chọn của bạn", value=f"Bạn lăn được số **{user_dice}**!", inline=True
    )
    embed.add_field(
        name="Lựa chọn của tôi", value=f"Tôi lăn được số **{bot_dice}**!", inline=True
    )
    embed.add_field(name="Kết quả", value=result, inline=False)

    await ctx.send(embed=embed)


# Game 3: Oẳn Tù Tì
@bot.command()
async def ott(ctx, choice: str):
    valid_choices = ["búa", "bao", "kéo"]
    if choice not in valid_choices:
        error_embed = discord.Embed(
            title="⚠️ | Lựa chọn không hợp lệ!",
            description="Vui lòng chọn một trong các lựa chọn hợp lệ: **búa**, **bao**, hoặc **kéo**.",
            color=discord.Colour.red(),
        )
        await ctx.send(embed=error_embed)
        return

    bot_choice = rand.choice(valid_choices)

    embed = discord.Embed(title="Oẳn Tù Tì", color=discord.Colour.blue())
    embed.add_field(name="Lựa chọn của bạn", value=choice, inline=True)
    embed.add_field(name="Lựa chọn của tôi", value=bot_choice, inline=True)

    if choice == bot_choice:
        result = "Hòa!"
    elif (
        (choice == "búa" and bot_choice == "kéo")
        or (choice == "bao" and bot_choice == "búa")
        or (choice == "kéo" and bot_choice == "bao")
    ):
        result = "Bạn thắng!"
    else:
        result = "Tôi thắng!"

    embed.add_field(name="Kết quả", value=result, inline=False)

    await ctx.send(embed=embed)

# gmae 4: đoán số
@bot.command()
async def doanso(ctx):
    number_to_guess = rand.randint(1, 100)
    number_of_attempts = 0

    embed = discord.Embed(
        title="**Chào mừng đến với trò chơi 'Số Bí Ẩn'!**",
        description="**Tôi đã nghĩ ra một số từ 1 đến 100, hãy đoán thử!**",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    while True:
        guess_msg = await bot.wait_for("message", check=check)
        try:
            guess = int(guess_msg.content)
            number_of_attempts += 1

            if guess < number_to_guess:
                embed = discord.Embed(
                    description="**Số của bạn đoán thấp quá!**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
            elif guess > number_to_guess:
                embed = discord.Embed(
                    description="**Số của bạn đoán cao quá!**",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Chúc mừng!",
                    description=f"**Bạn đã đoán đúng số {number_to_guess} trong {number_of_attempts} lần thử** :tada::tada::tada:",
                    color=discord.Color.green(),
                )
                await ctx.send(embed=embed)
                break
        except ValueError:
            embed = discord.Embed(
                description="**:warning: | Vui lòng nhập một số hợp lệ!**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)


@bot.command()
async def game(ctx):
    game_intro = (
        f"Xin chào {ctx.author.name}! Đây là các trò chơi mà bạn có thể chơi với tôi:\n"
        "1. **Trivia (Đố vui)**: Sử dụng lệnh `>trivia` để chơi trò chơi đố vui.\n"
        "2. **Lăn xúc xắc**: Sử dụng lệnh `>roll` để lăn xúc xắc.\n"
        "3. **Oẳn Tù Tì**: Sử dụng lệnh `>ott <búa/bao/kéo>` để chơi trò oẳn tù tì với tôi.\n"
        "4. **Số bí ẩn**: Sử dụng lệnh `>doanso` và nhập con số bất kì để chơi.\n"
        "Hãy thử các trò chơi và tận hưởng nhé!"
    )

    embed = discord.Embed(description=game_intro, color=discord.Colour.gold())

    embed.set_author(name="🎮 Trò chơi vui vẻ 🎮")

    embed.set_thumbnail(url="https://example.com/games_thumbnail.png")

    await ctx.send(embed=embed)


# Translate
LANGUAGES = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "ar": "Arabic",
    "hy": "Armenian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "hi": "Hindi",
    "hu": "Hungarian",
    "is": "Icelandic",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "kn": "Kannada",
    "km": "Khmer",
    "ko": "Korean",
    "la": "Latin",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "pl": "Polish",
    "pt": "Portuguese",
    "pa": "Punjabi",
    "ro": "Romanian",
    "ru": "Russian",
    "sr": "Serbian",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "es": "Spanish",
    "su": "Sundanese",
    "sw": "Swahili",
    "sv": "Swedish",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "**Vietnamese**",
    "cy": "Welsh",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "zu": "Zulu",
}


@bot.command()
async def languages(ctx):
    try:
        languages_str = "\n".join(
            [f"**{key}**: {value}" for key, value in LANGUAGES.items()]
        )

        embed = discord.Embed(
            title="🌍 Danh sách ngôn ngữ",
            description=languages_str,
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"**⚠️ Đã xảy ra lỗi:** `{e}`")


@bot.command()
async def translate(ctx, source_lang: str, target_lang: str, *, text_to_translate: str):
    try:
        translated_text = GoogleTranslator(
            source=source_lang, target=target_lang
        ).translate(text_to_translate)

        embed = discord.Embed(
            title="🔄 Kết quả dịch",
            description=f"**Văn bản gốc (Ngôn ngữ: {source_lang})**:\n{text_to_translate}",
            color=discord.Color.blue(),
        )
        embed.add_field(name="**Văn bản dịch**", value=translated_text, inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"**⚠️ Đã xảy ra lỗi:** `{e}`")


@bot.command(aliases=["ac"])
async def allchannels(ctx):
    danhsach_kenh = ""
    dem_kenh = 0
    embed = discord.Embed(title="Danh sách các kênh", colour=discord.Colour.green())

    for i in ctx.guild.channels:
        dem_kenh += 1
        danhsach_kenh += f"[{dem_kenh}] {i.name}\n"

    embed.description = danhsach_kenh
    await ctx.send(embed=embed)


@bot.command()
async def showhiddenvoice(ctx):
    danhsach_voice = []
    for kenh in ctx.guild.channels:
        if kenh.type == discord.ChannelType.voice:
            if not kenh.permissions_for(ctx.guild.me).connect:
                voice_channel = discord.utils.get(ctx.guild.channels, id=kenh.id)
                thanh_vien = voice_channel.members
                ten_thanh_vien = "\n - - - ".join([x.name for x in thanh_vien])
                danhsach_voice.append(voice_channel)
                await ctx.send(
                    f"**[Hidden]** {voice_channel.name} : **\n - - - {ten_thanh_vien}**"
                )
    await ctx.send(f"**Đã hoàn thành:** {len(danhsach_voice)} **kênh ẩn**")

token = os.getenv("TOKEN")

if token is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    print("✅ TOKEN đã được tìm thấy!")
    bot.run(token)

# @bot.command()
# async def translate(ctx, source_lang: str, target_lang: str, *, text: str):
#     try:
#         translator = Translator()
#         translated_text = translator.translate(text, src=source_lang, dest=target_lang)
#         translated_message = f"Dịch từ **{translated_text.src}** sang **{translated_text.dest}**:\n**{translated_text.text}**"

#         embed = discord.Embed(description=translated_message, color=discord.Color.blue())
#         await ctx.send(embed=embed)

#     except ValueError as e:
#         await ctx.send(f"**Đã xảy ra lỗi:** **{e}**")
