import discord
from discord.ext import commands, tasks
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

hello_message = None
target_channel_id = 1119263575836471377

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    check_roles_task.start()

@bot.event
async def on_voice_state_update(member, before, after):
    role_mappings = {
        1119248565261303828: 1135685942053715998,
        1119248760535531621: 1135685968318451792,
        1119248830664278116: 1135685998194470922
    }
    log_channel_id = 1136224937460387932  # Channel ID for logging

    # Check if the user left a voice channel
    if before.channel and not after.channel:
        for role_id in role_mappings.values():
            role = discord.utils.get(member.guild.roles, id=role_id)
            if role and role in member.roles:
                await member.remove_roles(role)
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Role Removed",
                        description=f"{role.mention} was removed from {member.mention} as they left the voice channel.",
                        color=discord.Color.red()
                    )
                    await log_channel.send(embed=embed)
    else:
        # Check if the user joined or moved to a voice channel
        if after.channel:
            role_id = role_mappings.get(after.channel.id)
            if role_id:
                role = discord.utils.get(member.guild.roles, id=role_id)
                if role:
                    await member.add_roles(role)
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        embed = discord.Embed(
                            title="Role Added",
                            description=f"{role.mention} was added to {member.mention} as they joined/moved to a voice channel.",
                            color=discord.Color.green()
                        )
                        await log_channel.send(embed=embed)


@bot.command()
async def delete(ctx):
    allowed_user_id = 727275632945266850  # Replace this with the specific user ID

    if ctx.author.id != allowed_user_id:
        await ctx.send("You are not allowed to use this command.")
        return

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["y", "yes", "n", "no"]

    await ctx.send("Are you sure you want to delete all messages in this channel? (Y/N)")
    try:
        confirmation = await bot.wait_for("message", check=check, timeout=15.0)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. The deletion process has been canceled.")
        return

    if confirmation.content.lower() in ["y", "yes"]:
        await ctx.channel.purge(limit=None)
        await ctx.send("All messages in this channel have been deleted.")
    else:
        await ctx.send("Deletion process canceled.")






@bot.event
async def on_message(message):
    global hello_message

    if not message.author.bot and message.channel.id == target_channel_id:
        if hello_message:
            await hello_message.delete()

        embed = discord.Embed(
            description="# **حفاظا على رأي عملائنا، فهو متاح الآن على موقعنا**\n[**اضغط هنا لتوجه الى الموقع**](https://realspoofer.shop/discord-room)",
            color=discord.Color.blue()
        )

        hello_message = await message.channel.send(embed=embed)

    await bot.process_commands(message)


@bot.command()
async def come(ctx, user: discord.User):
    room_id = ctx.channel.id
    message = f'**يرجى مرجعة تذكرة الخاصة بك** ... [ <#{room_id}> ] - {user.mention}'

    # Send the message
    await user.send(message)

    # Delete the command message
    await ctx.message.delete()


# Function to check and remove roles from users not in a voice channel
async def check_and_remove_roles():
    role_mappings = {
        1119248565261303828: 1135685942053715998,
        1119248760535531621: 1135685968318451792,
        1119248830664278116: 1135685998194470922
    }

    for guild in bot.guilds:
        for member in guild.members:
            for role_id in role_mappings.values():
                role = discord.utils.get(guild.roles, id=role_id)
                if role and role in member.roles and not member.voice:
                    await member.remove_roles(role)
                    log_channel_id = 1136224937460387932  # Channel ID for logging
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        log_message = f"Removed role {role.name} from {member.mention} as they are not in a voice channel."
                        await log_channel.send(log_message)
                    print(log_message)

# Schedule the task to run every 1 minute (adjust the time interval as needed)
@tasks.loop(minutes=1)
async def check_roles_task():
    await check_and_remove_roles()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token


# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run("")
