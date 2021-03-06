import asyncio
import discord
from   Cogs import Nullify
from   Cogs import DisplayName
from   Cogs import Message
from   discord.ext import commands
import json
import os
import mtranslate

def setup(bot):
	# Add the bot and deps
	settings = bot.get_cog("Settings")
	bot.add_cog(Translate(bot, settings))

# Requires the mtranslate module be installed

class Translate:
            
    def __init__(self, bot, settings, language_file = "Languages.json"):
        self.bot = bot
        self.settings = settings

        if os.path.exists(language_file):
            f = open(language_file,'r')
            filedata = f.read()
            f.close()
            self.languages = json.loads(filedata)
        else:
            self.languages = []
            print("No {}!".format(language_file))

    @commands.command(pass_context=True)
    async def langlist(self, ctx):
        """Lists available languages."""
        if not len(self.languages):
            await ctx.send("I can't seem to find any languages :(")
            return
        description = ""
        for lang in self.languages:
                description += "**{}** - {}\n".format(lang["name"], lang["code"])
        await Message.EmbedText(title="Language List",
                force_pm=True,
                description=description,
                color=ctx.author,
                footer="Note - some languages may not be supported."
        ).send(ctx)
        '''# Pm languages to author
        await ctx.send("I'll pm them to you.")
        msg = "Languages:\n\n"
        for lang in self.languages:
            msg += lang["Name"] + "\n"
        await ctx.author.send(msg)'''

    @commands.command(pass_context=True)
    async def tr(self, ctx, *, translate = None):
        """Translate some stuff!"""

        # Check if we're suppressing @here and @everyone mentions
        if self.settings.getServerStat(ctx.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        usage = "Usage: `{}tr [words] [language code]`".format(ctx.prefix)
        if translate == None:
            await ctx.send(usage)
            return

        word_list = translate.split(" ")

        if len(word_list) < 2:
            await ctx.send(usage)
            return

        lang = word_list[len(word_list)-1]
        trans = " ".join(word_list[:-1])

        lang_code = None

        for item in self.languages:
            if item["code"].lower() == lang.lower():
                lang_code = item["code"]
                break
        
        if not lang_code:
            await Message.EmbedText(
                        title="Something went wrong...",
                        description="I couldn't find that language!",
                        color=ctx.author
                ).send(ctx)
            return

        result = mtranslate.translate(trans, lang_code, "auto")
        
        if not result:
            await Message.EmbedText(
                        title="Something went wrong...",
                        description="I wasn't able to translate that!",
                        color=ctx.author
                ).send(ctx)
            return
        
        if result == trans:
                # We got back what we put in...
                await Message.EmbedText(
                        title="Something went wrong...",
                        description="The text returned from Google was the same as the text put in.  Either the translation failed - or you were translating from/to the same language (en -> en)",
                        color=ctx.author
                ).send(ctx)
                return

        # Check for suppress
        if suppress:
            result = Nullify.clean(result)

        await Message.EmbedText(
                title="{}, your translation is:".format(DisplayName.name(ctx.author)),
                force_pm=True,
                color=ctx.author,
                description=result,
                footer="Powered by Google Translate"
        ).send(ctx)
        # await ctx.send("*{}*, your translation is:\n\n{}".format(DisplayName.name(ctx.author), result))
