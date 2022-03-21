import os
import requests
import pandas as pd
from discord.ext.commands import Bot
import urllib.parse

GOOD = '\N{THUMBS UP SIGN}'
BAD = '\N{THUMBS DOWN SIGN}'
IDK = '\N{Eyes}'

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = '.'
bot = Bot(PREFIX)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith(PREFIX):
        await bot.process_commands(message)
        return

    resp = requests.get("http://localhost/predict?msg=%s" % urllib.parse.quote("my text that should work"))
    positive = float(resp.text) > 0

    if positive > 0:
        emoji = GOOD
    elif positive < 0:
        emoji = BAD
    else:
        emoji = IDK

    await message.add_reaction(emoji)


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    data = reaction.message.content
    emoji = reaction.emoji

    requests.post("http://localhost/add", json={
        "text": data,
        "positive": emoji == GOOD
    })


@bot.command(name='top')
async def top(ctx):
    resp = requests.get("http://localhost/top")
    temp = pd.read_json(resp.text)
    temp['diff'] = temp['word|pos'] - temp['word|neg']
    temp = temp.sort_values(by=['diff'], ascending=False)
    await ctx.send("```%s```" % temp)

bot.run(TOKEN)
