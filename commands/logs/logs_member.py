import discord
from discord.ext import commands

from functions import Utils

class LogsMember(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    def checks(self, guild: discord.Guild) -> discord.TextChannel|None:
        # Vérifications         
        if not self.utils.get_server_config(guild.id, "logs", "active"):
            return None

        logs_channel = self.utils.get_server_config(guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        return logs_channel


    # === Member ===
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logs_channel = self.checks(member.guild)
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un membre a rejoint le serveur", icon_url=member.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("notif"))

        embed.add_field(name="Membre", value=member.mention, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=member.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        logs_channel = self.checks(member.guild)
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un membre a quitté le serveur", icon_url=member.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("notif"))

        embed.add_field(name="Membre", value=member.name, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        logs_channel = self.checks(guild)
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un membre a été banni", icon_url=user.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("notif"))

        embed.add_field(name="Membre", value=user.name, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        logs_channel = self.checks(guild)
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un membre a été débanni", icon_url=user.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("notif"))

        embed.add_field(name="Membre", value=user.name, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        logs_channel = self.checks(before.guild)
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un membre a été modifié", icon_url=before.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("edit"))

        embed.add_field(name="Membre", value=before.mention, inline=True)
        

        # vérification des modifications
        if before.nick != after.nick:
            embed.add_field(name="Ancien pseudo", value=before.nick, inline=True)
            embed.add_field(name="Nouveau pseudo", value=after.nick, inline=True)

        if before.roles != after.roles:
            roles_diff = list(set(before.roles) - set(after.roles))

            if len(roles_diff) > 0:
                embed.add_field(name="Rôle retiré", value=roles_diff[0].mention, inline=True)
            else:
                embed.add_field(name="Rôle ajouté", value=list(set(after.roles) - set(before.roles))[0].mention, inline=True)

        embed.add_field(name=self.utils.invisible_string(), value=after.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsMember(bot))
