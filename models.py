from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Spotify_Object:
    id: str

    def __eq__(s, o):
        return s.id == o.id


@dataclass
class Playlist(Spotify_Object):
    name: str
    description: str
    snapshot_id: str
    owner_display_name: str
    owner_uri: str


@dataclass
class Artist(Spotify_Object):
    name: str
    popularity: int
    genres: List[str]
    followers: int


@dataclass
class Album(Spotify_Object):
    name: str
    type: str
    popularity: str
    release_data: str
    added_date: str
    upc: Optional[str]
    artists: List[str]
    total_tracks: int
    tracks: List[str]


@dataclass
class Track(Spotify_Object):
    name: str
    popularity: int
    release_date: str
    added_date: str
    isrc: str
    artists: List[str]
    albums: List[str]
