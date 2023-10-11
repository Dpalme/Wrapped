from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Spotify_Object:
    id: str

    def __eq__(s, o):
        return s.id == o.id


@dataclass
class Response:
    items: List[Spotify_Object]
    total: int


@dataclass
class User(Spotify_Object):
    display_name: str
    uri: str


@dataclass
class _Track(Spotify_Object):
    pass

@dataclass
class _Album(Spotify_Object):
    pass

@dataclass
class _Artist(Spotify_Object):
    pass


@dataclass
class _Album(Spotify_Object):
    pass

@dataclass
class Playlist(Spotify_Object):
    name: str
    description: str
    snapshot_id: str
    owner: User
    collaborative: bool
    external_urls: dict
    href: str
    images: list
    name: str
    owner: dict
    primary_color: str
    public: bool
    tracks: dict
    type: str
    uri: str



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
    popularity: int
    release_date: str
    artists: List[Artist]
    total_tracks: int
    tracks: List[_Track]
    album_type: str
    available_markets: list[str]
    copyrights: list[dict]
    external_ids: dict
    external_urls: dict
    genres: list[str]
    href: str
    images: list[dict]
    label: str
    release_date_precision: str
    total_tracks: int
    tracks: dict
    type: str
    uri: str
    added_date: str = None
    upc: Optional[str] = None


@dataclass
class Track(Spotify_Object):
    name: str
    popularity: int
    release_date: str
    added_date: str
    isrc: str
    artists: List[Artist]
    albums: List[Album]


@dataclass
class Genre:
    name: str
    tracks: List[Track]

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class Database:
    tracks: List[Track]
    albums: List[Album]
    playlists: List[Playlist]
    artists: List[Artist]
    genres: List[Genre]
