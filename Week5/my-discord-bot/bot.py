import discord
from discord.ext import commands

import os
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Required for message reading

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}! 👋')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓')

@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(f'{a} + {b} = {a + b}')


TOKEN = os.getenv("DISCORD_TOKEN")
print("Starting bot...")
print(f"Using token: {TOKEN}")


bot.run(TOKEN)
