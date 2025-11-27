from collections import deque
from .track import Track
from .config import YDL_OPTIONS, FFMPEG_OPTIONS
import re
import yt_dlp
import asyncio
import discord

class MusicHandler:
   def __init__(self):
      self.__current_track = Track()
      self.__queue = deque()
      self.__history = deque()

      self.__stopFlag = False
      self.__skipFlag = False
      self.__backFlag = False

   def setBackFlag(self, flag: bool):
      self.__backFlag = flag

   def isBackFlag(self):
      return self.__backFlag
   
   def setSkipFlag(self, flag: bool):
      self.__skipFlag = flag

   def isSkipFlag(self):
      return self.__skipFlag
   
   async def setStopFlag(self, flag: bool):
      self.__stopFlag = flag

   def isStopFlag(self):
      return self.__stopFlag

   async def addTrack(self, track: Track):
      self.__queue.append(track)

   def isQueueEmpty(self):
      return len(self.__queue) == 0
   
   def isHistoryEmpty(self):
      return len(self.__history) == 0
   
   def sizeQueue(self):
      return len(self.__queue)

   def sizeHistory(self):
      return len(self.__history)
   
   async def getCurrentTrack(self):
      if self.__current_track.empty():
         self.__current_track = await self.getNextTrack()
      return self.__current_track

   async def getNextTrack(self):
      if not self.__queue:
         self.__current_track = None
         return None
      
      if self.__current_track is not None:
         self.__history.append(self.__current_track)

      self.__current_track = self.__queue.popleft()
      return self.__current_track
   
   async def getBackTrack(self):
      if not self.__history:
         self.__current_track = None
         return None
      
      if self.__current_track is not None:
         self.__queue.append(self.__current_track)

      self.__current_track = self.__history.pop()
      return self.__current_track
   
   async def isValidUrl(self, url: str):
      return bool(re.compile(r"^https://[^\s]+$").match(url))
   
   async def updateWorkingStreamLink(self, track: Track):
      pass

   async def __updateInfo(self, track: Track):
      pass

   async def extractInfo(self, url: str):
      with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
         info = ydl.extract_info(url, download=False)
         
         if not info:
            raise "json empty"

         track = Track()
         track.setTitle(info.get("title", "Unknown track"))         
         track.setAuthor(info.get("uploader", "Unknown author"))
         track.setDuration(int(info.get("duration", 0)))
         track.setStreamUrl(info.get("url", ""))
         track.setUrl(track.getBeginUrl() + info.get("id", ""))
         return track

   async def player(self, voice):
      if self.__backFlag:
         self.__backFlag = False

         if self.isHistoryEmpty():
            return

         await self.updateWorkingStreamLink(await self.getBackTrack())


      if self.__skipFlag:
         self.__skipFlag = False
         if await self.isQueueEmpty():
            return

         await self.updateWorkingStreamLink(await self.getNextTrack())

      await self.__playTrack(track=await self.getCurrentTrack(), voice=voice)


   async def __playTrack(self, track: Track, voice):
      try:
         source = discord.FFmpegPCMAudio(track.getStreamUrl(), **FFMPEG_OPTIONS)
         voice.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
            self.player(voice), self.bot.loop
         ) if voice and voice.is_connected() and not self.__stopFlag else None)
      except Exception as e:
         print(f"Error: {e}")