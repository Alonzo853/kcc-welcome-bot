import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio

# --- DATABASE SETUP ---
conn = sqlite3.connect("welcome_bot.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS settings (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel_id INTEGER
)
""")
conn.commit()

# --- INTENTS & BOT SETUP ---
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# --- UTILITIES ---
def set_welcome_channel(guild_id: int, channel_id: int):
    with sqlite3.connect("welcome_bot.db") as conn:
        c = conn.cursor()
        c.execute("REPLACE INTO settings (guild_id, welcome_channel_id) VALUES (?, ?)", (guild_id, channel_id))
        conn.commit()

def get_welcome_channel(guild_id: int):
    with sqlite3.connect("welcome_bot.db") as conn:
        c = conn.cursor()
        c.execute("SELECT welcome_channel_id FROM settings WHERE guild_id = ?", (guild_id,))
        result = c.fetchone()
        return result[0] if result else None

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_member_join(member):
    channel_id = get_welcome_channel(member.guild.id)
    if not channel_id:
        return

    channel = member.guild.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(
        title="Welcome to KCC !",
        description=f"Hello {member.mention} Welcome To KCC (:\nMake sure to read the <#123456789012345678> !",  # Replace with your rules channel ID
        color=discord.Color.purple()
    )
    embed.set_image(url="attachment://welcome_banner.png")

    file = discord.File("welcome_banner.png", filename="welcome_banner.png")
    await channel.send(embed=embed, file=file)

# --- SLASH COMMAND: /setchannel ---
@tree.command(name="setchannel", description="Set the welcome channel")
@app_commands.describe(channel="Channel to set for welcome messages")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_welcome_channel(interaction.guild.id, channel.id)
    await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}", ephemeral=True)

@setchannel.error
async def setchannel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ An error occurred.", ephemeral=True)

# --- RUN BOT ---
bot.run("YOUR_BOT_TOKEN")