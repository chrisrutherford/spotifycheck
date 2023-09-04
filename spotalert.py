import json
import os
from datetime import datetime as dt

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
scope = "user-follow-read"
ARTIST_LIMIT = 50
RELEASE_DATE_FMT = "%Y-%m-%d"
today = dt.today()

sp = Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.environ.get("REDIRECT_URI"),
        scope=scope,
    )
)


def main():
    token_check()
    artist_info = get_followed_artists()
    get_latest_albums(artist_info)


def get_followed_artists() -> dict[str, str]:
    all_followed_artists = []
    artists = {}
    followed_artists = sp.current_user_followed_artists(ARTIST_LIMIT)
    all_followed_artists.extend(followed_artists["artists"]["items"])
    while followed_artists["artists"]["next"]:
        followed_artists = sp.next(followed_artists["artists"])
        all_followed_artists.extend(followed_artists["artists"]["items"])
    print(f"{len(all_followed_artists) = }")
    for artist in all_followed_artists:
        artists[artist["id"]] = artist["name"]
    return artists


def get_latest_albums(artist_info: dict[str, str]):
    media_types = ["album", "single"]
    for a_id, a_name in artist_info.items():
        print(f"Obtaining new release information for {a_name}")
        for type in media_types:
            print("* " * 5 + type.upper() + "S" + " *" * 5)
            releases = sp.artist_albums(a_id, album_type=type)
            for i, media_info in enumerate(releases["items"]):
                release_date = media_info["release_date"]
                release_date_dt = dt.strptime(release_date, RELEASE_DATE_FMT)
                if (today - release_date_dt).days > 7:
                    if i == 0:
                        print(f"No new {type}s released within the past week.")
                    break
                name = media_info["name"]
                print(f"{name} was released on {release_date}")
        print("-" * 80)


def token_check() -> None:
    CACHE_FILE = ".cache"
    if os.path.isfile(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache: dict[str, str] = json.load(f)
        exp_date = dt.fromtimestamp(cache["expires_at"])
        print(f"current token expires at {exp_date}")


if __name__ == "__main__":
    main()
