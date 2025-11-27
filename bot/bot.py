from dotenv import dotenv_values
import discord
from discord.ext import commands
import os
from handler.music_handler import MusicHandler 

class Bot(commands.Bot):
   def __init__(self):
      super().__init__(command_prefix="!", intents=discord.Intents.all())
      self.__musicHandlers = {}

      token = self.load_token()
      if token == "":
         print("Invalid token")
         return
      self.__TOKEN = token

   async def getMusicHandler(self, guild_id):
      if guild_id not in self.__musicHandlers:
         self.__musicHandlers[guild_id] = MusicHandler()
         print(f"Created MusicHandler for server: {guild_id}")
      
      return self.__musicHandlers[guild_id]

   async def on_voice_state_update(self, member, before, after):
      if member == self.user:
         if before.channel and not after.channel:
            await self.__musicHandlers[member.guild.id].setStopFlag(True)
         elif not before.channel and after.channel:
            await self.__musicHandlers[member.guild.id].setStopFlag(True)

   async def on_ready(self):
      print(f'Бот вошел в систему как {self.user.name}')
      try:
         # Синхронизируем глобальные команды
         synced = await self.tree.sync()
         print(f"Синхронизировано {len(synced)} слеш-команд(ы).")
      except Exception as e:
         print(e)

   async def load(self):
      for filename in os.listdir("./cogs"):
         if filename.endswith(".py"):
            await self.load_extension(f"cogs.{filename[:-3]}")

   def load_token(self):
      config = dotenv_values("./.env")
      return config.get("TOKEN", "")

   async def run(self):
      async with self:
         await self.load()
         await self.start(self.__TOKEN)
      