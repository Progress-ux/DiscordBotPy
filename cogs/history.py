import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler
from utils.utils import createHistoryEmbed

class HistoryCommand(commands.Cog):
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="history", description="Shows the current history.")
   async def history(self, interaction: discord.Interaction):
      # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content="You are not in a voice channel.",
            ephemeral=True # Only the user sees this message
         )
         return
      
      await interaction.response.defer()

      # Get the specific MusicHandler instance associated with this server (guild)
      guild_id = interaction.guild.id
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)

      current_track = musicHandler.get_current_track()
      history_list = musicHandler.get_history()

      embed = createHistoryEmbed(current_track, history_list)

      await interaction.followup.send(embed=embed)
      
     

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the HistoryCommand cog with the bot.
   """
   await bot.add_cog(HistoryCommand(bot))
