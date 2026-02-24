import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler

class SkipCommand(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @app_commands.command(name="skip", description="Skips current track.")
   async def skip(self, interaction: discord.Interaction):
       # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content="You are not in a voice channel.",
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Get the specific MusicHandler instance associated with this server (guild)
      guild_id = interaction.guild.id
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)
      
      if musicHandler.queue_empty:
         await interaction.response.send_message(
            content="Queue is empty. I'm skipping the command.",
            ephemeral=True # Only the user sees this message
         )
         return

      musicHandler.skip_flag = True
      
      voice = interaction.guild.voice_client
      voice.stop()
      await interaction.response.send_message(
         content="Audio skipped.",
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