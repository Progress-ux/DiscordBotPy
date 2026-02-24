from collections import deque

from handler.track import Track

class QueueManager:

   def __init__(self):
      self.__current_track = Track()
      self.__queue = deque()
      self.__history = deque()

   def add_track(self, track: Track) -> None:
      """
      Adds a new track to the end of the playback queue.

      Args:
         track: The Track object to add.
      """
      self.__queue.append(track)

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
   
   @current_track.setter
   def current_track(self, track: Track):
      self.__current_track = track

   def next_track(self) -> Track | None:
      """
      Moves the current track to history and selects the next track from the queue.

      Returns:
         The next Track object from the queue, or None if the queue is empty.
      """
      if not self.__queue:
         self.__current_track = None
         return None
      
      # Move the current track to history before updating
      if not self.__current_track.empty:
         self.__history.append(self.__current_track)

      self.__current_track = self.__queue.popleft()
      return self.__current_track
   
   def back_track(self) -> Track | None:
      """
      Moves the current track back to the queue and selects the previous track from history.

      Returns:
         The previous Track object from history, or None if history is empty.
      """
      if not self.__history:
         self.__current_track = None
         return None
      
      # Move the current track back to the front of the queue
      if not self.__current_track.empty:
         self.__queue.append(self.__current_track)

      self.__current_track = self.__history.pop()
      return self.__current_track
   
   def clear_current(self) -> None:
      if self.__current_track and not self.__current_track.empty:
         self.__history.append(self.__current_track)
         self.__current_track = Track()