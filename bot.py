import os
import random

import discord
from discord.ext import commands

from database import Database
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix=os.getenv('PREFIX'))
data = Database(os.getenv('DATABASE'))


@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected to Discord now!')


@bot.command(
    name='roll', 
    help="""Simulate rolling dice.
    Syntax: !r [NumberOfDices]d[NumberOfSides]
         or !r [NumberOfSides] if you want to roll with one dice
    Example: !r 2d10""",
    aliases=['r']    
)
async def roll(ctx, dices="100"):
    if "d" in dices:
        numberOfDices, numberOfSides = tuple(map(int,dices.split("d")))
    else:
        numberOfDices, numberOfSides = 1, int(dices)
    rolls = [random.randint(0,numberOfSides - 1) for _ in range(numberOfDices)]
    results = ", ".join(map(str,rolls))
    response = f'**{ctx.author.nick}** is rolling {dices}:\n`{results}`'
    await ctx.send(response)


@bot.command(
    name='set',
    help="""Set your character attribute's value
    Separate <attribute> and <value> with colon
    You can specify many pairs separating them with spaces
    If you need to use spaces inside attribute or value use double quotes outside this attribute/value

    Syntax !s <attribute#1>:<value#1> <attribute#2>:<value#2>
    Example: !s age:22 name:\"Adam Herling\"""",
    aliases=['s']
)
async def setAttribute(ctx, *pairs):
    players = data.getPlayers()
    playerID = str(ctx.author.id)
    if playerID not in players.keys():
        players[playerID] = {}

    if len(pairs) == 0:
        await ctx.send(f"**{ctx.author.nick}**, you need to specify at least one pair `<attribute>:<value>`")
        return
    
    logs = ""
    for pair in pairs:
        try:
            attribute, value = pair.split(":")
            players[playerID][attribute] = value
            logs += f"\n{attribute}: {value}"
        except ValueError:
            logs += f"\nUnable to set attribute's value for `{pair}`"
    data.savePlayers(players)
    response = f"Set attributes for **{ctx.author.nick}**:{logs}"
    await ctx.send(response)

@bot.command(
    name='delete',
    help="""Delete your character attributes
    You can specify many attributes separating them with spaces
    If you need to use spaces inside attribute use double quotes outside this attribute
    You can delete all your attributes using "--all" 
""",
    aliases=['del']
)
async def deleteAttribute(ctx, *attributes):
    players = data.getPlayers()
    playerID = str(ctx.author.id)
    if playerID not in players.keys():
        await ctx.send(f"There is no record of **{ctx.author.nick}** in database, sorry.")
        return

    if len(attributes) == 0:
        await ctx.send(f"**{ctx.author.nick}**, you need to specify at least one attribute to delete")
        return

    if "--all" in attributes:
        attributes = list(players[playerID].keys())
    
    logs = ""
    for attribute in attributes:
        if attribute not in players[playerID].keys():
            logs += f"\nThere is no atrribute `{attribute}` to delete"
            continue
        players[playerID].pop(attribute)
        logs += f"\n{attribute}"
    data.savePlayers(players)
        
    response = f"Deleted attributes for **{ctx.author.nick}**:{logs}"
    await ctx.send(response)


@bot.command(
    name='get',
    help="""Get your character attributes' value
    You can specify many attributes separating them with spaces
    Default return all attributes""",
    aliases=['g']
)
async def getAttribute(ctx, *attributes):
    players = data.getPlayers()
    playerID = str(ctx.author.id)
    if playerID not in players.keys():
        await ctx.send(f"There is no record of **{ctx.author.nick}** in database, sorry.")
        return

    logs = ""
    if len(attributes) == 0:
        attributes = players[playerID].keys()

    for attribute in attributes:
        if attribute not in players[playerID].keys():
            logs += f"\nThere is no atrribute `{attribute}`"
            continue
        value = players[playerID].get(attribute)
        logs += f"\n{attribute}: {value}"
        
    response = f"**{ctx.author.nick}**'s attributes:{logs}"
    await ctx.send(response)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))