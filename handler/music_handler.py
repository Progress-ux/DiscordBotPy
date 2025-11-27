from collections import deque
from .track import Track
from .config import YDL_OPTIONS, FFMPEG_OPTIONS
import re
import yt_dlp
import asyncio
import discord

class MusicHandler:
   """
   Handles music playback logic, queue management, history tracking, and YouTube info extraction
   for a Discord bot.
   """
   def __init__(self, bot):
      """
      Initializes the MusicHandler with empty queue/history and control flags set to False.
      """
      self.__current_track = Track()
      self.__queue = deque()
      self.__history = deque()

      # Control flags for stop, skip, and back actions
      self.__stopFlag = False
      self.__skipFlag = False
      self.__backFlag = False

      self.__bot = bot
   def setBackFlag(self, flag: bool):
      """
      Sets the flag to signal the player to go back to the previous track.

      Args:
         flag: The boolean value to set the flag to (usually True).
      """
      self.__backFlag = flag

   def isBackFlag(self) -> bool:
      """
      Checks if the back flag is currently set.

      Returns:
         True if the back flag is set, False otherwise.
      """
      return self.__backFlag
   
   def setSkipFlag(self, flag: bool):
      """
      Sets the flag to signal the player to skip to the next track.

      Args:
         flag: The boolean value to set the flag to (usually True).
      """
      self.__skipFlag = flag

   def isSkipFlag(self) -> bool:
      """
      Checks if the skip flag is currently set.

      Returns:
         True if the skip flag is set, False otherwise.
      """
      return self.__skipFlag
   
   async def setStopFlag(self, flag: bool):
      """
      Sets the flag to signal the player to stop all playback.

      Args:
         flag: The boolean value to set the flag to (usually True).
      """
      self.__stopFlag = flag

   def isStopFlag(self) -> bool:
      """
      Checks if the stop flag is currently set.

      Returns:
         True if the stop flag is set, False otherwise.
      """
      return self.__stopFlag

   async def addTrack(self, track: Track):
      """
      Adds a new track to the end of the playback queue.

      Args:
         track: The Track object to add.
      """
      self.__queue.append(track)

   def isQueueEmpty(self) -> bool:
      """
      Checks if the main playback queue is empty.

      Returns:
         True if the queue has no tracks, False otherwise.
      """
      return len(self.__queue) == 0
   
   def isHistoryEmpty(self) -> bool:
      """
      Checks if the playback history is empty.

      Returns:
         True if the history has no tracks, False otherwise.
      """
      return len(self.__history) == 0
   
   def sizeQueue(self) -> int:
      """
      Returns the number of tracks currently in the queue.
      """
      return len(self.__queue)

   def sizeHistory(self) -> int:
      """
      Returns the number of tracks currently in the history.
      """
      return len(self.__history)
   
   async def getCurrentTrack(self) -> Track:
      """
      Retrieves the current track. 
      If the current track is empty, attempts to get the next track from the queue.

      Returns:
         The current Track object or None if the queue is empty.
      """
      if self.__current_track.empty():
         self.__current_track = await self.getNextTrack()
      return self.__current_track

   async def getNextTrack(self) -> Track | None:
      """
      Moves the current track to history and selects the next track from the queue.

      Returns:
         The next Track object from the queue, or None if the queue is empty.
      """
      if not self.__queue:
         self.__current_track = None
         return None
      
      # Move the current track to history before updating
      if self.__current_track is not None:
         self.__history.append(self.__current_track)

      self.__current_track = self.__queue.popleft()
      return self.__current_track
   
   async def getBackTrack(self) -> Track | None:
      """
      Moves the current track back to the queue and selects the previous track from history.

      Returns:
         The previous Track object from history, or None if history is empty.
      """
      if not self.__history:
         self.__current_track = None
         return None
      
      # Move the current track back to the front of the queue
      if self.__current_track is not None:
         self.__queue.append(self.__current_track)

      self.__current_track = self.__history.pop()
      return self.__current_track
   
   async def isValidUrl(self, url: str) -> bool:
      """
      Validates if the provided string is a valid URL using a basic regex pattern.

      Args:
         url: The string to validate.

      Returns:
         True if the string matches the URL pattern, False otherwise.
      """
      return bool(re.compile(r"^https://[^\s]+$").match(url))
   
   async def updateWorkingStreamLink(self, track: Track):
      """
      (Placeholder) Updates the stream URL for a given track if it has expired.
      """
      return

   async def __updateInfo(self, track: Track):
      """
      (Internal Placeholder) Intended for updating track info if needed.
      """
      return

   async def extractInfo(self, url: str) -> Track:
      """ 
      Extracts detailed information (title, author, duration, stream_url, etc.) 
      from a given URL using yt-dlp without downloading the file.

      Args:
         url: The link to the video/stream.
         
      Raises:
         Exception: If yt-dlp returns an empty information dictionary.

      Returns:
         A populated Track object with all relevant metadata.
      """
      with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
         info = ydl.extract_info(url, download=False)
         
         if not info:
            raise Exception("yt-dlp returned empty info dictionary")

         track = Track()
         track.setTitle(info.get("title", "Unknown track"))         
         track.setAuthor(info.get("uploader", "Unknown author"))
         track.setDuration(int(info.get("duration", 0)))
         track.setStreamUrl(info.get("url", ""))
         track.setThumbnail(info.get("thumbnail"))
         # Constructs the full display URL from the base URL and video ID
         track.setUrl(track.getBeginUrl() + info.get("id", "")) 
         return track

   async def player(self, voice: discord.VoiceProtocol):
      """
      Main playback control loop.

      Manages the state machine for playing, skipping, and going back based on internal flags
      and queue status. It calls the `__play` method internally to stream audio.

      Args:
         voice: The Discord voice client needed to pass to `__play` for audio transmission.
      """
      if self.__backFlag:
         self.__backFlag = False

         if self.isHistoryEmpty():
            return # Stop playback if no history available

         await self.updateWorkingStreamLink(await self.getBackTrack())
      else:
         self.__skipFlag = False

         if self.isQueueEmpty():
            return # Stop playback if nothing new to play

         await self.updateWorkingStreamLink(await self.getNextTrack())

      # Get the current track and start playback
      await self.__play(track=await self.getCurrentTrack(), voice=voice)


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
         source = discord.FFmpegPCMAudio(track.getStreamUrl(), **FFMPEG_OPTIONS)
         voice.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
            self.player(voice), self.__bot.loop # Callback to advance the player state
         ) if voice and voice.is_connected() and not self.__stopFlag else None)
      except Exception as e:
         print(f"Error during audio playback: {e}")

