import Wrapped2
wp = Wrapped2.Wrapped()


for year in range(2021, 2022):
    print(str(year) + ':\n')
    for album in sorted(
            filter(
                lambda a: str(year) in a['added_date'],
                wp.albums.values()
            ),
            key=lambda a: a['added_date']
    ):
        for track in album['tracks']:
            if track in wp.tracks and str(year) not in wp.tracks[track]['added_date']:
                break
        else:
            print(
                str(album["name"]),
                '-',
                f'{", ".join(ar["name"] for ar in album["artists"].values())}'
            )
