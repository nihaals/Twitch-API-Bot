import discord
from discord.ext import commands

import cogs.utils.checks as checks

import asyncio


async def twitchSort(ctx, *, message: discord.Message = None):
    """Sorts all the categories and channels."""
    categoryBlacklist = ["Info", "Main", "", "Other", "Admin"]
    langCategories = [c for c in ctx.guild.categories if c.name not in categoryBlacklist]
    allLangChannels = []

    # Sort channels in each category
    if message:
        await message.edit(content="Sorting channels...")

    for langCategory in langCategories:
        langChannels = [channel for channel in langCategory.channels if isinstance(channel, discord.TextChannel)]
        allLangChannels.extend(langChannels)
        sortedOrder = sorted(langChannels, key=lambda c: c.name.lower())  # Sorted list of channels
        for channel in langChannels:
            if sortedOrder.index(channel) != channel.position:
                await channel.edit(position=sortedOrder.index(channel))  # Change position to match sorted order

    # Sort categories
    if message:
        await message.edit(content="Sorting categories...")

    sortedOrder = []
    for categoryName in categoryBlacklist:
        if categoryName:
            categoryObj = discord.utils.get(ctx.guild.categories, name=categoryName)
            if not categoryObj:
                await ctx.send(f"Can't find category `{categoryName}`")
                return

            sortedOrder.append(categoryObj)

        else:
            # Add sorted lang categories
            sortedLangCategories = sorted(langCategories, key=lambda c: c.name)
            sortedOrder.extend(sortedLangCategories)

    for category in langCategories:
        if sortedOrder.index(category) != category.position:
            await category.edit(position=sortedOrder.index(category))

    # Sort roles
    roles = getLibRoles(ctx.guild)

    # Check permissions
    if message:
        await message.edit(content="Checking role permissions...")

    emptyPerms = discord.Permissions.none()

    for role in roles:
        if role.permissions.value != 0:
            await role.edit(permissions=emptyPerms)

    # Sort roles
    if message:
        await message.edit(content="Sorting roles...")

    sortedRoles = sorted(roles, key=lambda r: r.name.lower())

    if sortedRoles != roles:
        if message:
            await message.edit(content="Moving roles...")

        closeRoleTagPos = discord.utils.get(ctx.guild.roles, name="</roles>").position  # TODO Might be None and error

        for role in roles:
            currentPos = role.position
            correctPos = closeRoleTagPos + len(roles) - sortedRoles.index(role)

            if currentPos != correctPos:
                await role.edit(position=correctPos)

    # if message:
    #     await message.edit(content="Checking channel matches...")
    #
    # roleNames = [r.name for r in roles]
    # roleNamesLowered = [rn.lower() for rn in roleNames]
    #
    # for channel in allLangChannels:
    #     roleName = f"{channel.category.name}: {channel.name}"
    #     if roleName not in roleNames:
    #         if roleName not in roleNamesLowered:
    #             await ctx.send(f"No role for `{channel.name}` ({channel.mention}).")
    #
    #         else:
    #             await ctx.send(f"Wrong capitalisation for role for `{channel.name}` ({channel.mention}).")
    #
    # if message:
    #     await message.edit(content="Checking role matches...")
    #
    # allChannelNamesRoles = [f"{c.category.name}: {c.name}" for c in allLangChannels]
    # allChannelNamesRolesLowered = [rn.lower() for rn in allChannelNamesRoles]
    #
    # for role in roles:
    #     if role.name not in allChannelNamesRoles:
    #         if role.name not in allChannelNamesRolesLowered:
    #             await ctx.send(f"No channel for `{role.name}` ({role.id})")
    #
    #         else:
    #             pass  # Already checked above

    if message:
        await message.edit(content=":thumbsup:")

    else:
        await ctx.send(":thumbsup:")


