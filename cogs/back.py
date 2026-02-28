import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler

class BackCommand(commands.Cog):
   """
   A Discord bot cog that handles the '/back' slash command.
   This command allows you to switch a track to the previous one. 
   If the history is empty, playback does not stop.
   """
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="back", description="Returns to the previous track.")
   async def back(self, interaction: discord.Interaction):
      guild_id = interaction.guild.id

      if not interaction.user.voice:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "common.not_in_voice"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Get the specific MusicHandler instance associated with this server (guild)
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)

      if musicHandler.history_empty:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "back.history_empty"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      musicHandler.back_flag = True
      
      voice = interaction.guild.voice_client
      voice.stop()
      await interaction.response.send_message(
         content=self.bot.locale_manager.get_text(guild_id, "back.returned"), 
      )

      if not voice.is_playing() and not musicHandler.is_playing:
         # If nothing was playing, start the playback loop using the MusicHandler's player method
         await musicHandler.player(voice=voice)

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the PlayCommand cog with the bot.
   """
   await bot.add_cog(BackCommand(bot))