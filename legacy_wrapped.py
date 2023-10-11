'''
Library of functions that use the Spotify's API.

Requires­:  spotipy_auth, json, sys.stdout.
'''

import json
from spotipy_auth import sp, USERNAME
from sys import stdout

# Variables
data_limit = 50     # int from 1 to 50
LOAD_CHARS = ('\\', '|', "/", '–')
L_CARRY = 0
database = {}


def loading():
    global L_CARRY
    L_CARRY += 1
    stdout.write(f'\r{LOAD_CHARS[L_CARRY % 4]}')
    stdout.flush()


def get_tracks_uri(playlist_code: str):
    '''Given a playlist uri, it returns a list with the uris
    of all tracks on the playlist.

    Keyword arguments:
       - `playlist_code` The uri for the playlists from which to get the
    tracks.

    :return
      - List with the uri of all tracks on the playlist.
    :rtype List
    '''
    tracks, response, n = [], [None], 0
    while response != []:
        response = sp.user_playlist_tracks(USERNAME, playlist_code,
                                           fields='items(track(uri))',
                                           limit=data_limit,
                                           offset=n*data_limit)['items']
        n += 1
        tracks.extend([track['track']['uri'] for track in response])
        loading()
    return tracks


def get_tracks_name(playlist_code: str):
    '''Given a playlist uri, it returns a list with the names
    of all tracks on the playlist

    :param
      playlist_code: The uri for the playlists from which to get the tracks.

    :return
      List with the names of all tracks on the playlist.
    '''

    tracks, response, n = [], [None], 0
    while response != []:
        response = sp.user_playlist_tracks(USERNAME, playlist_code,
                                           fields='items(track(name))',
                                           limit=data_limit,
                                           offset=n*data_limit)['items']
        n += 1
        tracks.extend([track['track']['name'] for track in response])
        loading()
    return tracks


def get_tracks_reduced(playlist_code: str):
    '''Given a playlist uri, it returns a list with the names
    of all tracks on the playlist

    :param
      playlist_code: The uri for the playlists from which to get the tracks.

    :return
      List with the names of all tracks on the playlist.
    '''

    tracks, response, n = {}, [None], 0
    fields_params = 'items(track(name, uri, artists(name, uri)))'
    while response != []:
        response = sp.user_playlist_tracks(USERNAME, playlist_code,
                                           fields=fields_params,
                                           limit=100,
                                           offset=n*100)['items']
        n += 1
        for track in response:
            t_obj = track['track']
            t_uri, t_name = t_obj['uri'], t_obj['name']
            artist = t_obj['artists'][0]
            a_uri, a_name = artist['name'], artist['uri']
            tracks[t_uri] = {'name': t_name, 'artist': {'name': a_name,
                                                        'uri': a_uri}}
        loading()
    return tracks


def get_artists(playlist_code: str):
    '''Given a playlist uri, it returns a list with the names of the artists from
    the first (data limit) songs in the playlist (Includes duplicates).

    :param
      playlist_code: The uri for the playlists from which to get the tracks.

    :return
      List with the names of all artists (not featuring) on the playlist.
    '''

    response = sp.user_playlist_tracks(USERNAME, playlist_code,
                                       fields='items(track(artists))',
                                       limit=data_limit)
    artists = []
    for artist in response['items']:
        artists.append(artist['track']['artists'][0]['name'])
        loading()
    return artists


