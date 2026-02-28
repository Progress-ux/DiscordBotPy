import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler

class StopCommand(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @app_commands.command(name="stop", description="Stops playback.")
   async def stop(self, interaction: discord.Interaction):
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

      voice = interaction.guild.voice_client

      if not voice.is_playing() or not musicHandler.is_playing:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "stop.nothing_playing"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      musicHandler.stop_flag = True
      voice.stop()

      await interaction.response.send_message(
         content=self.bot.locale_manager.get_text(guild_id, "stop.stopped"), 
      )

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the SkipCommand cog with the bot.
   """
   await bot.add_cog(StopCommand(bot))