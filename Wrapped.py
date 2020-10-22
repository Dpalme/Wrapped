"""
Library of functions that use the Spotify's API.

Requires­:  , json, collections.
"""

import json
from collections import defaultdict

import spotipy
import spotipy.util as util

# Variables
data_limit = 50     # int from 1 to 50

# Constants and inits
client_id = ''
client_secret = ''
redirect_uri = 'http://localhost:8888'
username = ''
scope = """user-library-read, user-top-read, playlist-read-private,
           playlist-modify-public, playlist-modify-private, user-follow-read"""

# Makes a call to the Spotify API using Spotipy to get the access token
token = util.prompt_for_user_token(username, scope, client_id, client_secret,
                                   redirect_uri)
sp = spotipy.Spotify(auth=token)
database = {}


def get_tracks_uri(playlist_code: str):
    """Given a playlist uri, it returns a list with the uris
    of all tracks on the playlist.

    Keyword arguments:
    playlist_code -- The uri for the playlists from which to get the
    tracks.

    :return List with the uri of all tracks on the playlist.
    :rtype List
    """

    response = sp.user_playlist_tracks(username, playlist_code,
                                       fields='items(track(uri))',
                                       limit=data_limit)

    return [track['track']['uri'] for track in response['items']]


def get_tracks_name(playlist_code: str):
    """Given a playlist uri, it returns a list with the names
    of all tracks on the playlist

    :param
      playlist_code: The uri for the playlists from which to get the tracks.

    :return
      List with the names of all tracks on the playlist.
    """

    response = sp.user_playlist_tracks(username, playlist_code,
                                       fields='items(track(name))',
                                       limit=data_limit)
    return [track['track']['name'] for track in response['items']]


def get_artists(playlist_code: str):
    """Given a playlist uri, it returns a list with the names of the artists from
    the first (data limit) songs in the playlist (Includes duplicates).

    :param
      playlist_code: The uri for the playlists from which to get the tracks.

    :return
      List with the names of all artists (not featuring) on the playlist.
    """

    response = sp.user_playlist_tracks(username, playlist_code,
                                       fields='items(track(artists))',
                                       limit=data_limit)
    artists = []
    for artist in response['items']:
        artists.append(artist['track']['artists'][0]['name'])
    return artists


