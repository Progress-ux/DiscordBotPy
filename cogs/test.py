import discord
from discord.ext import commands
from discord import app_commands

class Test(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   # @commands.Cog.listener()
   # async def on_ready(self):
   #    print(f"{__name__} is online!")
   
   @app_commands.command(name="ping", description="reply Pong!")
   async def ping(self, interaction: discord.Interaction):
      await interaction.response.defer()

      ping_embed = discord.Embed(title="Ping", description="Latency in ms", color=discord.Color.blue())
      ping_embed.add_field(name=f"{self.bot.user.name}'s Latancy (ms): ", value=f"{round(self.bot.latency * 1000)}ms.", inline=False)
      ping_embed.set_footer(text=f"Requested by {interaction.user.display_name}.", icon_url=interaction.user.avatar.url)

      await interaction.followup.send(embed=ping_embed)

async def setup(bot):
   await bot.add_cog(Test(bot))