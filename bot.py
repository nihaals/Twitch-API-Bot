import discord
from discord.ext import commands
import BotIDs
import traceback
import sys
import cogs.utils.prefix as Prefixes
import cogs.utils.checks as checks

description = f"A bot built by Orangutan Gaming ({BotIDs.dev_name}, {BotIDs.dev_id}) for the Twitch API Discord server"

prefixes = Prefixes.prefixes
bot = commands.Bot(command_prefix=commands.when_mentioned_or(*prefixes), description=description)
bot.blank = "\u200B"
bot.config = BotIDs.settings
bot.prefixes = prefixes

startup_extensions = ["cogs.eval",
                      "cogs.twitch"
                      ]

@bot.event
async def on_ready():
    gamename="with OG|t!help"
    await bot.change_presence(activity=discord.Game(name=gamename))
    print("Logged in as")
    print("Name: " + str(bot.user))
    print("ID: " + str(bot.user.id))
    print("Playing", gamename)
    print(BotIDs.URL)
    print("Prefixes: " + Prefixes.Prefix('"'))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

@bot.command()
@checks.is_dev()
async def load(ctx, extension_name: str):
    """Loads a module."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send(bot.blank + "```py\n{}: {}\n```".format(type(e).__name__, str(e)), delete_after=3)
        return
    await ctx.send(bot.blank + "{} loaded.".format(extension_name), delete_after=3)

@bot.command()
@checks.is_dev()
async def unload(ctx, extension_name: str):
    """Unloads a module."""
    bot.unload_extension(extension_name)
    await ctx.send(bot.blank + "{} unloaded.".format(extension_name), delete_after=3)
    
@bot.command(name="reload")
@checks.is_dev()
async def _reload(ctx, *, module: str):
    """Reloads a module."""
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except Exception as e:
        await ctx.send("{}: {}".format(type(e).__name__, e))
    else:
        await ctx.send(":thumbsup:")

@bot.command()
@checks.is_dev()
async def shutdown(ctx):
    """Shutdown."""
    try:
        await ctx.send("System Shutting down.")
        await bot.logout()
        await bot.close()
    except:
        await ctx.send("Error!")

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension, exc))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        try: await ctx.channel.send(error)
        except: return
    elif isinstance(error, commands.errors.CommandNotFound):
        try: await ctx.channel.send("`{}` is not a valid command".format(ctx.invoked_with))
        except: return
    elif isinstance(error, commands.errors.CommandInvokeError):
        print(f"In {ctx.command.qualified_name}:", file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print(f"{error}", file=sys.stderr)
    elif isinstance(error, discord.Forbidden):
        try: await ctx.channel.send("I do not have permissions")
        except: return
    elif isinstance(error, commands.errors.BadArgument):
        try: await ctx.channel.send(f"Bad Argument: {error}")
        except: return
    elif isinstance(error, commands.errors.CheckFailure):
        try: await ctx.channel.send(f"You do not have permission to use the command `{ctx.invoked_with}`.")
        except: return
    else:
        print(f"In {ctx.command.qualified_name}:", file=sys.stderr)
        traceback.print_tb(error.__traceback__)
        print(f"{error.__class__.__name__}: {error}", file=sys.stderr)

bot.run(BotIDs.token)