def get_top_tracks():
    """Returns a sorted list of the top 100 tracks from all playlists the user
    owns/follows with '2019' in the name."""

    playlists = []
    for name, uri in database["playlists"].items():
        if "2019" in name and len(name.split()) == 2:
            playlists.append(uri)

    tracks = defaultdict(int)
    for mes in playlists:
        n = data_limit
        for track in get_tracks_uri(mes):
            tracks[track] += (n//(data_limit//10))//(data_limit//10)
            n -= 1
    return sorted(tracks, key=tracks.__getitem__, reverse=True)[0:100]


def get_top_artists_2019():
    """Returns sorted list of top 100 artists from all playlists the user
    owns/follows with '2019' in the name"""

    artists = defaultdict(int)
    playlists = []
    for name, uri in database["playlists"].items():
        if "2019" in name and len(name.split()) == 2:
            playlists.append(uri)

    for mes in playlists:
        n = data_limit
        for artist in get_artists(mes):
            artists[artist] *= (n//(data_limit//10)) // (data_limit//10)
            n -= 1
    return sorted(artists, key=artists.__getitem__, reverse=True)[0:100]


def get_top_tracks_spotify():
    """Dictionary with the format {name: uri} using Spotify's internal
    all time top 50 tracks."""

    response = sp.current_user_top_tracks(50, 0, time_range='long_term')
    return {track['name']: track['uri'] for track in response['items']}


def get_top_artists_spotify():
    """Returns a dictionary with the format {name: uri} using Spotify's
    internal all time top 50 artists."""

    response = sp.current_user_top_artists(50, 0, time_range='long_term')
    return {artist['name']: artist['uri'] for artist in response['items']}


def add_tracks(tracks, uri):
    """Replaces all tracks on a given playlist with a list of tracks.
    
    :param
      - tracks: List of track uris
      - uri: uri of the playlist """
    if len(tracks) > 100:
        sp.user_playlist_replace_tracks(username, uri, [])
        for n in range((len(tracks)//100) + 1):
            sp.user_playlist_add_tracks(username, uri,
                                        tracks[100*n:100*(n+1)])
    else:
        sp.user_playlist_replace_tracks(username, tracks, uri)


def create_playlist(name, privacy=False):
    """Replaces all tracks on a given playlist with a list of tracks.
   
    :param
      - name: name for the playlist
      - privacy(optional): False for private True for public. False is default"""
    sp.user_playlist_create(username, name, public=privacy)


def update_top_all_time():
    """Replaces all tracks on the playlist named 'Top 50' with the top 50
    tracks of all time acording to the database."""

    add_tracks(tracks=[uri for name, uri in database["tracksAllTime"].items()],
               uri=database["playlists"]["Top 50"])


def update_top_playlist():
    """Replaces all tracks on the playlist named 'Top 100 2019' with the top
    100 tracks of the year."""

    add_tracks(database["playlists"]["Top 100 2019"], get_top_tracks())


def update_genres_playlists():
    """Replaces all tracks on each playlist named exactly as the genre for each
    genre in the database with all tracks put under the genre. If there isn't a
    playlist named after the genre, it creates it."""

    genres = database["genres"]
    playlists = database["playlists"]

    for genre, tracks in genres.items():
        if genre in playlists:
            uri = playlists[genre]
        else:
            sp.user_playlist_create(username, genre, public=False)
            uri = sp.current_user_playlists(limit=1)['items'][0]['uri']
            print("Cree la playlist %s, espero no haberla cagado" % genre)
        add_tracks(tracks=tracks, uri=uri)


def get_playlists():
    """Returns a dictionary with the format {'name': 'uri'} for all playlists
    the current user owns/follows."""

    playlists = {}
    response = [None]
    n = 0
    while response != []:
        response = sp.current_user_playlists(offset=50*n)['items']
        for playlist in response:
            playlists[playlist['name']] = playlist['uri']
        n += 1
    return playlists


def get_top_artists(number_of_artists):
    """Returns the 5 most listened to artists on the database.

    :param
      - number_of_artists: number of artists to return
    """
    top_artists = [name for name, uri in database["artistsAllTime"].items()]
    return top_artists[:number_of_artists]


def get_saved_albums():
    """Returns a dictionary with the format {name: uri} with all saved albums.
    """
    albums = {}
    response = [None]

    n = 0
    while response != []:
        response = sp.current_user_saved_albums(limit=data_limit,
                                                offset=data_limit*n)['items']
        for album in response:
            album = album['album']
            artist = album['artists'][0]
            albums[album['name']] = {"uri": album['uri'],
                                     "release_date": album['release_date'],
                                     "artist": {artist['name']: artist['uri']}}
        n += 1
    return albums


def get_albums_from_year(year):
    """Returns a list with all albums saved from the specified year.

    :param
      - year: year to analize. can be int or str.

    :return
      - List with the names of all albums from the specified year.
    """
    return {album: content for album, content in database['albums'].items()
            if str(year) in database['albums'][album]["release_date"]}


def get_saved_tracks():
    """Returns a dictionary with the format {name: uri} with all saved tracks.
    """
    return database['tracks']


def get_genres(minimun_songs_per_genre):
    """Returns a dictionary with the format {genre name: [uris]} from all
    saved tracks.
    """
    genres = database["genres"]

    for genre, items in genres.copy().items():
        if len(items) < minimun_songs_per_genre:
            del genres[genre]
    return genres


def database_genres_tracks_artists():
    """Optimized method for getting Genres, Tracks and Artists for all saved
    tracks.

    WARNING! This function uses a constant that changes from user to user
    to get the value to replace in the API, divide the number of songs in
    your library by 50 and round up.

      - tracks: Dictionary with format:
        {"track_name": "track_uri"}

      - artists: Dictionary with the format:
        {"artist_name": {"uri": "artist_uri", "tracks": {}, "genres": []}}

      - genres: Dictionary with the format:
        {"genre_name": {"track_name": "track_uri"}}
    """

    tracks = {}
    artists = {}
    genres = {}

    number_of_songs_divided_by_50 = 74

    for n in range(number_of_songs_divided_by_50):
        response = sp.current_user_saved_tracks(limit=50,
                                                offset=50*n)['items']
        for track in response:
            track = track['track']
            artist = track['artists'][0]

            current_track = {"uri": track['uri'], "artist":
                             {"name": artist['name'], "uri": artist['uri']}}
            tracks[track['name']] = current_track

            if artist['name'] in artists:
                artists[artist['name']]['tracks'][track['name']] = track['uri']
                for genre in artists[artist['name']]['genres']:
                    genres[genre][track['name']] = current_track
            else:
                artist = sp.artist(artist['uri'])
                artists[artist['name']] = {"uri": artist['uri'], "tracks": {},
                                           "genres": []}
                artists[artist['name']]['tracks'][track['name']] = track['uri']
                artists[artist['name']]['genres'] = artist['genres']
                for genre in artist['genres']:
                    if genre in genres:
                        genres[genre][track['name']] = current_track
                    else:
                        genres[genre] = {track['name']: current_track}

    return genres, tracks, artists


def update_genre_tracks_artists():
    with open("database.json", "w", encoding="UTF-8") as archivo:
        database["genres"], database['tracks'], database["artists"] =\
            database_genres_tracks_artists()
        archivo.write(json.dumps(database, indent=4, sort_keys=False,
                                 ensure_ascii=False))


def update_database_albums():
    with open("database.json", "w", encoding="UTF-8") as archivo:
        database["albums"] = get_saved_albums()
        archivo.write(json.dumps(database, indent=4, sort_keys=False,
                                 ensure_ascii=False))

def update_database():
    """Deletes database.json and creates a new one with the most up to date
    data."""
    database["playlists"] = get_playlists()
    print("Got playlists")
    database["tracksAllTime"] = get_top_tracks_spotify()
    print("Got top tracks")
    database["artistsAllTime"] = get_top_artists_spotify()
    print("Got top artists")
    database["albums"] = get_saved_albums()
    print("Got saved albums")
    database["genres"], database['tracks'], database["artists"] =\
        database_genres_tracks_artists()
    print("Got all saved tracks, genres and artists")

    with open("database.json", "w", encoding="UTF-8") as archivo:
        archivo.write(json.dumps(database, indent=4, sort_keys=False,
                                 ensure_ascii=False))


try:
    database = json.load(open("database.json", encoding="UTF-8"))
except FileNotFoundError:
    update_database()
