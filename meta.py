from dataclasses import dataclass
from typing import Dict
from mafic import Track

from uuid import uuid4, UUID

from disnake import User, Member
@dataclass
class Metadata:
    """
    Additional information related to a track

    Fields
    ---------------------
    channel_id: int - The channel where the command was executed.
    requester: int - The user who requested the track
    """
    channel_id: int 
    requester: User | Member
    track: Track
    meta_id: UUID = uuid4()

class MetaDep:
    """
    Keep record of all the metadata for the tracks
    """
    def __init__(self) -> None:
        self.metalist: Dict[str, Metadata] = {}
    
    def append_meta(self, metadata: Metadata) -> None:
        self.metalist[metadata.meta_id] = metadata

    def remove_meta(self, meta_id: str) -> None:
        self.metalist.pop(meta_id)

    def get_by_id(self, meta_id: str) -> Metadata | None:
        """
        Get metadata by it's meta ID. Returns `None` if not found.
        """
        metadata = self.metalist.get(meta_id)
        return metadata
    
    def get(self, track: Track) -> Metadata | None:
        """
        Get metadata by it's track. Returns `None` if not found.
        """
        for meta_id in self.metalist:
            metadata = self.get_by_id(meta_id)
            if metadata.track.id == track.id:
                return metadata
            continue 
        return None 
        