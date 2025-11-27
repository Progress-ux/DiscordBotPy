import discord
from discord.ext import commands
from discord import app_commands
from handler.track import Track

class PlayCommand(commands.Cog):
   """
   A Discord bot cog that handles the '/play' slash command.
   This command allows users to add music tracks to a guild's queue and start playback.
   """
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="play", description="Play audio.")
   @app_commands.describe(url="The song to play (URL).")
   async def play(self, interaction: discord.Interaction, url: str):
      """
      The main handler for the /play slash command.

      Args:
          interaction: The Discord interaction object representing the command invocation.
          url: The URL provided by the user for the track to be played.
      """
      # --- 1. Pre-checks ---

      # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content="You are not in a voice channel.",
            ephemeral=True # Only the user sees this message
         )
         return
      
      # Defer the response because processing the URL might take time (API call)
      await interaction.response.defer()
      
      # Get the specific MusicHandler instance associated with this server (guild)
      guild_id = interaction.guild.id
      musicHandler = await self.bot.getMusicHandler(guild_id)
      
      # Ensure playback is not explicitly stopped if a new command is issued
      await musicHandler.setStopFlag(False)

      # --- 2. Validate and Extract Track Info ---

      # Check if the provided string looks like a valid URL
      if not await musicHandler.isValidUrl(url):
         await interaction.followup.send(content="Incorrect video link", ephemeral=True)
         return
      
      try:
         # Use the MusicHandler to fetch track metadata from the URL (e.g., via yt-dlp)
         track = await musicHandler.extractInfo(url)
      except Exception as e:
         # Handle potential errors during information extraction (e.g., video not found/private)
         await interaction.followup.send(content=f"Error: {e}")
         return
      
      # --- 3. Add to Queue and Send Confirmation ---

      # Add the newly extracted track object to the queue
      await musicHandler.addTrack(track)

      # Format the duration nicely (HH:MM:SS) for the embed message
      duration = track.getDuration()
      if duration:
         m, s = divmod(duration, 60)
         h, m = divmod(m, 60)
         if h:
            duration_str = f"{h}:{m:02d}:{s:02d}"
         else:
            duration_str = f"{m}:{s:02d}"
      else:
         duration_str = "-"

      # Create a rich embed message to confirm the track was added
      embed = discord.Embed(
         title=track.getTitle(),
         url=track.getUrl(),
         color=0x5865F2
      )
      embed.add_field(name="Author", value=track.getAuthor() or "Unknown", inline=True)
      embed.add_field(name="Duration", value=duration_str or "-", inline=True)
      # Mention the user who added the song
      embed.add_field(name="Added", value=f"<@{interaction.user.id}>", inline=False) 

      if track.getThumbnail():
         embed.set_thumbnail(url=track.getThumbnail())

      # Send the confirmation message in the channel
      await interaction.followup.send(embed=embed)

      # --- 4. Connect and Start Playback ---

      # Check if the bot is already connected to a voice channel in this guild
      if interaction.guild.voice_client:
         voice = interaction.guild.voice_client
      else:
         # If not connected, connect to the user's current voice channel
         voice = await interaction.user.voice.channel.connect()

      # If music is already actively playing (the queue loop is running), we just added to the queue, so we return.
      if voice.is_playing():
         return
      
      # If nothing was playing, start the playback loop using the MusicHandler's player method
      await musicHandler.player(voice=voice)

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the PlayCommand cog with the bot.
   """
   await bot.add_cog(PlayCommand(bot))
