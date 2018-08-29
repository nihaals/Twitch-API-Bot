import discord
from discord.ext import commands

class Forward():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if not message.guild:
            dev: discord.Member =
            quote = None
            quote = message
            embed = discord.Embed(description=quote.content)
            embed.set_author(name=quote.author.name, icon_url=quote.author.avatar_url)
            embed.set_footer(text=(quote.created_at))
            dev.send(embed=embed)

def setup(bot):
    bot.add_cog(Forward(bot))