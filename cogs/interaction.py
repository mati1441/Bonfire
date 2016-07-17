from discord.ext import commands
from .utils import config
from .utils import checks
from threading import Timer
import discord
import random

battling = False
battleP1 = None
battleP2 = None


def battlingOff():
    global battleP1
    global battleP2
    global battling
    battling = False
    battleP1 = ""
    battleP2 = ""


def updateBattleRecords(winner, loser):
    battles = config.getContent('battle_records')
    if battles is not None:
        record = battles.get(winner.id)
        if record is not None:
            result = record.split('-')
            result[0] = str(int(result[0]) + 1)
            battles[winner.id] = "-".join(result)
        record = battles.get(loser.id)
        if record is not None:
            result = record.split('-')
            result[1] = str(int(result[1]) + 1)
            battles[loser.id] = "-".join(result)
    else:
        battles = {winner.id:"1-0",loser.id:"0-1"}
    config.saveContent('battle_records',battles)


class Interaction:
    """Commands that interact with another user"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @checks.customPermsOrRole("none")
    async def battle(self, ctx, player2: discord.Member):
        """Challenges the mentioned user to a battle"""
        global battleP1
        global battleP2
        global battling
        if battling:
            return
        if len(ctx.message.mentions) == 0:
            await self.bot.say("You must mention someone in the room " + ctx.message.author.mention + "!")
            return
        if len(ctx.message.mentions) > 1:
            await self.bot.say("You cannot battle more than one person at once!")
            return
        if ctx.message.author.id == player2.id:
            await self.bot.say("Why would you want to battle yourself? Suicide is not the answer")
            return
        if self.bot.user.id == player2.id:
            await self.bot.say("I always win, don't even try it.")
            return
        fmt = "{0.mention} has challenged you to a battle {1.mention}\n!accept or !decline"
        battleP1 = ctx.message.author
        battleP2 = player2
        await self.bot.say(fmt.format(ctx.message.author, player2))
        t = Timer(180, battlingOff)
        t.start()
        battling = True

    @commands.command(pass_context=True, no_pm=True)
    @checks.customPermsOrRole("none")
    async def accept(self, ctx):
        """Accepts the battle challenge"""
        if not battling or battleP2 != ctx.message.author:
            return
        num = random.randint(1, 100)
        fmt = config.battleWins[random.randint(0, len(config.battleWins) - 1)]
        if num <= 50:
            await self.bot.say(fmt.format(battleP1.mention, battleP2.mention))
            updateBattleRecords(battleP1, battleP2)
            battlingOff()
        elif num > 50:
            await self.bot.say(fmt.format(battleP2.mention, battleP1.mention))
            updateBattleRecords(battleP2, battleP1)
            battlingOff()
            
    @commands.command(pass_context=True, no_pm=True)
    @checks.customPermsOrRole("none")
    async def decline(self, ctx):
        """Declines the battle challenge"""
        if not battling or battleP2 != ctx.message.author:
            return
        await self.bot.say("{0} has chickened out! {1} wins by default!".format(battleP2.mention, battleP1.mention))
        updateBattleRecords(battleP1, battleP2)
        battlingOff()
        
    @commands.command(pass_context=True, no_pm=True)
    @checks.customPermsOrRole("none")
    async def boop(self, ctx, boopee: discord.Member):
        """Boops the mentioned person"""
        booper = ctx.message.author
        if len(ctx.message.mentions) == 0:
            await self.bot.say("You must mention someone in the room " + ctx.message.author.mention + "!")
            return
        if len(ctx.message.mentions) > 1:
            await self.bot.say("You cannot boop more than one person at once!")
            return
        if boopee.id == booper.id:
            await self.bot.say("You can't boop yourself! Silly...")
            return
        if boopee.id == self.bot.user.id:
            await self.bot.say("Why the heck are you booping me? Get away from me >:c")
            return

        boops = config.getContent('boops')
        if boops is None:
            boops = {}
        amount = 1
        booper_boops = boops.get(ctx.message.author.id)
        if booper_boops is None:
            boops[ctx.message.author.id] = {boopee.id:1}
        elif booper_boops.get(boopee.id) is None:
            booper_boops[boopee.id] = 1
            boops[ctx.message.author.id] = booper_boops
        else:
            amount = booper_boops.get(boopee.id) + 1
            booper_boops[boopee.id] = amount
            boops[ctx.message.author.id] = booper_boops
            
        config.saveContent('boops',boops)
        fmt = "{0.mention} has just booped you {1.mention}! That's {2} times now!"
        await self.bot.say(fmt.format(booper, boopee, amount))


def setup(bot):
    bot.add_cog(Interaction(bot))
