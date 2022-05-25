import tidal_auth
import Wrapped2
import concurrent.futures

td = tidal_auth.Tidal().td
tidal_auth.tidalapi.Album.id
wp = Wrapped2.Wrapped()


def get_data_by_id(fn, ids, *args, **kwargs):
    ids = set(ids)
    n = len(ids) if len(ids) < 20 else 20
    with concurrent.futures.ThreadPoolExecutor(n) as ex:
        return (
            req.result()
            for req in concurrent.futures.as_completed(
                {ex.submit(fn, *args, **kwargs) for id in ids})
        )

queries = {f"{a['name']} {''.join(ar['name'] for ar in a['artists'].values())}" for a in wp.albums.values()}
with concurrent.futures.ThreadPoolExecutor(20) as ex:
    for req in concurrent.futures.as_completed(
        {ex.submit(td.search, 'album', query) for query in queries}
    ):
        if len(req.result()):
            print(req.__annotations__)
    albums = (
        req.result().albums
        for req in concurrent.futures.as_completed(
            {ex.submit(td.search, 'album', query) for query in queries})
    )

favorites = tidal_auth.tidalapi.Favorites(td, td.user.id)
for album in albums:
    if len(album):
        favorites.add_album(album[0].id)
# print(*(a.name for a in favorites.albums()))
# get_data_by_id(favorites.add_album, albums)
