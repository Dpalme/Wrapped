import Wrapped2
import wrapped

wp = Wrapped2.Wrapped()
# wp.update()
# wp.save()

playlist_names = {playlist['name']: playlist['id']
                  for playlist in wp.playlists.values()}
for genre, tracks in wp.genres.items():
    if genre in playlist_names:
        wp.replace_tracks(tracks, playlist_names[genre])

wrapped.replace_tracks(tuple(wp.tracks.keys()), 'spotify:playlist:7BSjFCivH1WPp1xRD3QgOF')