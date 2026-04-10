import unittest


raise unittest.SkipTest("Manual Spotify smoke script; excluded from automated test runs")

SPOTIFY_TOKEN = "BQBjlhtddi6FPpvkGzmyEqjPjJZzFUUAWJ7X0gDLXWX6Fkj1jI9ng6csKWIWORVPS3b_Yb3hwp9cqOww4RsWAzJOsb7GTxcU6J9goGvSfZKbFfanlDP06UxVSxtSwDBYIwuf0PhWzh5wh5HUOJrusoruKvix-TelZKE3y1bEMkv3l9Pa1nLEovmbmwz8NgKFTxJtfPN6_DxJgBvnYx9uIbVhQ-FvROyy908EvAgfietUWGPsKQRcvNTF1HXfvkDSSJv23VOc8HHPxKRt1utpyfyW_-1E5xH1rJbkRQw8rmQOuGlpAQmEwY9zoqqq4drUDc7B7mjhVDG6DJY"


client = SpotifyClient(SPOTIFY_TOKEN)


def test_user():
    print("\n=== USER ===")
    user = client.get_current_user()
    print("Name:", user.get("display_name"))
    print("ID:", user.get("id"))


def test_playlists():
    print("\n=== PLAYLISTS ===")
    playlists = client.get_user_playlists()

    print(f"Total playlists: {len(playlists)}")

    for i, p in enumerate(playlists[:5]):
        print(f"{i+1}. {p.get('name')} (ID: {p.get('id')})")

    return playlists


def extract_valid_track_ids(items):
    valid = []

    for item in items:
        # 🔥 FINAL FIX: support BOTH formats
        track = item.get("track") or item.get("item")

        if not track:
            continue

        if track.get("type") != "track":
            continue

        if not track.get("id"):
            continue

        valid.append(track["id"])

    return valid


def find_first_non_empty_playlist(playlists):
    """
    Finds first playlist that actually has tracks
    """
    for p in playlists:
        items = client.get_playlist_items(p["id"])

        if items and len(items) > 0:
            return p, items

    return None, []


def test_playlist_items(playlists):
    print("\n=== PLAYLIST ITEMS ===")

    if not playlists:
        print("No playlists found")
        return []

    playlist, items = find_first_non_empty_playlist(playlists)

    if not playlist:
        print("No non-empty playlists found")
        return []

    print("Testing playlist:", playlist["name"])
    print(f"Raw items: {len(items)}")

    # 🔍 Debug sample item (very useful)
    if items:
        print("\nSample item:")
        print(items[0])

    track_ids = extract_valid_track_ids(items)
    print(f"Valid tracks: {len(track_ids)}")

    return track_ids


def test_track(track_ids):
    print("\n=== TRACK FETCH ===")

    if not track_ids:
        print("No valid tracks")
        return

    track_id = track_ids[0]

    track = client.get_track(track_id)

    print("Track Name:", track.get("name"))
    print("Artist:", track["artists"][0]["name"])
    print("Album:", track["album"]["name"])


def test_create_playlist():
    print("\n=== CREATE PLAYLIST ===")

    playlist = client.create_playlist(
        name="Test Playlist API",
        description="Created via API",
        public=False
    )

    print("Created Playlist:", playlist.get("name"))
    print("Playlist ID:", playlist.get("id"))

    return playlist.get("id")


def test_add_tracks(playlist_id, track_ids):
    print("\n=== ADD TRACKS ===")

    if not playlist_id or not track_ids:
        print("Missing playlist or tracks")
        return

    response = client.add_tracks_to_playlist(
        playlist_id,
        track_ids[:3]  # add first 3 tracks
    )

    print("Tracks added:", response)


if __name__ == "__main__":
    test_user()

    playlists = test_playlists()

    track_ids = test_playlist_items(playlists)

    test_track(track_ids)

    new_playlist_id = test_create_playlist()

    test_add_tracks(new_playlist_id, track_ids)
