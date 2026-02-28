import discord
from discord.ext import commands
from discord import app_commands

class JoinCommand(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @app_commands.command(name="join", description="The bot will join your voice channel.")
   async def join(self, interaction: discord.Interaction):
      try:
         guild_id = interaction.guild.id
         if not interaction.user.voice:
            await interaction.response.send_message(
               content=self.bot.locale_manager.get_text(guild_id, "common.not_in_voice"), 
               ephemeral=True
            )
            return

         channel = interaction.user.voice.channel
         voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

         if voice_client:
            # If the bot is already in the same channel, send a message and return
            if voice_client.channel == channel:
               await interaction.response.send_message(
                  content=self.bot.locale_manager.get_text(guild_id, "join.already_in_channel", channel=str(channel.name)), 
                  ephemeral=True
               )
            # If the bot is in a different channel, move to the user's channel
            else:
               await interaction.response.send_message(
                  content=self.bot.locale_manager.get_text(guild_id, "join.cannot_join"), 
                  ephemeral=True
               )
         else:
            # If the bot is not connected at all, connect to the user's channel
            await channel.connect()
            await interaction.response.send_message(
               content=self.bot.locale_manager.get_text(guild_id, "join.joined", channel=str(channel.name)), 
               ephemeral=True
            )
      except Exception as e:
         print(f"Error: {e}")


async def setup(bot):
   await bot.add_cog(JoinCommand(bot))