import random
import asyncio

import spotipy_auth
from lastfm_auth import lastfm
import lastfmpy

async def get_top_week_tracks(user: str) -> list[lastfmpy.objects.Track]:
    return await lastfm.user.get_weekly_track_chart(user=user)

async def get_recent_tracks(user: str,
                            number_of_tracks:int = 20,
                            existing_tracks: list[lastfmpy.objects.Track] = []) -> list[lastfmpy.objects.Track]:
    tracks = {f'{track.name} - {track.artist.name}': track
                        for track in existing_tracks}
    async def get_random_recent_track() -> lastfmpy.objects.Track:
        return (await lastfm.user.get_recent_tracks(user=user, limit=1, page=random.randint(0, 1024))).results[-1]
    while len(tracks) < number_of_tracks:
        random_track = await get_random_recent_track()
        if f'{random_track.name} - {random_track.artist.name}' not in tracks:
            tracks[f'{random_track.name} - {random_track.artist.name}'] = random_track
            print('+', end='')
            continue
        print('.', end='')
    print()
    return set(tracks.values())

async def get_new_tracks(user: str, number_of_tracks: int) -> list[lastfmpy.objects.Track]:
    top_tracks = (await get_top_week_tracks(user=user)).items[:number_of_tracks]
    print('got top tracks')
    recent_tracks = await get_recent_tracks(user=user,
                                            number_of_tracks=number_of_tracks*2,
                                            existing_tracks=top_tracks)
    print('added random recent plays')
    return recent_tracks


async def translate_tracks_to_sp(tracks: list[lastfmpy.objects.Track]) -> list[str]:
    def find_lastfm_track_in_spotify(track: lastfmpy.objects.Track) -> str:
        results = spotipy_auth.sp.search(q=f'{track.artist.name} - {track.name}')
        for track_result in results['tracks']['items']:
            if (track_result['name'].lower() == track.name.lower()):
                print(f'\x1b[1;32m{track.name} - {track.artist.name}\x1b[0m')
                return track_result['uri']
        print(f'\x1b[1;33m{track.name} - {track.artist.name}\x1b[0m')
        if not len(results['tracks']['items']):
            return None
        return results['tracks']['items'][0]['uri']
    return list(set(filter(lambda a: a is not None,
                       (find_lastfm_track_in_spotify(track)
                        for track in tracks))))

async def update_playlist(playlist_id: str, number_of_tracks: int):
    tracks = await  get_new_tracks(user='dpalme', number_of_tracks=number_of_tracks)
    sp_tracks = await translate_tracks_to_sp(tracks=tracks)
    random.shuffle(sp_tracks)
    tracks_to_add = sp_tracks[:number_of_tracks]
    spotipy_auth.sp.playlist_replace_items(playlist_id=playlist_id,
                                           items=tracks_to_add)
    playlist = spotipy_auth.sp.playlist(playlist_id=playlist_id, fields='external_urls')
    print(playlist['external_urls']['spotify'])

async def main():
    await update_playlist(playlist_id='09qBk2r5XTES8ma0CJIjoG', number_of_tracks=20)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())