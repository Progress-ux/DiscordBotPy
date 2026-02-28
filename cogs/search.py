import discord
from discord.ext import commands
from discord import app_commands
from handler.track import Track
from utils.utils import extractInfoByTitle, createEmbed
from handler.music_handler import MusicHandler

class SearchCommand(commands.Cog):
   """
   A Discord bot cog that handles the '/play' slash command.
   This command allows users to add music tracks to a guild's queue and start playback.
   """
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="search", description="Play audio.")
   @app_commands.describe(title="The song to play (Name).")
   async def search(self, interaction: discord.Interaction, title: str):
      """
      The main handler for the /search slash command.

      Args:
          interaction: The Discord interaction object representing the command invocation.
          url: The URL provided by the user for the track to be played.
      """
      # --- 1. Pre-checks ---

      # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "common.not_in_voice"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Check if the bot is already connected to a voice channel in this guild
      if not interaction.guild.voice_client:
         # If not connected, display a message
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "common.bot_not_in_voice"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Defer the response because processing the URL might take time (API call)
      await interaction.response.defer()

      voice = interaction.guild.voice_client
      
      # Get the specific MusicHandler instance associated with this server (guild)
      guild_id = interaction.guild.id
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)
      
      # Ensure playback is not explicitly stopped if a new command is issued
      musicHandler.stop_flag = False
      
      try:
         # Use the MusicHandler to fetch track metadata from the URL (e.g., via yt-dlp)
         track: Track = await extractInfoByTitle(title)
      except Exception as e:
         # Handle potential errors during information extraction (e.g., video not found/private)
         await interaction.followup.send(
            content=self.bot.locale_manager.get_text(guild_id, "common.error", error=str(e)), 
         )
         return
      
      # --- 3. Add to Queue and Send Confirmation ---

      # Add the newly extracted track object to the queue
      musicHandler.add_track(track)

      # Create a rich embed message to confirm the track was added
      embed = createEmbed(track=track)

      # Mention the user who added the song
      embed.add_field(
         name=self.bot.locale_manager.get_text(guild_id, "common.added_by"), 
         value=f"<@{interaction.user.id}>", 
         inline=False
      ) 
      
      # Send the confirmation message in the channel
      await interaction.followup.send(embed=embed)

      # --- 4. Start Playback ---

      # If music is already actively playing (the queue loop is running), we just added to the queue, so we return.
      if voice.is_playing() or musicHandler.is_playing:
         return
      
      # If nothing was playing, start the playback loop using the MusicHandler's player method
      await musicHandler.player(voice=voice)

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the PlayCommand cog with the bot.
   """
   await bot.add_cog(SearchCommand(bot))
