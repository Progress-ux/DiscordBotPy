import discord
from discord.ext import commands
from discord import app_commands
from handler.track import Track

class PlayCommand(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @app_commands.command(name="play", description="Play audio.")
   @app_commands.describe(url="The song to play (URL).")
   async def play(self, interaction: discord.Interaction, url: str):
      if not interaction.user.voice:
         await interaction.response.send_message(
               content="You are not in a voice channel.",
               ephemeral=True
         )
         return
      
      await interaction.response.defer()
      
      guild_id = interaction.guild.id

      musicHandler = await self.bot.getMusicHandler(guild_id)
      await musicHandler.setStopFlag(False)

      if not await musicHandler.isValidUrl(url):
         await interaction.followup.send(content="Incorrect video link", ephemeral=True)
         return
      
      try:
         track = await musicHandler.extractInfo(url)
      except Exception as e:
         await interaction.followup.send(content=f"Error: {e}")
         return
      
      await musicHandler.addTrack(track)

      minutes = track.getDuration() // 60
      seconds = track.getDuration() % 60
      
      response = f"**Title:** {track.getTitle()}\n**Artist:** {track.getAuthor()}\n**Duration:** {minutes}:{seconds:02d}\n**Queue positions:** {await musicHandler.sizeQueue()}"

      await interaction.followup.send(content=response, ephemeral=False)

      if interaction.guild.voice_client:
         voice = interaction.guild.voice_client
      else:
         voice = await interaction.user.voice.channel.connect()

      if voice.is_playing():
         return
      
      await musicHandler.player(voice=voice)

async def setup(bot):
   await bot.add_cog(PlayCommand(bot))