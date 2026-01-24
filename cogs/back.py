import discord
from discord.ext import commands
from discord import app_commands

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
      if not interaction.user.voice:
         await interaction.response.send_message(
            content="You are not in a voice channel.",
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Get the specific MusicHandler instance associated with this server (guild)
      guild_id = interaction.guild.id
      musicHandler = await self.bot.getMusicHandler(guild_id)

      if musicHandler.isHistoryEmpty():
         await interaction.response.send_message(
            content="History is empty. I'm skipping the command.",
            ephemeral=True # Only the user sees this message
         )
         return
      
      musicHandler.setBackFlag(True)
      
      voice = interaction.guild.voice_client
      voice.stop()
      await interaction.response.send_message(
         content="I return to the previous track.",
      )

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the PlayCommand cog with the bot.
   """
   await bot.add_cog(BackCommand(bot))