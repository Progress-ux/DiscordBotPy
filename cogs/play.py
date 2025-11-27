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

      
      embed = discord.Embed(
         title=track.getTitle(),
         url=track.getUrl(),
         color=0x5865F2
      )
      embed.add_field(name="Author", value=track.getAuthor() or "Unknow", inline=True)
      embed.add_field(name="Duration", value=duration_str or "-", inline=True)
      embed.add_field(name="Added", value=f"<@{interaction.user.id}>", inline=False)

      if track.getThumbnail():
         embed.set_thumbnail(url=track.getThumbnail())

      await interaction.followup.send(embed=embed)

      if interaction.guild.voice_client:
         voice = interaction.guild.voice_client
      else:
         voice = await interaction.user.voice.channel.connect()

      if voice.is_playing():
         return
      
      await musicHandler.player(voice=voice)

async def setup(bot):
   await bot.add_cog(PlayCommand(bot))