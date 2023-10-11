from typing import Dict, List
import spotipy
import wrapped
import datetime
import requests
import base64
from watching_playlists import playlists as watched_playlists
import spotipy_auth
wp = wrapped.Wrapped(sp=spotipy_auth.sp)

def get_snapshots() -> Dict[str, str]:
    try:
        with open("playlist_watch.txt", encoding="UTF-8") as saved_file:
            prev = saved_file.read().rsplit('\n')[:-1]
            return {a:b for a,b in map(lambda a: a.split(), prev)}
    except FileNotFoundError:
        return {playlist: "" for playlist in watched_playlists}

def snapshot_playlist(wp, playlist, curr):
    wp.sp.user_playlist_create(wp.USER,
        f'{curr["name"]} ({datetime.date.today()})', public=False,
        description=curr['description'])
    new_playlist = wp.sp.current_user_playlists(limit=1)['items'][0]
    tracks = get_tracks_from_playlist(playlist)
    wp.replace_tracks(tracks, new_playlist['uri'])
    cover = wp.sp.playlist_cover_image(playlist)[0]['url']
    img = base64.b64encode(requests.get(cover).content)
    wp.sp.playlist_upload_cover_image(new_playlist['uri'], img)
    new_playlist = wp.sp.current_user_playlists(limit=1)['items'][0]
    return new_playlist

def get_tracks_from_playlist(playlist):
    return tuple(t['track']['uri']
                for t in wp.get_chained_data(
                    wp.sp.user_playlist_tracks,
                    user=wp.USER,
                    playlist_id=playlist,
                    fields='items(track(uri)),total'))

def main():
    try:
        snapshots, playlists = [], wp.get_data_by_id(wp.sp.playlist, watched_playlists)
        snapshots = get_snapshots()
    except spotipy.exceptions.SpotifyException:
        return
    
    for playlist in playlists:
        uri = playlist['uri']
        if ((uri not in snapshots or playlist['snapshot_id'] != snapshots[uri])
            and input(f'create snapshot for {playlist["name"]}?\n> ') == 'y'):

            new_playlist = snapshot_playlist(wp, uri, playlist)
            print(f'''    "url": "{new_playlist['external_urls']['spotify']}",
    "text": "{playlist['name']} ({datetime.date.today()})",
    "img": "{new_playlist['images'][0]['url']}"''')
        snapshots[uri] = playlist["snapshot_id"]
    save_snapshots(snapshots)

def save_snapshots(playlists: dict[str, str]) -> None:
    with open(f'playlist_watch.txt', 'w', encoding='UTF-8') as archivo:
        for uri, snapshot_id in playlists.items():
            archivo.write(f'{uri} {snapshot_id}\n')


if __name__ == '__main__':
    main()