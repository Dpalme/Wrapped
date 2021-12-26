import wrapped
import datetime
from watching_playlists import playlists

try:
    with open("playlist_watch.txt", encoding="UTF-8") as saved_file:
        prev = saved_file.read().rsplit('\n')[:-1]
        previous = {a:b for a,b in map(lambda a: a.split(), prev)}
except FileNotFoundError:
    previous = {playlist: "" for playlist in playlists}


with open(f'playlist_watch.txt', 'w', encoding='UTF-8') as archivo:
    for playlist in playlists:
        curr = wrapped.sp.playlist(playlist)
        if curr['snapshot_id'] != previous[playlist]:
            wrapped.create_playlist(f'{curr["name"]} ({datetime.date.today()})')
            new_p = wrapped.sp.current_user_playlists(limit=1)['items'][0]['uri']
            wrapped.replace_tracks(wrapped.get_tracks_uri(playlist), new_p)
            if curr['description'] != '':
                wrapped.sp.playlist_change_details(playlist, description=curr['description'])
        archivo.write(f'{playlist} {curr["snapshot_id"]}\n')