def get_top_tracks_year(year):
    '''Returns a sorted list of the top 100 tracks from all playlists the user
    owns/follows with '2019' in the name.'''

    playlists = []
    yr_str = str(year)
    for name, uri in database['playlists'].items():
        if yr_str in name and len(name.split()) == 2:
            playlists.append(uri)
        loading()

    tracks = {}
    for mes in playlists:
        for n, track in enumerate(reversed(get_tracks_uri(mes))):
            try:
                tracks[track] *= ((n+1)//5)//5
            except KeyError:
                tracks[track] = n
        loading()
    return sorted(tracks, key=tracks.__getitem__, reverse=True)[:100]


def get_top_artists_2019(year):
    '''Returns sorted list of top 100 artists from all playlists the user
    owns/follows with '2019' in the name'''

    playlists = []
    yr_str = str(year)
    for name, uri in database['playlists'].items():
        if yr_str in name and len(name.split()) == 2:
            playlists.append(uri)
        loading()

    artists = {}
    for mes in playlists:
        for n, artist in enumerate(reversed(get_artists(mes))):
            try:
                artists[artist] *= ((n+1)//5)//5
            except KeyError:
                artists[artist] = n
    return sorted(artists, key=artists.__getitem__, reverse=True)[:100]


def get_top_tracks_spotify():
    '''Dictionary with the format {name: uri} using Spotify's internal
    all time top 50 tracks.'''
    tracks = {}
    response = sp.current_user_top_tracks(50, 0, time_range='long_term')
    for track in response['items']:
        artist = track['artists'][0]

        current_track = {'name': track['name'],
                         'artist': {'name': artist['name'],
                                    'uri': artist['uri']}}
        tracks[track['uri']] = current_track
        stdout.write('.')
    return tracks


def get_top_artists_spotify():
    '''Returns a dictionary with the format {name: uri} using Spotify's
    internal all time top 50 artists.'''

    response = sp.current_user_top_artists(50, 0, time_range='long_term')
    return {artist['uri']: artist['name'] for artist in response['items']}


def add_tracks(tracks, uri):
    '''Adds all give tracks to a playlist.

    :param
      - tracks: List of track uris
      - uri: uri of the playlist '''
    if len(tracks) > 100:
        for n in range((len(tracks)//100) + 1):
            sp.user_playlist_add_tracks(USERNAME, uri,
                                        tracks[100*n:100*(n+1)])
            loading()
    else:
        sp.user_playlist_add_tracks(USERNAME, uri, tracks)


def replace_tracks(tracks, uri):
    '''Replaces all tracks on a given playlist with a list of tracks.

    :param
      - tracks: List of track uris
      - uri: uri of the playlist '''
    if len(tracks) > 100:
        sp.user_playlist_replace_tracks(USERNAME, uri, [])
        for n in range((len(tracks) // 100) + 1):
            sp.user_playlist_add_tracks(USERNAME, uri,
                                        tracks[100*n:100*(n+1)])
            loading()
    else:
        sp.user_playlist_replace_tracks(USERNAME, uri, tracks)


def create_playlist(name, public=False):
    '''Replaces all tracks on a given playlist with a list of tracks.

    :param
      - name: name for the playlist
      - privacy(optional): False for private True for public. False is default
    '''
    sp.user_playlist_create(USERNAME, name, public=public)


def update_top_all_time():
    '''Replaces all tracks on the playlist named 'Top 50' with the top 50
    tracks of all time acording to the database.'''
    replace_tracks(tracks=get_top_tracks_spotify().keys(),
                   uri="spotify:playlist:3DVuVCAbXz14G801wEIoqO")


def update_year_top_playlist(year):
    '''Replaces all tracks on the playlist named 'Top 100 2019' with the top
    100 tracks of the year.'''

    replace_tracks(database['playlists']
                   [f'top 100 {year}'], get_top_tracks_year(year))


def update_genres_playlists(genre_list):
    '''Replaces all tracks on each playlist named exactly as a genre in the
    database with all tracks put under the genre'''

    genres, playlists = merge_genres(genre_list), database['playlists']
    for genre, tracks in genres.items():
        replace_tracks(tracks, playlists[genre])
        loading()


def get_playlists():
    '''Returns a dictionary with the format {'name': 'uri'} for all playlists
    the current user owns/follows.'''

    playlists, res, n = {}, None, 0
    iters = (sp.current_user_playlists(limit=1)['total']//50)+1
    for n in range(iters):
        res = sp.current_user_playlists(offset=50*n)['items']
        playlists.update({p['name']: p['uri'] for p in res})
        loading()
    return playlists


def get_saved_albums():
    '''Returns a dictionary with the format {name: uri} with all saved albums.
    '''
    albums, response, n = {}, None, 0

    while response != []:
        response = sp.current_user_saved_albums(limit=data_limit,
                                                offset=data_limit*n)['items']
        for album in response:
            album = album['album']
            artist = album['artists'][0]
            albums[album['uri']] = {'name': album['name'],
                                    'release_date': album['release_date'],
                                    'artist': {'uri': artist['uri'],
                                               'name': artist['name']}}
        n += 1
        loading()
    return albums


def get_albums_from_year(year, saved_percent=.9):
    '''Returns a list with all albums saved from the specified year.

    :param
      - year: year to analize. can be int or str.
      - saved_percent: float from 0 to 1 that represents the percentage
      of tracks saved for it to be returned. defaults to 90%.

    :return
      - List with the names of all albums from the specified year.
    '''
    yr_st = str(year)
    albums = {}
    for a_id, album in database['albums']['items'].items():
        if yr_st in album['release_date'] and album['type'] == 'album':
            if len(album['tracks']) >= album['total_tracks']*saved_percent:
                albums[a_id] = album
    for uri, album in database['saved_albums'].items():
        if yr_st in album['release_date']:
            a_id = uri[-22:]
            albums[a_id] = database['albums']['items'][a_id]
    return albums


def get_saved_tracks():
    '''Returns a dictionary with the format {name: uri} with all saved tracks.
    '''
    return database['tracks']


def get_genres(minimun_songs_per_genre):
    '''Returns a dictionary with the format {genre name: [uris]} from all
    saved tracks.
    '''
    genres = database['genres']['items']
    for genre, items in genres.copy().items():
        if len(items) < minimun_songs_per_genre:
            del genres[genre]
    return genres


def merge_genres(genre_list):
    '''Returns a dictionary with the format {genre name: [uris]} from all
    saved tracks.
    '''
    from re import search
    all_genres = database['genres']['items']
    genres_str = r'.*(' + r'|'.join(genre_list) + r').*'
    genres = {gen: set() for gen in genre_list}
    for genre, items in all_genres.items():
        res = search(genres_str, genre)
        if res:
            genres[res.group(1)].update(set(items))
    return {name: tuple(cont) for name, cont in genres.items()}


def database_genres_tracks_artists():
    '''Optimized method for getting Genres, Tracks and Artists for all saved
    tracks.

    WARNING! This function uses a constant that changes from user to user
    to get the value to replace in the API, divide the number of songs in
    your library by 50 and round up.

      - tracks: Dictionary with format:
        {'track_name': 'track_uri'}

      - artists: Dictionary with the format:
        {'artist_name': {'uri': 'artist_uri', 'tracks': {}, 'genres': []}}

      - genres: Dictionary with the format:
        {'genre_name': {'track_name': 'track_uri'}}
    '''

    tracks, artists = {'total': 0, 'items': []}, {'total': 0, 'items': {}}
    genres, albums = {'total': 0, 'items': {}}, {'total': 0, 'items': {}}
    iterations = sp.current_user_saved_tracks(limit=1)['total']//50 + 1
    for n in range(iterations):
        response = sp.current_user_saved_tracks(limit=50,
                                                offset=50*n)['items']
        for t_obj in response:
            track = t_obj['track']
            artist, album = track['artists'][0], track['album']
            t_uri, ar_uri, al_uri = track['uri'], artist['uri'], album['uri']
            al_id, ar_id = album['id'], artist['id']
            track_dic = {'name': track['name'],
                         'uri': t_uri,
                         'saved': t_obj['added_at']}
            tracks['items'].append(t_uri)
            tracks['total'] += 1
            if ar_id in artists['items']:
                art_dict = artists['items'][ar_id]
                if al_uri not in art_dict['albums']:
                    art_dict['albums'].append(al_uri)
                art_dict['tracks'].append(t_uri)
                c_genres = art_dict['genres']
            else:
                artist = sp.artist(ar_uri)
                c_genres = artist['genres']
                fllwrs = artist['followers']['total']
                artists['items'][ar_id] = {'name': artist['name'],
                                           'uri': ar_uri,
                                           'followers': fllwrs,
                                           'popularity': artist['popularity'],
                                           'genres': c_genres,
                                           'albums': [al_uri],
                                           'tracks': [t_uri]}
                artists['total'] += 1

            for genre in c_genres:
                if genre not in genres['items']:
                    genres['items'][genre] = []
                    genres['total'] += 1
                genres['items'][genre].append(t_uri)

            if al_id in albums['items']:
                albums['items'][al_id]['tracks'].append(track_dic)
            else:
                album = sp.album(al_uri)
                al_obj = {'name': album['name'],
                          'uri': album['uri'],
                          'type': album['album_type'],
                          'genres': c_genres,
                          'popularity': album['popularity'],
                          'release_date': album['release_date'],
                          'artist': {'name': artist['name'],
                                     'uri': ar_uri},
                          'total_tracks': album['tracks']['total'],
                          'tracks': [track_dic]}
                albums['items'][al_id] = al_obj
                albums['total'] += 1
        x = int(40*((n + 1)/iterations))
        stdout.write(''.join(('\r[', '■'*(x), ' '*(40-x), ']')))
        stdout.flush()
    return genres, tracks, artists, albums


def update_genre_tracks_artists():
    with open('database.json', 'w', encoding='UTF-8') as archivo:
        database['genres'], database['tracks'], database['artists'] =\
            database_genres_tracks_artists()
        archivo.write(json.dumps(database, indent=4, sort_keys=False,
                                 ensure_ascii=False))


def update_database_albums():
    with open('database.json', 'w', encoding='UTF-8') as archivo:
        database['albums'] = get_saved_albums()
        archivo.write(json.dumps(database, indent=4, sort_keys=False,
                                 ensure_ascii=False))


def update_database():
    '''Overwrites database.json with the most up to date data.'''
    stdout.write(' - getting playlists\n')
    database['playlists'] = get_playlists()
    stdout.write('\r - getting top tracks from spotify\n')
    stdout.flush()
    database['tracksAllTime'] = get_top_tracks_spotify()
    stdout.write('\r - getting top artists from spotify\n')
    stdout.flush()
    database['artistsAllTime'] = get_top_artists_spotify()
    stdout.write('\r - getting saved albums\n')
    stdout.flush()
    database['saved_albums'] = get_saved_albums()
    stdout.write('\r - getting genres, tracks and artists\n')
    stdout.flush()
    genres, tracks, artists, albums = database_genres_tracks_artists()
    database['genres'], database['tracks'] = genres, tracks
    database['artists'], database['albums'] = artists, albums
    stdout.write('\r - writing to json\n')
    stdout.flush()
    save_json('database', database)


def save_json(fn, data):
    with open(f'{fn}.json', 'w', encoding='UTF-8') as archivo:
        archivo.write(json.dumps(data, indent=4, sort_keys=False,
                                 ensure_ascii=False))


try:
    database = json.load(open('database.json', encoding='UTF-8'))
except FileNotFoundError:
    update_database()
