import tidalapi


class Tidal(object):
    def __init__(self) -> None:
        self.td: tidalapi.Session = tidalapi.Session()
        try:
            with open('.cache-tidal', 'r') as cache:
                self.td.load_oauth_session(**eval(cache.read()))
        except FileNotFoundError:
            link, future = self.td.login_oauth()
            print(link.verification_uri_complete)
            future.result()
            if self.td.check_login():
                with open('.cache-tidal', 'w') as cache:
                    cache.write(str({
                        "session_id": self.td.session_id,
                        "token_type": self.td.token_type,
                        "access_token": self.td.access_token,
                        "refresh_token": self.td.refresh_token
                    }))
            else:
                print("Error with login")
                exit(1)
        return self.td
