import itertools
import spotipy_auth
import json
import concurrent.futures
import collections
DATA_LIMIT = 50


class Track(object):
    def __init__(self, uri, name, popularity, release_date,
                 added_date, isrc, artists, album):
        self.uri = uri
        self.name = name
        self.popularity = popularity
        self.release_date = release_date
        self.added_date = added_date
        self.isrc = isrc
        self.artists = artists
        self.album = album


class Wrapped(object):
    def __init__(self, sp=spotipy_auth.sp):
        # Makes a call to the Spotify API using Spotipy to get the access token
        self.sp = sp
        self.playlists = {}
        self.albums = {}
        self.artists = {}
        self.tracks = {}
        self.genres = collections.defaultdict(list)
        try:
            database = json.load(open("database.json", encoding="UTF-8"))
            self.tracks = database['tracks']
            self.albums = database['albums']
            self.playlists = database['playlists']
            self.artists = database['artists']
        except FileNotFoundError:
            self.update()

    def get_data(self, fn):
        reqs = range(0, fn(limit=1)['total'], DATA_LIMIT)
        n = len(reqs)
        n = n if n <= 50 else 50
        with concurrent.futures.ThreadPoolExecutor(n) as ex:
            return tuple(itertools.chain.from_iterable(
                req.result()['items']
                for req in concurrent.futures.as_completed(
                    {ex.submit(fn, DATA_LIMIT, n): n for n in reqs})))

    def get_saved_albums(self):
        self.albums = {a['album']['id']: {
            "name": a['album']['name'],
            "uri": a['album']['uri'],
            "type": a['album']['type'],
            "popularity": a['album']['popularity'],
            "release_date": a['album']['release_date'],
            'added_date': a['added_at'],
            "upc": a['album']['external_ids']['upc'],
            "artists": {
                ar['uri']: {
                    'name': ar['name'],
                    'uri': ar['uri']}
                for ar in a['album']['artists']},
            "total_tracks": a['album']['total_tracks'],
            "tracks": [
                {t['uri']: {
                    'name': t['name'],
                    'uri': t['uri']}
                 for t in a['album']['tracks']['items']}]}
            for a in self.get_data(self.sp.current_user_saved_albums)}
        return self.albums

    def get_playlists(self):
        self.playlists = {
            p['id']: {
                'name': p['name'],
                'uri': p['uri'],
                'description': p['description'],
                'owner': {
                    'display_name': p['owner']['display_name'],
                    'uri': p['owner']['uri']
                }}
            for p in self.get_data(self.sp.current_user_playlists)}
        return self.playlists

    def get_tracks(self):
        self.tracks = {t['track']['id']: {
            "name": t['track']['name'],
            "uri": t['track']['uri'],
            "popularity": t['track']['popularity'],
            "release_date": t['track']['album']['release_date'],
            'added_date': t['added_at'],
            "isrc": t['track']['external_ids']['isrc'],
            "artists": [
                {ar['uri']: {
                    'name': ar['name'],
                    'uri': ar['uri']}
                 for ar in t['track']['artists']}],
            "album": {
                'uri': t['track']['album']['uri'],
                'id': t['track']['album']['id'],
                'name': t['track']['album']['name']}
        } for t in self.get_data(self.sp.current_user_saved_tracks)}
        return self.tracks

    def get_artists(self):
        artists = {}
        for track in self.tracks.values():
            for a in track['artists']:
                uri = tuple(a.keys())[0]
                track = {track['uri']: {
                    'uri': track['uri'],
                    'name': track['name']}}
                if uri in artists:
                    artists[uri]['tracks'].append(track)
                else:
                    artists[uri] = {
                        'uri': uri,
                        'name': a[uri]['name'],
                        'tracks': [track]
                    }
        self.artists = artists
        return self.artists

    def update(self):
        self.get_playlists()
        self.get_saved_albums()
        # self.get_tracks()
        self.get_artists()
        self.save()

    def save(self, filename='database'):
        with open(f'{filename}.json', 'w', encoding='UTF-8') as archivo:
            archivo.write(json.dumps({
                'playlists': self.playlists,
                'albums': self.albums,
                'tracks': self.tracks,
                'artists': self.artists
            },
                indent=2,
                sort_keys=False,
                ensure_ascii=False))


if __name__ == '__main__':
    wrapped = Wrapped()
    # wrapped.update()
    wrapped.save()
