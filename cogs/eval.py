from discord.ext import commands
import inspect
import io
from contextlib import redirect_stdout
import textwrap
import traceback
import BotIDs
import discord
import cogs.utils.checks as checks

class Eval():
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        if content.startswith("```") and content.endswith("```"):
            output = content[3:-3].rstrip("\n").lstrip("\n")
            return output

        # remove `foo`
        return content.strip("` \n")

    def get_syntax_error(self, e):
        if e.text is None:
            return "```py\n{0.__class__.__name__}: {0}\n```".format(e)
        return "```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```".format(e, "^", type(e).__name__)

    @commands.command(hidden=True)
    @checks.is_dev()
    async def eval(self, ctx, *, code: str):
        original = ctx.message

        code = code.strip("`")
        python = "{}"
        result = None

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "guild": ctx.message.guild,
            "channel": ctx.message.channel,
            "author": ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.channel.send(python.format(type(e).__name__ + ": " + str(e)))
            await ctx.message.delete()
            return

        lines = ["```py"]
        lines.append(f">>> {code}")
        lines.append(">>> {}".format(python.format(result)))
        lines.append("```")

        await ctx.send("\n".join(lines))

    @commands.command(name="exec", aliases = ["ex", "exed"], hidden=True)
    @checks.is_dev()
    async def _exec(self, ctx, *, body: str):
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "server": ctx.guild,
            "message": ctx.message,
            "_": self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = "async def func():\n{}".format(textwrap.indent(body, "  "))

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(self.bot.blank + "```py\n{}{}\n```".format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await ctx.send(self.bot.blank + "```py\n%s\n```" % value)
            else:
                self._last_result = ret
                await ctx.send(self.bot.blank + "```py\n%s%s\n```" % (value, ret))

def setup(bot):
    bot.add_cog(Eval(bot))