import requests
from typing import List, Dict


class SpotifyClient:
    """
    Spotify API Client (safe endpoints only)

    Responsibilities:
    - Fetch playlists
    - Fetch playlist items
    - Fetch track metadata
    - Create playlists
    - Add tracks to playlists

    Does NOT include:
    - audio features (deprecated)
    - recommendations (deprecated)
    """

    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("Access token required")
        self.access_token = access_token

    def _headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def _request(self, method: str, endpoint: str, params=None, json=None) -> Dict:
        """
        Internal request handler

        Raises:
            Exception if request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        res = requests.request(
            method,
            url,
            headers=self._headers(),
            params=params,
            json=json
        )

        if res.status_code in [200, 201]:
            return res.json()

        raise Exception(f"{res.status_code}: {res.text}")

    # --------------------------------------------------
    # USER
    # --------------------------------------------------

    def get_current_user(self) -> Dict:
        """
        Get current user profile
        """
        return self._request("GET", "/me")

    # --------------------------------------------------
    # PLAYLISTS
    # --------------------------------------------------

    def get_user_playlists(self) -> List[Dict]:
        """
        Fetch all playlists for current user
        """
        data = self._request("GET", "/me/playlists")
        return data.get("items", [])

    def get_playlist_items(self, playlist_id: str) -> List[Dict]:
        """
        Fetch tracks from a playlist

        Uses NON-DEPRECATED endpoint:
        GET /playlists/{id}/items
        """
        data = self._request("GET", f"/playlists/{playlist_id}/items")
        return data.get("items", [])

    # --------------------------------------------------
    # TRACKS
    # --------------------------------------------------

    def get_track(self, track_id: str) -> Dict:
        """
        Fetch track metadata (name, artist, album, etc.)
        """
        return self._request("GET", f"/tracks/{track_id}")

    # --------------------------------------------------
    # WRITE OPERATIONS
    # --------------------------------------------------

    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Dict:
        """
        Create a new playlist for current user

        Endpoint:
        POST /users/{user_id}/playlists
        """
        current_user = self.get_current_user()
        user_id = current_user.get("id")

        if not user_id:
            raise ValueError("Spotify user id not available")

        return self._request(
            "POST",
            f"/users/{user_id}/playlists",
            json={
                "name": name,
                "description": description,
                "public": public
            }
        )

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> Dict:
        """
        Add tracks to a playlist

        Uses NON-DEPRECATED endpoint:
        POST /playlists/{id}/items
        """
        uris = [f"spotify:track:{tid}" for tid in track_ids]

        return self._request(
            "POST",
            f"/playlists/{playlist_id}/items",
            json={"uris": uris}
        )
    

# --------------------------------------------------
# SEARCH (🔥 MISSING)
# --------------------------------------------------

    def search_tracks(self, query: str, limit: int = 5) -> Dict:
        """
        Search tracks using Spotify API

        Endpoint:
        GET /search?q=...&type=track
        """
        return self._request(
            "GET",
            "/search",
            params={
                "q": query,
                "type": "track",
                "limit": limit
            }
        )
