import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler
from handler.queue_manager import RepeatMode

class RepeatAllCommand(commands.Cog):
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="repeat_all", description="Enables/disables repeating the current queue")
   async def leave(self, interaction: discord.Interaction):
      if not interaction.user.voice:
         await interaction.response.send_message(
            content="You are not in a voice channel.",
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Get the specific MusicHandler instance associated with this server (guild)
      guild_id = interaction.guild.id
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)
      
      new_mode = musicHandler.toggle_repeat_mode(RepeatMode.ALL)

      await interaction.response.send_message(
         content=new_mode.status_message,
      )

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the PlayCommand cog with the bot.
   """
   await bot.add_cog(RepeatAllCommand(bot))