from collections import deque
from handler.track import Track
from enum import Enum, auto

class RepeatMode(Enum):
   NONE = auto()
   ONE = auto()
   ALL = auto()

   @property
   def status_message(self) -> str:
      messages = {
         RepeatMode.NONE: "repeat.repeat_disabled",
         RepeatMode.ONE: "repeat.one_enabled",
         RepeatMode.ALL: "repeat.all_enabled"
      }
      return messages[self]

class QueueManager:

   def __init__(self):
      self.__current_track = Track()
      self.__queue = deque()
      self.__history = deque()
      self.__repeat_mode = RepeatMode.NONE

   def add_track(self, track: Track) -> None:
      """
      Adds a new track to the end of the playback queue.

      Args:
         track: The Track object to add.
      """
      self.__queue.append(track)

   @property
   def repeat_mode(self) -> RepeatMode:
      return self.__repeat_mode
   
   @repeat_mode.setter
   def repeat_mode(self, mode: RepeatMode):
      self.__repeat_mode = mode

   @property
   def queue_empty(self) -> bool:
      return len(self.__queue) == 0
   
   @property
   def history_empty(self) -> bool:
      return len(self.__history) == 0
   
   @property
   def queue_size(self) -> int:
      return len(self.__queue)

   @property
   def history_size(self) -> int:
      return len(self.__history)
   
   @property
   def current_track(self) -> Track:
      """
      Retrieves the current track. 
      If the current track is empty, attempts to get the next track from the queue.

      Returns:
         The current Track object or None if the queue is empty.
      """
      if self.__current_track.empty:
         self.__current_track = self.next_track()
      return self.__current_track
   
   def get_current_track_for_embed(self) -> Track | None:
      return self.__current_track
   
   @current_track.setter
   def current_track(self, track: Track):
      self.__current_track = track

   @property
   def queue(self) -> list:
      return list(self.__queue)
   
   @property
   def history(self) -> list:
      return list(self.__history)

   def clear_current(self):
      if not self.__current_track.empty:
         self.__history.append(self.__current_track)
      self.__current_track = Track()

   def next_track(self, force_skip: bool = False) -> Track | None:
      """
      Moves the current track to history and selects the next track from the queue.

      Returns:
         The next Track object from the queue, or None if the queue is empty.
      """
      if self.__repeat_mode == RepeatMode.ONE and not self.__current_track.empty and not force_skip:
         return self.__current_track
      
      if not self.__current_track.empty:
         if self.__repeat_mode == RepeatMode.ALL:
            self.__queue.append(self.__current_track)
         else:
            self.__history.append(self.__current_track)
      
      if not self.__queue:
         self.__current_track = Track()
         return None
      
      self.__current_track = self.__queue.popleft()
      return self.__current_track
   
   def back_track(self) -> Track | None:
      """
      Moves the current track back to the queue and selects the previous track from history.

      Returns:
         The previous Track object from history, or None if history is empty.
      """
      if not self.__history:
         self.__current_track = Track()
         return None
      
      # Move the current track back to the front of the queue
      if not self.__current_track.empty:
         self.__queue.append(self.__current_track)
      
      self.__current_track = self.__history.pop()
      return self.__current_track
   
