from dotenv import dotenv_values
import discord
from discord.ext import commands
import os
from handler.music_handler import MusicHandler 
from cogs.locales.locale_manager import LocaleManager

class Bot(commands.Bot):
   """
   Custom implementation of a Discord bot using discord.py library.
   Manages the bot's lifecycle, configuration, cogs loading, and per-guild music handlers.
   """
   def __init__(self):
      """
      Initializes the bot, sets intents, loads configuration from .env, and validates the token.
      """
      # Initialize the commands.Bot parent class with a prefix and all intents
      super().__init__(command_prefix="!", intents=discord.Intents.all())
      
      # Dictionary to store a dedicated MusicHandler instance for each Discord server (guild)
      self.__musicHandlers = {}

      # Initialize local manager
      self.locale_manager = LocaleManager(self)

      # Load the bot token securely from the environment file
      token = self.load_token()
      if token == "":
         print("Invalid token specified in .env file.")
         return
      self.__TOKEN = token

   async def getMusicHandler(self, guild_id: int) -> MusicHandler:
      """
      Retrieves the MusicHandler instance for a specific guild ID.
      Creates a new handler if one does not already exist for that guild.

      Args:
         guild_id: The unique ID of the Discord server (guild).

      Returns:
         The MusicHandler instance for the specified guild.
      """
      if guild_id not in self.__musicHandlers:
         self.__musicHandlers[guild_id] = MusicHandler(self)
         print(f"Created MusicHandler for server: {guild_id}")
      
      return self.__musicHandlers[guild_id]

   async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
      """
      Event handler triggered when a user's voice state changes (e.g., joins/leaves/moves channel).

      Used here to detect if the bot itself (self.user) is disconnected from a voice channel 
      by a user action (e.g. kicked, or channel emptied), and sets the stop flag.
      """
      # Check if the update event is about the bot itself
      if member == self.user:
         guild_id = member.guild.id
         
         # Case 1: Bot was in a channel (before) and is no longer (after is None)
         if before.channel and not after.channel:
            if guild_id in self.__musicHandlers:
               await self.__musicHandlers[guild_id].setStopFlag(True)
         
         # Case 2: Bot joins a new channel (this case seems redundant with Case 1 logic but included as in original)
         # Note: The original logic here also sets the stop flag when *joining* a channel, which may be unintentional. 
         # A typical implementation only stops when leaving/disconnecting.
         elif not before.channel and after.channel:
             if guild_id in self.__musicHandlers:
               await self.__musicHandlers[guild_id].setStopFlag(True)


   async def on_ready(self):
      """
      Event handler called when the bot successfully connects to Discord.
      Used to print connection status and synchronize application (slash) commands.
      """
      print(f'Бот вошел в систему как {self.user.name}')
      try:
         # Synchronize slash commands globally with Discord's API
         synced = await self.tree.sync()
         print(f"Синхронизировано {len(synced)} слеш-команд(ы).")
      except Exception as e:
         print(f"Failed to sync slash commands: {e}")

   async def load(self):
      """
      Loads all extension files (cogs) located in the './cogs' directory.
      """
      for filename in os.listdir("./cogs"):
         if filename.endswith(".py"):
            # Constructs the module path, e.g., "cogs.playcommand"
            await self.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename[:-3]}")

   def load_token(self) -> str:
      """
      Reads the 'TOKEN' value from the local .env file using dotenv.

      Returns:
         The bot token string, or an empty string if not found.
      """
      config = dotenv_values("./.env")
      return config.get("TOKEN", "")

   async def run(self):
      """
      The main entry point to start the bot's operation.
      It loads cogs and connects to the Discord API using the stored token.
      """
      # Use an async context manager for proper startup/shutdown
      async with self:
         await self.load() # Load all functionality/commands
         await self.start(self.__TOKEN) # Connect and start the bot loop
