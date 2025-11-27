class Track:
   def __init__(self):
      self.__title = ""
      self.__author = ""
      self.__url = ""
      self.__stream_url = ""
      self.__duration = 0
      self.__thumbnail = None
      self.__BEGIN_URL = "https://youtu.be/"
   
   def setTitle(self, _title: str):
      self.__title = _title

   def getTitle(self):
      return self.__title

   def setAuthor(self, _author: str):
      self.__author = _author

   def getAuthor(self):
      return self.__author
   
   def setUrl(self, _url: str):
      self.__url = _url

   def getUrl(self):
      return self.__url
   
   def setStreamUrl(self, _stream_url: str):
      self.__stream_url = _stream_url

   def getStreamUrl(self):
      return self.__stream_url
   
   def setDuration(self, _duration: int):
      self.__duration = _duration

   def getDuration(self):
      return self.__duration

   def setThumbnail(self, _thumbnail):
      self.__thumbnail = _thumbnail

   def getThumbnail(self):
      return self.__thumbnail

   def getBeginUrl(self):
      return self.__BEGIN_URL
   
   def empty(self):
      return self.__stream_url == ""
   