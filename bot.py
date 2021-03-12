import os
import discord
from dotenv import load_dotenv
from model import naive_bayes as nb
from discord.ext import commands
from discord.ext.commands import Bot

GOOD = '\N{THUMBS UP SIGN}'
BAD = '\N{THUMBS DOWN SIGN}'
IDK = '\N{Eyes}'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = '.'
bot = Bot(PREFIX)

PATH_STOP = "model/stop.txt"
PATH_MODEL = "model/model.pkl"

model = nb.Model(PATH_MODEL, PATH_STOP)


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

    positive = model.message_is_positive(message.content)

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
    WEIGHT = 2
    if emoji == GOOD:
        model.add_data(("%s " % data) * WEIGHT, True)
    elif emoji == BAD:
        model.add_data(("%s " % data) * WEIGHT, False)

    # expensive, try saving on set intervals given there are changes.
    model.model.to_pickle(PATH_MODEL)

    print(model)


@bot.command(name='top')
async def top(ctx):
    temp = model.model.copy()
    temp['diff'] =  temp['word|pos'] - temp['word|neg']
    temp = temp.sort_values(by=['diff'],ascending=False)
    await ctx.send("```%s```"%temp)
    print("sent")


bot.run(TOKEN)
