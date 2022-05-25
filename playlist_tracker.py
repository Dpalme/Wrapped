import Wrapped2
import datetime
import requests
import base64
from watching_playlists import playlists

try:
    with open("playlist_watch.txt", encoding="UTF-8") as saved_file:
        prev = saved_file.read().rsplit('\n')[:-1]
        previous = {a:b for a,b in map(lambda a: a.split(), prev)}
except FileNotFoundError:
    previous = {playlist: "" for playlist in playlists}

wp = Wrapped2.Wrapped()
with open(f'playlist_watch.txt', 'w', encoding='UTF-8') as archivo:
    for playlist, curr in map(lambda a: (a['uri'], a), wp.get_data_by_id(wp.sp.playlist, playlists)):
        if (playlist not in previous or curr['snapshot_id'] != previous[playlist]) and input(f'create snapshot for {curr["name"]}?\n> ') == 'y':
            wp.sp.user_playlist_create(wp.USER, f'{curr["name"]} ({datetime.date.today()})', public=False, description=curr['description'])
            new_p = wp.sp.current_user_playlists(limit=1)['items'][0]
            tracks = tuple(t['track']['uri']
            for t in wp.get_chained_data(
                wp.sp.user_playlist_tracks,
                user=wp.USER,
                playlist_id=playlist,
                fields='items(track(uri)),total'))
            wp.replace_tracks(tracks, new_p['uri'])
            cover = wp.sp.playlist_cover_image(playlist)[0]['url']
            img = base64.b64encode(requests.get(cover).content)
            wp.sp.playlist_upload_cover_image(new_p['uri'], img)
            new_p = wp.sp.current_user_playlists(limit=1)['items'][0]
            print(f'''    "url": "{new_p['external_urls']['spotify']}",
    "text": "{curr['name']} ({datetime.date.today()})",
    "img": "{new_p['images'][0]['url']}"''')
        archivo.write(f'{playlist} {curr["snapshot_id"]}\n')
