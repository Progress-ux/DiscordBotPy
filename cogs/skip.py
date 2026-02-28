import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler

class SkipCommand(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @app_commands.command(name="skip", description="Skips current track.")
   async def skip(self, interaction: discord.Interaction):
      guild_id = interaction.guild.id

      # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "common.not_in_voice"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Get the specific MusicHandler instance associated with this server (guild)
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)
      
      if musicHandler.queue_empty:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "skip.queue_empty"), 
            ephemeral=True # Only the user sees this message
         )
         return

      musicHandler.skip_flag = True
      
      voice = interaction.guild.voice_client
      voice.stop()
      await interaction.response.send_message(
         content=self.bot.locale_manager.get_text(guild_id, "skip.skipped"),
      )
      if not voice.is_playing() and not musicHandler.is_playing:
         # If nothing was playing, start the playback loop using the MusicHandler's player method
         await musicHandler.player(voice=voice)

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the SkipCommand cog with the bot.
   """
   await bot.add_cog(SkipCommand(bot))