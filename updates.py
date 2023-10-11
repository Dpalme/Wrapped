import wrapped as wrapped2
import legacy_wrapped as wrapped
from spotipy_auth import sp

wp = wrapped2.Wrapped(sp)
wp.update()
wp.save()

playlist_names = {playlist['name']: playlist['id']
                  for playlist in wp.playlists.values()}
for genre, tracks in wp.genres.items():
    if genre in playlist_names:
        wrapped.replace_tracks(tracks, playlist_names[genre])

wrapped.replace_tracks(tuple(wp.tracks.keys()), 'spotify:playlist:7BSjFCivH1WPp1xRD3QgOF')