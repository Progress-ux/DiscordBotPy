import discord
from discord.ext import commands
from discord import app_commands
from handler.music_handler import MusicHandler
from utils.utils import formatDuration

class QueueCommand(commands.Cog):
   def __init__(self, bot):
      """
      Initializes the cog with the bot instance.
      """
      self.bot = bot

   @app_commands.command(name="queue", description="Shows the current queue.")
   async def queue(self, interaction: discord.Interaction):
      guild_id = interaction.guild.id

      # Ensure the user is in a voice channel before proceeding
      if not interaction.user.voice:
         await interaction.response.send_message(
            content=self.bot.locale_manager.get_text(guild_id, "common.not_in_voice"), 
            ephemeral=True # Only the user sees this message
         )
         return
      
      await interaction.response.defer()

      # Get the specific MusicHandler instance associated with this server (guild)
      musicHandler: MusicHandler = await self.bot.getMusicHandler(guild_id)

      current_track = musicHandler.get_current_track()
      queue_list = musicHandler.get_queue()

      embed = discord.Embed(
         title=self.bot.locale_manager.get_text(guild_id, "queue.title_queue"), 
         color=0x5865F2
      )

      if not current_track or current_track.empty:
         embed.description = self.bot.locale_manager.get_text(guild_id, "queue.nothing_playing") + "\n", 
      else: 
         embed.description = self.bot.locale_manager.get_text(guild_id, "queue.currently_playing") + f"\n🚀 [{current_track.title}]({current_track.url}) `[{formatDuration(current_track.duration)}]`\n"
         if current_track.thumbnail:
            embed.set_thumbnail(url=current_track.thumbnail)

      if not queue_list:
         embed.add_field(
            name=self.bot.locale_manager.get_text(guild_id, "queue.next_in_list"),  
            value=self.bot.locale_manager.get_text(guild_id, "queue.queue_empty"),  
            inline=False
         )
      else:
         total_seconds = sum(t.duration for t in queue_list)
         total_duration_str = formatDuration(total_seconds)

         display_queue = queue_list[:10]
         lines = []

         for i, t in enumerate(display_queue):
            dur = formatDuration(t.duration)
            title = t.title[:50] + "..." if len(t.title) > 53 else t.title
            lines.append(f"`{i+1}.` [{title}]({t.url}) `[{dur}]`")

         queue_str = "\n".join(lines)

         if len(queue_list) > 10:
            count = len(queue_list) - 10
            queue_str += "\n\n" + self.bot.locale_manager.get_text(
               guild_id, 
               "queue.and_another", 
               count=count, 
               type=self.bot.locale_manager.get_text(
                  guild_id, 
                  "queue.type_queue"
               )
            )


         embed.add_field(
            name=self.bot.locale_manager.get_text(guild_id, "queue.next_in_list") + "(" + 
            self.bot.locale_manager.get_text(guild_id, "queue.total") + f": {total_duration_str})",   
            value=queue_str, 
            inline=False
         )

         await interaction.followup.send(embed=embed)
      
     

# Required setup function for Discord Cogs
async def setup(bot):
   """
   Registers the QueueCommand cog with the bot.
   """
   await bot.add_cog(QueueCommand(bot))
