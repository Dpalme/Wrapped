from lastfm_auth import lastfm
import asyncio
import lastfmpy
import ratefm

async def main():
    res = await lastfm.user.get_top_albums(user="dpalme")
    for album in res.results:
        album = await lastfm.album.get_info(
            username='dpalme', artist=album.artist.name, album=album.name)
        for track in album.tracks:
            track = await lastfm.track.get_info(
                username='dpalme', artist=track.artist.name, track=track.name)
            print(track.stats.__dict__, sep='\t')
        print()

async def test_rate():
    fm = await lastfmpy.LastFM('3f8babce61655d2e0dc3804dafe2f83c')
    rate = await ratefm.RateFM(user='dpalme', fm=fm)
    albums = await rate.get_albums_to_rate()
    print(*map(lambda a: a.name, albums))
    print(len(albums))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_rate())
