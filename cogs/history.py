import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler
from utils.utils import formatDuration

class HistoryCommand(commands.Cog):
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="history", description="Shows the current history.")
   async def history(self, interaction: discord.Interaction):
      guild_id = interaction.guild.id
      
      # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "common.not_in_voice"), 
            ephemeral=True
         )
         return
      
      await interaction.response.defer()

      # Get the specific MusicHandler instance associated with this server (guild)
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)

      current_track = musicHandler.get_current_track()
      history_list = musicHandler.get_history()

      # Creating an embed with a localized title
      embed = discord.Embed(
         title=self.bot.locale_manager.get_text(guild_id, "queue.title_history"), 
         color=0x5865F2
      )

      # Description with current track
      if not current_track or current_track.empty:
         embed.description = self.bot.locale_manager.get_text(guild_id, "queue.nothing_playing") + "\n"
      else: 
         embed.description = self.bot.locale_manager.get_text(guild_id, "queue.currently_playing") + f"\n🚀 [{current_track.title}]({current_track.url}) `[{formatDuration(current_track.duration)}]`\n"
         if current_track.thumbnail:
            embed.set_thumbnail(url=current_track.thumbnail)

      # History
      if not history_list:
         embed.add_field(
            name=self.bot.locale_manager.get_text(guild_id, "queue.previous_in_list"),  
            value=self.bot.locale_manager.get_text(guild_id, "queue.history_empty"),  
            inline=False
         )
      else:
         # Total duration of the entire story
         total_seconds = sum(t.duration for t in history_list)
         total_duration_str = formatDuration(total_seconds)

         # We take only the first 10 tracks for display
         display_history = history_list[:10]
         lines = []

         for i, t in enumerate(display_history):
            dur = formatDuration(t.duration)
            title = t.title[:50] + "..." if len(t.title) > 53 else t.title
            lines.append(f"`{i+1}.` [{title}]({t.url}) `[{dur}]`")

         history_str = "\n".join(lines)

         # If there are more than 10 tracks, add a message about hidden
         if len(history_list) > 10:
            count = len(history_list) - 10
            history_str += "\n\n" + self.bot.locale_manager.get_text(
               guild_id, 
               "queue.and_another", 
               count=count, 
               type=self.bot.locale_manager.get_text(
                  guild_id, 
                  "queue.type_history"
               )
            )

         #We form the name of the field with the total duration
         field_name = self.bot.locale_manager.get_text(guild_id, "queue.previous_in_list") + " (" + \
                     self.bot.locale_manager.get_text(guild_id, "queue.total") + f": {total_duration_str})"

         embed.add_field(
            name=field_name,   
            value=history_str, 
            inline=False
         )

      await interaction.followup.send(embed=embed)


# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the HistoryCommand cog with the bot.
   """
   await bot.add_cog(HistoryCommand(bot))