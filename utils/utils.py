from handler.track import Track
import re
import yt_dlp
import discord
from handler.config import YDL_OPTIONS, YDL_OPTIONS_FROM_TITLE
import httpx

def createEmbed(track: Track) -> discord.Embed:
   # Format the duration nicely (HH:MM:SS) for the embed message
   duration_str = __formatDuration(track.duration)

   # Create a rich embed message to confirm the track was added
   embed = discord.Embed(
      title=track.title,
      url=track.url,
      color=0x5865F2
   )
   embed.add_field(name="Author", value=track.author or "Unknown", inline=True)
   embed.add_field(name="Duration", value=duration_str or "-", inline=True)
   

   if track.thumbnail:
      embed.set_thumbnail(url=track.thumbnail)

   return embed

def createQueueEmbed(current_track: Track, queue: list[Track]):
   embed = discord.Embed(title="Queue", color=0x5865F2)

   if not current_track or current_track.empty:
      embed.description = "Nothing is playing now.\n"
   else: 
      embed.description = f"**Currently playing:**\n🚀 [{current_track.title}]({current_track.url}) `[{__formatDuration(current_track.duration)}]`\n"
      if current_track.thumbnail:
         embed.set_thumbnail(url=current_track.thumbnail)

   if not queue:
      embed.add_field(name="Next in the list:", value="Queue is empty", inline=False)
   else:
      total_seconds = sum(t.duration for t in queue)
      total_duration_str = __formatDuration(total_seconds)

      display_queue = queue[:10]
      lines = []

      for i, t in enumerate(display_queue):
         dur = __formatDuration(t.duration)
         title = t.title[:50] + "..." if len(t.title) > 53 else t.title
         lines.append(f"`{i+1}.` [{title}]({t.url}) `[{dur}]`")

      queue_str = "\n".join(lines)

      if len(queue) > 10:
         queue_str += f"\n\n*...and another {len(queue) - 10} tracks in the queue*"

      embed.add_field(
         name=f"Next on the list (Total: {total_duration_str}):", 
         value=queue_str, 
         inline=False
      )

   return embed

def createHistoryEmbed(current_track: Track, history: list[Track]):
   embed = discord.Embed(title="History", color=0x5865F2)

   if not current_track or current_track.empty:
      embed.description = "Nothing is playing now.\n"
   else: 
      embed.description = f"**Currently playing:**\n🚀 [{current_track.title}]({current_track.url}) `[{__formatDuration(current_track.duration)}]`\n"
      if current_track.thumbnail:
         embed.set_thumbnail(url=current_track.thumbnail)

   if not history:
      embed.add_field(name="Previous in the list:", value="History is empty", inline=False)
   else:
      total_seconds = sum(t.duration for t in history)
      total_duration_str = __formatDuration(total_seconds)

      display_queue = history[:10]
      lines = []

      for i, t in enumerate(display_queue):
         dur = __formatDuration(t.duration)
         title = t.title[:50] + "..." if len(t.title) > 53 else t.title
         lines.append(f"`{i+1}.` [{title}]({t.url}) `[{dur}]`")

      queue_str = "\n".join(lines)

      if len(history) > 10:
         queue_str += f"\n\n*...and another {len(history) - 10} tracks in the history*"

      embed.add_field(
         name=f"Previous in the list (Total: {total_duration_str}):", 
         value=queue_str, 
         inline=False
      )

   return embed

def __formatDuration(duration: int) -> str:
   """
   Formats the video duration as: hh:mm:ss or mm:ss if the video is less than an hour
   
   :param duration: video duration
   :type duration: str
   :return: formatted video duration
   :rtype: str
   """
   if duration:
      m, s = divmod(duration, 60)
      h, m = divmod(m, 60)
      if h:
         duration_str = f"{h}:{m:02d}:{s:02d}"
      else:
         duration_str = f"{m}:{s:02d}"
   else:
      duration_str = "-"

   return duration_str

async def isValidUrl(url: str) -> bool:
      """
      Validates if the provided string is a valid URL using a basic regex pattern.

      Args:
         url: The string to validate.

      Returns:
         True if the string matches the URL pattern, False otherwise.
      """
      return bool(re.compile(r"^https://[^\s]+$").match(url))
   
async def updateWorkingStreamLink(track: Track) -> str:
   """
   Проверяет стрим ссылку на работоспособность. Если ссылка недоступна, то обновляет

   Args:
      track: Трек, который нужно обновить

   Returns:
      Если ссылка работоспособна, то она же и вернется, иначе вернется обновленная ссылка
   """
   stream_url = track.stream_url
   is_valid = False
   
   if stream_url:
      try:
         headers = {
            "Range": "bytes=0-0" # Запрашиваем только первый байт
         }
         async with httpx.AsyncClient(follow_redirects=True) as client:
               response = await client.get(stream_url, headers=headers, timeout=5.0)
               # 200 или 206 означают успех
               is_valid = response.status_code in (200, 206)
      except Exception as e:
         print(f"Validation error: {e}")
         is_valid = False

   if not is_valid:
      track.stream_url = await __updateInfo(track.url)
      return track
   
   return track

async def __updateInfo(url: str):
   """
   Retrieves stream link
   
   Args:
      url: The link to the video. 
   
   Raises:
      Exception: If yt-dlp returns an empty information dictionary.

   Returns:
      Link to audio stream
   """
   with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download=False)
      
      if not info:
         raise Exception("yt-dlp returned empty info dictionary")
   
      return info.get("url", "")

async def extractInfoByUrl(url: str) -> Track:
      """ 
      Extracts detailed information (title, author, duration, stream_url, etc.) 
      from a given URL using yt-dlp without downloading the file.

      Args:
         url: The link to the video.
         
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
         track.title = info.get("title", "Unknown track")     
         track.author = info.get("uploader", "Unknown author")
         track.duration = int(info.get("duration", 0))
         track.stream_url = info.get("url", "")
         track.thumbnail = info.get("thumbnail")
         # Constructs the full display URL from the base URL and video ID
         track.url = (track.begin_url + info.get("id", "")) 
         return track
      
async def extractInfoByTitle(title: str) -> Track: 
   """ 
      Retrieves detailed information (title, author, duration, stream_url, etc.) 
      by given name using yt-dlp without downloading the file.

      Args:
         title: Video title.
         
      Raises:
         Exception: If yt-dlp returns an empty information dictionary.

      Returns:
         A populated Track object with all relevant metadata.
      """
   with yt_dlp.YoutubeDL(YDL_OPTIONS_FROM_TITLE) as ydl:
      info = (ydl.extract_info(f"ytsearch:{title}", download=False))['entries'][0]
      
      if not info:
         raise Exception("yt-dlp returned empty info dictionary")
      
      track = Track()
      track.title = info.get("title", "Unknown track")     
      track.author = info.get("uploader", "Unknown author")
      track.duration = int(info.get("duration", 0))
      track.stream_url = info.get("url", "")
      track.thumbnail = info.get("thumbnail")
      # Constructs the full display URL from the base URL and video ID
      track.url = (track.begin_url + info.get("id", "")) 
      return track