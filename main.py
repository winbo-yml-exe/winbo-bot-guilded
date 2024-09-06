import random
import json
import os
import glob
from pathlib import Path
import guilded
from guilded.ext import commands
import platform
import psutil
from datetime import datetime
import requests

client = commands.Bot(command_prefix="w!")
serverdb = {}
cgcdb = {}
sad_stories = [
    "Winbo found a note in his mailbox: \"I’m sorry I couldn’t stay. Goodbye.\" He never saw his friend again.",
    "Winbo celebrated his birthday alone, his closest friends having forgotten the day entirely.",
    "Winbo sat in the chair that once held his best friend. The empty seat was a constant, painful reminder of his absence.",
    "Winbo found an old letter from a friend that was never read. The words of regret and apology were now lost to time.",
    "Winbo waited for his partner to remember their anniversary, but as the day passed without a word, the silence spoke volumes.",
    "Winbo looked at the last photo taken with his family before they drifted apart. The image was a bittersweet memory of happier times.",
    "Winbo’s phone remained silent, filled with messages from friends he could no longer reach. The emptiness of unreturned calls was deafening."
]
async def getairesponse(question):
    url = 'https://gpt4o-kohl.vercel.app/chat'
    payload = {
        'message': question,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('response', 'noresponse')
    else:
        return f"err-{response.status_code}-{response.text}"
try:
    if not os.path.isfile("serverdb.json"):
        with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
            json.dump(serverdb, sdbfile, indent=2)
            print("Created serverdb.json")
    else:
        with open("serverdb.json", "r", encoding="utf-8") as sdbfile:
            serverdb = json.load(sdbfile)
            print("Loaded serverdb.json")
except:
    pass
try:
    if not os.path.isfile("cgcdb.json"):
        with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
            json.dump(cgcdb, cgcdbfile, indent=2)
            print("Created serverdb.json")
    else:
        with open("serverdb.json", "r", encoding="utf-8") as cgcdbfile:
            cgcdb = json.load(cgcdbfile)
            print("Loaded cgcdb.json")
except:
    pass
try:
    if cgcdb["bans"]:
        cgcdb["bans"] = []
except:
    cgcdb["bans"] = []
with open("owner.txt", "r", encoding="utf-8") as ownerfile:
    owner = str(ownerfile.read().rstrip())
    cgcdb["owner"] = owner
    with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
        json.dump(cgcdb, cgcdbfile, indent=2)
        print("Loaded owner.txt")
with open("staff.txt", "r", encoding="utf-8") as stafffile:
    staff = str(stafffile.read().rstrip()).split(", ")
    cgcdb["staff"] = staff
    with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
        json.dump(cgcdb, cgcdbfile, indent=2)
        print(f"Loaded staff.txt ({staff})")

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")

async def on_message(message):
    if not message.author.bot and not str(message.author.id) in cgcdb["bans"]:
        for server in serverdb:
            await send_message_to_servers(message, server)

async def send_message_to_servers(message, server):
    if str(message.channel.id) == str(serverdb[server]["cgcchannel"]):
        for server in serverdb:
            try:
                embed = guilded.Embed(title=f"Message by {message.author.name}")
                channel = client.get_channel(int(serverdb[server]["cgcchannel"]))
                embed.description = message.content
                if str(message.author.id) == cgcdb["owner"]:
                    embed.set_footer(text=f"{message.author.name} - Owner - {message.server.name}")
                elif str(message.author.id) in cgcdb["staff"]:
                    embed.set_footer(text=f"{message.author.name} - Staff - {message.server.name}")
                else:
                    embed.set_footer(text=f"{message.author.name} - {message.server.name}")
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)
                await channel.send(embed=embed)
            except Exception as excp:
                print(excp)
                pass
        try:
            await message.delete()
        except:
            pass

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 {round(client.latency * 1000)}ms")

@client.command()
async def sadstory(ctx):
    message = random.choice(sad_stories)
    await ctx.send(message)

@client.command()
async def mute(ctx, member: guilded.Member, reason: str = "No reason provided"):
    if ctx.author.has_permission("manageRoles"):
        mute_role = guilded.utils.get(ctx.guild.roles, name="Muted")
        if mute_role is None:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        if mute_role in member.roles:
            await ctx.send(f"{member.mention} is already muted!")
        else:
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f"Muted {member.mention} for {reason}")
    else:
        await ctx.send("You do not have permission to mute members.")

@client.command()
async def unmute(ctx, member: guilded.Member):
    if ctx.author.has_permission("manageRoles"):
        mute_role = guilded.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"Unmuted {member.mention}")
        else:
            await ctx.send("Member is not muted.")
    else:
        await ctx.send("You do not have permission to unmute members.")

@client.command()
async def ban(ctx, member: guilded.Member, reason: str = "No reason provided"):
    if ctx.author.has_permission("banMembers"):
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention} for {reason}")
    else:
        await ctx.send("You do not have permission to ban members.")

@client.command()
async def unban(ctx, member: guilded.Member):
    if ctx.author.has_permission("banMembers"):
        await ctx.guild.unban(member)
        await ctx.send(f"Unbanned {member.mention}")
    else:
        await ctx.send("You do not have permission to unban members.")
    
@client.command()
async def purge(ctx, amount: int):
    if ctx.author.has_permission("manageMessages"):
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Deleted {len(deleted) - 1} messages.")
    else:
        await ctx.send("You do not have permission to manage messages.")

