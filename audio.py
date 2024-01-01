import mafic
from collections import deque
from typing import TYPE_CHECKING
from disnake.ext import commands

from disnake.abc import Connectable

class TrackOutOfBounds(mafic.PlayerException):
    """
    Raise when track is not in queue
    """


class MaomaoPlayer(mafic.Player[commands.AutoShardedBot]):
    """
    This is a custom implementation of mafic.Player class. It includes the queue system for tracks and various other methods are implemented here.
    """
    def __init__(self, client: commands.AutoShardedBot, channel: Connectable) -> None:
        self._queue = deque()

        super().__init__(client, channel)
    
    def get_track_position(self, track: mafic.Track) -> mafic.Track | None:
        """
        Get the position of the track in queue
        """
        try:
            track_ids = [t.id for t in self._queue]
            return track_ids.index(track.id)
        except:
            return None 
    
    def get_track(self, position: int) -> mafic.Track | None:
        """
        Get track from position
        """
        try:
            return self._queue[position]
        except IndexError:
            return None 


    async def append_track(self, track: mafic.Track) -> None:
        """
        Append a track to queue/play the track.
        """
        if not self._queue:
            await self.play(track)
        self._queue.append(track)

    @property
    def queue(self):
        return self._queue