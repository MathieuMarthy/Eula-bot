import os

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class PP_Banner(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(self.client)

        # === context menu ===
        self.ctx_menu_pp = app_commands.ContextMenu(name="pp", callback=self.pp_context_menu)
        self.client.tree.add_command(self.ctx_menu_pp)

        self.ctx_menu_banner = app_commands.ContextMenu(name="bannière", callback=self.banner_context_menu)
        self.client.tree.add_command(self.ctx_menu_banner)


    async def send(self, ctx: commands.Context, image: discord.Asset):
        if image is None:
            await ctx.send("Aucune image trouvée")
            return

        await ctx.interaction.response.defer()

        filename = "image.gif" if image.is_animated() else "image.png"
        file_path = os.path.join(self.utils.bot_path(), "tmp", filename)
        await image.save(file_path)

        file = discord.File(fp=file_path)
        await ctx.send(file=file)


    async def pp_command(self, ctx, member: discord.Member):
        await self.send(ctx, member.avatar)
    

    async def banner_command(self, ctx, member: discord.Member):
        member = await self.client.fetch_user(member.id)
        await self.send(ctx, member.banner)


    @app_commands.checks.has_permissions(administrator=True)
    async def pp_context_menu(self, interaction, member: discord.Member):
        ctx = await self.client.get_context(interaction)
        await self.pp_command(ctx, member)


    @commands.command()
    async def pp(self, ctx: commands.Context, member: str):
        if not await self.utils.is_user(member):
            await ctx.send("Je ne trouve pas cette personne")
            return

        member = ctx.guild.fetch_member(member)
        await self.pp_command(ctx, member)


    @app_commands.command(name="pp", description="envoie la pp d'une personne")
    @app_commands.describe(personne="la personne dont tu veux la pp")
    async def ppSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.pp_command(ctx, personne)


    @app_commands.checks.has_permissions(administrator=True)
    async def banner_context_menu(self, interaction, member: discord.Member):
        ctx = await self.client.get_context(interaction)
        await self.banner_command(ctx, member)


    @commands.command(aliases=["bannière", "banner"])
    async def banniere(self, ctx: commands.Context, member: str):
        if not await self.utils.is_user(member):
            await ctx.send("Je ne trouve pas cette personne")
            return

        member = ctx.guild.fetch_member(member)
        await self.banner_command(ctx, member)


    @app_commands.command(name="bannière", description="envoie la bannière d'une personne")
    @app_commands.describe(personne="la personne dont tu veux la bannière")
    async def bannerSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.banner_command(ctx, personne)


async def setup(bot):
    await bot.add_cog(PP_Banner(bot))
