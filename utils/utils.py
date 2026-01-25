from handler.track import Track
import re
import yt_dlp
import discord
from handler.config import YDL_OPTIONS, YDL_OPTIONS_FROM_TITLE

def createEmbed(track: Track) -> discord.Embed:
   # Format the duration nicely (HH:MM:SS) for the embed message
   duration_str = __formatDuration(track.getDuration())

   # Create a rich embed message to confirm the track was added
   embed = discord.Embed(
      title=track.getTitle(),
      url=track.getUrl(),
      color=0x5865F2
   )
   embed.add_field(name="Author", value=track.getAuthor() or "Unknown", inline=True)
   embed.add_field(name="Duration", value=duration_str or "-", inline=True)
   

   if track.getThumbnail():
      embed.set_thumbnail(url=track.getThumbnail())

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
   
async def updateWorkingStreamLink(track: Track):
   """
   (Placeholder) Updates the stream URL for a given track if it has expired.
   """
   return

async def __updateInfo(track: Track):
   """
   (Internal Placeholder) Intended for updating track info if needed.
   """
   return

async def extractInfoByUrl(url: str) -> Track:
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
      track.setTitle(info.get("title", "Unknown track"))         
      track.setAuthor(info.get("uploader", "Unknown author"))
      track.setDuration(int(info.get("duration", 0)))
      track.setStreamUrl(info.get("url", ""))
      track.setThumbnail(info.get("thumbnail"))
      # Constructs the full display URL from the base URL and video ID
      track.setUrl(track.getBeginUrl() + info.get("id", "")) 
      return track