@client.command()
async def warn(ctx, member: guilded.Member, reason: str):
    server_id = str(ctx.guild.id)
    member_id = str(member.id)
    if server_id not in serverdb:
        serverdb[server_id] = {}
    if "warns" not in serverdb[server_id]:
        serverdb[server_id]["warns"] = {}
    if member_id not in serverdb[server_id]["warns"]:
        serverdb[server_id]["warns"][member_id] = []
    serverdb[server_id]["warns"][member_id].append(reason)
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)
    await ctx.send(f"Warned {member.mention} for {reason}")

@client.command()
async def warns(ctx, member: guilded.Member):
    server_id = str(ctx.guild.id)
    member_id = str(member.id)
    warns = serverdb.get(server_id, {}).get("warns", {}).get(member_id, [])
    if warns:
        embed = guilded.Embed(color=guilded.Color.red(), title=f"{member}'s warnings", description="\n".join(warns))
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.mention} has no warnings.")

@client.command()
async def askai(ctx, *, prompt: str):
    response = await getairesponse(prompt)
    if response.startswith("err"):
        code, message = response.split("-")[1:3]
        embed = guilded.Embed(color=guilded.Color.red(), title="Error", description=f"Code: {code}, Message: {message}")
    else:
        embed = guilded.Embed(color=guilded.Color.blue(), title="AI Response", description=response)
    await ctx.send(embed=embed)

@client.command(name="unwarn", description="Removes a warn from a member")
async def unwarn(ctx, member: guilded.Member, warningreason: str):
    try:
        if serverdb[str(ctx.server.id)]:
            try:
                if not serverdb[str(ctx.server.id)]["warns"]:
                    serverdb[str(ctx.server.id)]["warns"] = {}
            except:
                serverdb[str(ctx.server.id)]["warns"] = {}
        else:
            serverdb[str(ctx.server.id)] = {}
            serverdb[str(ctx.server.id)]["warns"] = {}
    except:
        serverdb[str(ctx.server.id)] = {}
        serverdb[str(ctx.server.id)]["warns"] = {}
    try:
        if not serverdb[str(ctx.server.id)]["warns"][str(member.id)]:
            serverdb[str(ctx.server.id)]["warns"][str(member.id)] = []
    except:
        serverdb[str(ctx.server.id)]["warns"][str(member.id)] = []
    
    if warningreason in serverdb[str(ctx.server.id)]["warns"][str(member.id)]:
        serverdb[str(ctx.server.id)]["warns"][str(member.id)].remove(warningreason)
        with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
            json.dump(serverdb, sdbfile, indent=2)
        embed = guilded.Embed(color=0x00ff00, title=f"Removed a warning from {member.name}", description=f"Removed the warning '{warningreason}' from {member.name}.")
        await ctx.send(embed=embed)
    else:
        embed = guilded.Embed(color=0xff0000, title="Couldn't find such a warning", description=f"Couldn't find '{warningreason}' in {member.name}'s warnings.")
        await ctx.send(embed=embed)

@client.command(name="clearwarns", description="Clears all warns given to a member")
async def clearwarns(ctx, member: guilded.Member):
    try:
        serverdb[str(ctx.server.id)]["warns"][str(member.id)] = []
        await ctx.send(f"Cleared all warnings for {member.mention}")
    except:
        await ctx.send(f"{member.mention} has no warnings")

@client.group()
async def cgc(ctx):
    pass

@cgc.command()
async def set_cgc(ctx):
    try:
        if serverdb[str(ctx.server.id)]:
            serverdb[str(ctx.server.id)]["cgcchannel"] = str(ctx.channel.id)
        else:
            serverdb[str(ctx.server.id)] = {}
            serverdb[str(ctx.server.id)]["cgcchannel"] = str(ctx.channel.id)
    except:
        serverdb[str(ctx.server.id)] = {}
        serverdb[str(ctx.server.id)]["cgcchannel"] = str(ctx.channel.id)
    
    await ctx.send("Set channel for CGC-chatting successfully!")
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)

@cgc.command()
async def unset_cgc(ctx):
    try:
        serverdb[str(ctx.server.id)]["cgcchannel"] = "None"
    except:
        pass
    await ctx.send("Unset channel for CGC-chatting successfully!")
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)

@cgc.command()
async def ban_cgc(ctx, member: guilded.Member):
    if str(ctx.author.id) in cgcdb["staff"] or str(ctx.author.id) == cgcdb["owner"]:
        try:
            if cgcdb:
                try:
                    if not cgcdb["bans"]:
                        cgcdb["bans"] = []
                except:
                    cgcdb["bans"] = []
        except:
            pass
        cgcdb["bans"].append(str(member.id))
        with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
            json.dump(cgcdb, cgcdbfile, indent=2)
        await ctx.send(f"Banned {member.name}")

@cgc.command()
async def unban_cgc(ctx, member: guilded.Member):
    if str(ctx.author.id) in cgcdb["staff"] or str(ctx.author.id) == cgcdb["owner"]:
        try:
            cgcdb["bans"].remove(str(member.id))
            with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
                json.dump(cgcdb, cgcdbfile, indent=2)
            await ctx.send(f"Unbanned {member.name}.")
        except:
            await ctx.send(f"{member.name} is not banned.")

client.run("TOKEN_GOES_HERE")
