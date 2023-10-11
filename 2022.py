import spotipy_auth
import json


def getSrcSet(images: list[dict]) -> str:
    return f'{images[2]["url"]} 64w {images[1]["url"]} 300w {images[0]["url"]} 640w'

def export_albums_dataset(albums_playlist: str):
    response = spotipy_auth.sp.playlist_tracks(albums_playlist)
    data = [
    {
        'name': track['track']['album']['name'],
        'artist': ', '.join(
            map(lambda a: a['name'], track['track']['artists'])),
        'thumbnail': track['track']['album']['images'][0]['url'],
        'srcSet': getSrcSet(track['track']['album']['images']),
        'preview_url': track['track']['preview_url'],
        'album_link': track['track']['album']['external_urls']['spotify']
    }
    for track in response['items']
    ]
    with open('2022-albums.json', 'w', encoding='UTF-8') as output_file:
        output_file.write(json.dumps(data))


def export_tracks_dataset(tracks_playlist: str):

    response = spotipy_auth.sp.playlist_tracks(tracks_playlist)
    data = [
    {
        'name': track['track']['name'],
        'artist': ', '.join(
            map(lambda a: a['name'], track['track']['artists'])),
        'thumbnail': track['track']['album']['images'][0]['url'],
        'srcSet': getSrcSet(track['track']['album']['images']),
        'preview_url': track['track']['preview_url'],
        'album_link': track['track']['external_urls']['spotify']
    }
    for track in response['items']
    ]
    with open('2022-tracks.json', 'w', encoding='UTF-8') as output_file:
        output_file.write(json.dumps(data))


if __name__ == '__main__':
    albums_playlist = '0l8cb1mqo4h5v1uvZJRAj4'
    export_albums_dataset(albums_playlist=albums_playlist)
    tracks_playlist = '5bztx6p8HvSRPBEg604V40'
    export_tracks_dataset(tracks_playlist=tracks_playlist)