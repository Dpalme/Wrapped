import itertools

from six import print_
import spotipy_auth
import json
import concurrent.futures
import collections
DATA_LIMIT = 50


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
        
    def get_data_by_id(self, fn, ids):
        ids = set(ids)
        n = len(ids) if len(ids) < 20 else 20
        with concurrent.futures.ThreadPoolExecutor(n) as ex:
            return (
                req.result()
                for req in concurrent.futures.as_completed(
                    {ex.submit(fn, _id) for _id in ids})
            )

    def get_chained_data(self, fn):
        reqs = range(0, fn(limit=1)['total'], DATA_LIMIT)
        n = len(reqs) if len(reqs) < 50 else 50
        with concurrent.futures.ThreadPoolExecutor(n) as ex:
            return itertools.chain.from_iterable(
                req.result()['items']
                for req in concurrent.futures.as_completed(
                    {ex.submit(fn, DATA_LIMIT, n): n for n in reqs}))

    def get_saved_albums(self):
        self.albums = {a['album']['id']: {
            "name": a['album']['name'],
            "id": a['album']['id'],
            "type": a['album']['type'],
            "popularity": a['album']['popularity'],
            "release_date": a['album']['release_date'],
            'added_date': a['added_at'],
            "upc": a['album']['external_ids']['upc'] if 'upc' in a['album']['external_ids'] else '',
            "artists": {
                ar['id']: {
                    'name': ar['name'],
                    'uri': ar['id']}
                for ar in a['album']['artists']},
            "total_tracks": a['album']['total_tracks'],
            "tracks": {
                    t['id']: {
                    'name': t['name'],
                    'id': t['id']}
                 for t in a['album']['tracks']['items']}}
            for a in self.get_chained_data(self.sp.current_user_saved_albums)}
        print(len(self.albums), 'albums')
        return self.albums

    def get_playlists(self):
        self.playlists = {
            p['id']: {
                'name': p['name'],
                'id': p['id'],
                'description': p['description'],
                'owner': {
                    'display_name': p['owner']['display_name'],
                    'uri': p['owner']['uri']
                }}
            for p in self.get_chained_data(self.sp.current_user_playlists)}
        print(len(self.playlists), 'playlists')
        return self.playlists

    def get_tracks(self):
        self.tracks = {t['track']['id']: {
            "name": t['track']['name'],
            "id": t['track']['id'],
            "popularity": t['track']['popularity'],
            "release_date": t['track']['album']['release_date'],
            'added_date': t['added_at'],
            "isrc": t['track']['external_ids']['isrc'],
            "artists": 
                {ar['id']: {
                    'name': ar['name'],
                    'id': ar['id'],
                    'uri': ar['uri']}
                 for ar in t['track']['artists']},
            "album": {
                'uri': t['track']['album']['uri'],
                'id': t['track']['album']['id'],
                'name': t['track']['album']['name']}
        } for t in self.get_chained_data(self.sp.current_user_saved_tracks)}
        print(len(self.tracks), 'tracks')
        return self.tracks

    def get_artists(self):
        self.artists = {a['id']: {
            "name": a['name'],
            "id": a['id'],
            "popularity": a['popularity'],
            "uri": a['uri'],
            'genres': a['genres'],
            "followers": a['followers']['total']
        } for a in self.get_data_by_id(
            self.sp.artist,
            {artist for album in self.albums.values() for artist in album['artists']})}
        print(len(self.artists), 'artists')
        return self.artists

    def update(self):
        self.get_playlists()
        self.get_saved_albums()
        self.get_tracks()
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
    wrapped.update()
    wrapped.save()
