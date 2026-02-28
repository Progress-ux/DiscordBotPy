from collections import deque
from .track import Track
from .config import FFMPEG_OPTIONS
from .queue_manager import QueueManager, RepeatMode
from utils.utils import updateWorkingStreamLink
import asyncio
import discord

class MusicHandler:
   """
   Handles music playback logic, queue management, history tracking, and YouTube info extraction
   for a Discord bot.
   """
   def __init__(self, bot):
      """
      Initializes the MusicHandler with empty queue_manager and control flags set to False.
      """
      self.__queue_manager = QueueManager()
      self.__is_playing: bool = False

      # Control flags for stop, skip, and back actions
      self.__stop_flag: bool = False
      self.__skip_flag: bool = False
      self.__back_flag: bool = False

      self.__bot = bot

   def get_current_track(self) -> Track | None:
      return self.__queue_manager.get_current_track_for_embed()
   
   def get_queue(self) -> list:
      return self.__queue_manager.queue

   def add_track(self, track: Track) -> None:
      """
      Adds a new track to the end of the playback queue.

      Args:
         track: The Track object to add.
      """
      self.__queue_manager.add_track(track)

   def toggle_repeat_mode(self, target_mode: RepeatMode) -> RepeatMode:
      current = self.__queue_manager.repeat_mode

      if current == target_mode:
         self.__queue_manager.repeat_mode = RepeatMode.NONE
      else:
         self.__queue_manager.repeat_mode = target_mode

      return self.__queue_manager.repeat_mode

   @property
   def queue_empty(self) -> bool:
      return self.__queue_manager.queue_empty
   
   @property
   def history_empty(self) -> bool:
      return self.__queue_manager.history_empty

   @property
   def is_playing(self) -> bool:
      return self.__is_playing

   @property
   def back_flag(self) -> bool:
      return self.__back_flag
   
   @back_flag.setter
   def back_flag(self, flag: bool):
      self.__back_flag = flag
   
   @property
   def skip_flag(self) -> bool:
      return self.__skip_flag
   
   @skip_flag.setter
   def skip_flag(self, flag: bool):
      self.__skip_flag = flag

   @property
   def stop_flag(self) -> bool:
      return self.__stop_flag

   @stop_flag.setter
   def stop_flag(self, flag: bool):
     self.__stop_flag = flag

   async def player(self, voice: discord.VoiceProtocol):
      """
      Main playback control loop.

      Manages the state machine for playing, skipping, and going back based on internal flags
      and queue status. It calls the `__play` method internally to stream audio.

      Args:
         voice: The Discord voice client needed to pass to `__play` for audio transmission.
      """
      self.__is_playing = True

      if self.__stop_flag:
         self.__stop_flag = False
         self.__is_playing = False
         self.__queue_manager.clear_current()
         return
      
      track = None

      if self.__skip_flag:
         self.__skip_flag = False
         track = self.__queue_manager.next_track(force_skip=True)

      elif self.__back_flag:
         self.__back_flag = False
         track = self.__queue_manager.back_track()

      else:
         track = self.__queue_manager.next_track()

      if not track or track.empty:
         self.__is_playing = False
         return

      try:
         self.__queue_manager.current_track = await updateWorkingStreamLink(track)
         # Get the current track and start playback
         await self.__play(track=self.__queue_manager.current_track, voice=voice)
      except Exception as e:
         print(f"Error updating track: {e}")


   async def __play(self, track: Track, voice: discord.VoiceProtocol):
      """
      Internal helper method to initiate audio playback in a Discord voice channel.

      Uses FFMPEG to stream the audio source. Sets up a lambda callback function to automatically
      call `player()` again once the current track finishes, unless the stop flag is set.

      Args:
         track: The current track object to retrieve the stream_url from.
         voice: The Discord voice channel object for sending audio.
      """
      
      try:
         source = discord.FFmpegPCMAudio(track.stream_url, **FFMPEG_OPTIONS)
         voice.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
            self.player(voice), self.__bot.loop
         ))
      except Exception as e:
         print(f"Error during audio playback: {e}")