def getLibRoles(guild: discord.Guild):
    """Returns a list of library roles."""
    roles = []
    foo = False
    for role in guild.role_hierarchy:
        if role.name == "<roles>":
            foo = True
        elif role.name == "</roles>":
            break
        elif foo:
            roles.append(role)

    return roles


class Twitch:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions_owner(administrator=True)
    async def addlib(self, ctx, channelName, lang, dev: discord.Member):
        """Adds a library channel."""
        category = discord.utils.find(lambda c: c.name.lower() == lang.lower(), ctx.guild.categories)

        if not category:
            category = await ctx.guild.create_category(lang)

        channel = await ctx.guild.create_text_channel(channelName, category=category)

        permissions = discord.PermissionOverwrite()
        permissions.manage_channels = True
        permissions.manage_roles = True
        permissions.manage_webhooks = True
        permissions.manage_messages = True

        await channel.set_permissions(dev, overwrite=permissions)

        libraryDevRole = discord.utils.get(ctx.guild.roles, id=325553793833893888)

        if not libraryDevRole:
            await ctx.send("Can't find `Library Dev` role")

        else:
            await dev.add_roles(libraryDevRole)

        role = await ctx.guild.create_role(name=f"{lang}: {channelName}")
        await asyncio.sleep(3)

        closeRoleTag = discord.utils.get(ctx.guild.roles, name="</roles>")
        if not closeRoleTag:
            await ctx.send("Can't find closing role tag")

        else:
            pos = closeRoleTag.position
            await role.edit(position=pos+1)

        m = await ctx.send("Starting sorting...")

        await twitchSort(ctx, message=m)

    @commands.command(aliases=["sort"])
    @checks.has_permissions_owner(administrator=True)
    async def twitchsort(self, ctx):
        """Sorts all the categories and channels."""
        m = await ctx.send("Starting sorting...")
        await twitchSort(ctx, message=m)

    @commands.command(aliases=["twitchremoveroles", "trr"])
    @checks.has_permissions_owner(administrator=True)
    async def twitchrolesremove(self, ctx):
        """Removes all library roles."""
        roles = getLibRoles(ctx.guild)
        for role in roles:
            role.delete()

        await ctx.send(":thumbsup:")

    @commands.group(invoke_without_command=True, aliases=["role", "roles", "ranks"])
    async def rank(self, ctx):
        """Handles user's library roles."""
        helpText = (await self.bot.formatter.format_help_for(ctx, self.rank))[0]
        await ctx.send(helpText)

    @rank.command(name="list")
    async def _list(self, ctx):
        """Lists library roles."""
        roles = getLibRoles(ctx.guild)

        await ctx.send("All available roles are: `" + "`, `".join([r.name for r in roles]) + "`")

    @rank.command(name="join")
    async def _join(self, ctx, *, roleName):
        """Allows the user to join a library role."""
        roles = getLibRoles(ctx.guild)

        role = discord.utils.find(lambda r: r.name.lower() == roleName.lower(), roles)

        if not role:
            await ctx.send(f"Can't find a role with the name `{roleName}`. Run `list` to see a list of roles.")
            return

        if role in ctx.author.roles:
            await ctx.send(f"You already have the role `{roleName}`.")
            return

        await ctx.author.add_roles(role)
        await ctx.send(":thumbsup:")

    @rank.command(name="leave")
    async def _leave(self, ctx, *, roleName):
        """Allows the user to leave a library role."""
        roles = getLibRoles(ctx.guild)

        role = discord.utils.find(lambda r: r.name.lower() == roleName.lower(), roles)

        if not role:
            await ctx.send(f"Can't find a role with the name `{roleName}`. Run `list` to see a list of roles.")
            return

        if role not in ctx.author.roles:
            await ctx.send(f"You do not have the role `{roleName}`.")
            return

        await ctx.author.remove_roles(role)
        await ctx.send(":thumbsup:")


def setup(bot):
    bot.add_cog(Twitch(bot))
