import asyncio
from typing import List
import wrapped

__title__ = "rateAlbumizer"
__author__ = "dpalme"
__license__ = "MIT"
__version__ = "1.0"


class RateFMClient:
    def __init__(self, user: str = "dpalme", fm=None) -> None:
        if fm is None:
            raise ValueError("No API Client provided")
        self.user = user
        self.fm = fm

    async def get_albums_to_rate(self, threshold: int = 2):
        """
        Gets user's albums with plays above the threshold in which all tracks
        have at least one play
        """

        async def get_track_user_playcount(track: Track) -> int:
            populated_track = await self.fm.track.get_info(
                track=track.name, artist=track.artist.name, username=self.user
            )
            return populated_track.stats.userplaycount

        async def album_is_played_through(album: Album) -> bool:
            return 0 not in asyncio.gather(
                get_track_user_playcount(track)
                for track in album.get_info(
                    user=self.user, artist=album.artist.name, name=album.name
                )
            )

        async def get_above_threshold() -> List[Album]:
            """
            Get all albums whose user playcount is above the threshold
            """
            total = await self.fm.user.get_top_albums(user=self.user)
            responses = (
                    await self.fm.user.get_top_albums(user=self.user, page=page)
                    for page in range(int(total.pages)))
            albums = map(lambda response: response.result, await responses)
            print(tuple(albums))
            albums = filter(lambda album: album.stats.userplaycount < threshold, albums)
            return tuple(albums)

        albums_to_rate = await get_above_threshold()

        print(f"total albums above threshold: {len(albums_to_rate)}")

        async def filter_non_played_through(albums: List[Album]):
            """
            Creates a new list and only adds to it the ones that have been
            played through
            """
            played_through_albums = await asyncio.gather(
                album for album in albums if album_is_played_through(album)
            )
            return played_through_albums

        return await filter_non_played_through(albums_to_rate)


async def RateFM(user: str = "dpalme", fm=None) -> RateFMClient:
    return RateFMClient(user=user, fm=fm)
