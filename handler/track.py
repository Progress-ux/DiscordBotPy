class Track:
   def __init__(self, title="", author="", url="", duration=0, thumbnail=None):
      self.title = title
      self.author = author
      self.url = url
      self.duration = duration
      self.thumbnail = thumbnail
      self.__stream_url = ""
      self.__BEGIN_URL = "https://youtu.be/"
   
   @property
   def stream_url(self) -> str:
      return self.__stream_url
   
   @stream_url.setter
   def stream_url(self, value: str) -> None:
      if not value.startswith("http"):
         raise ValueError("Invalid stream url")
      self.__stream_url = value

   @property
   def begin_url(self) -> str:
      return self.__BEGIN_URL
   
   @property
   def empty(self) -> bool:
      return self.__stream_url == ""
   