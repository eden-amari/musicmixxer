from typing import Dict, Optional

from apps.integrations.spotify.client import SpotifyClient


class TrackResolver:
    """
    Resolves track identity using Spotify search.
    """

    @staticmethod
    def resolve(data: Dict, access_token: Optional[str]) -> Dict:
        """
        Resolve a track into Spotify identity.

        Returns:
            dict with spotify_id if found, else original data
        """

        # ------------------------
        # SKIP IF ALREADY RESOLVED
        # ------------------------
        if data.get("spotify_id"):
            return data

        # ------------------------
        # SKIP IF NO TOKEN
        # ------------------------
        if not access_token:
            print("❌ No access token → skipping resolver")
            return data

        title = data.get("title")
        artist = data.get("artist")

        if not title:
            print("❌ Missing title → cannot resolve")
            return data

        client = SpotifyClient(access_token)

        # 🔥 IMPROVED QUERY
        query = TrackResolver._build_query(title, artist)

        print(f"\n🔍 RESOLVER QUERY: {query}")

        # ------------------------
        # CALL SPOTIFY
        # ------------------------
        try:
            response = client.search_tracks(query)
        except Exception as e:
            print("❌ Spotify API error:", str(e))
            return data

        items = response.get("tracks", {}).get("items", [])

        print(f"🎯 Found {len(items)} results")

        if not items:
            print("❌ No matches found")
            return data

        # ------------------------
        # PICK BEST MATCH
        # ------------------------
        best_match = TrackResolver._pick_best_match(items, title, artist)

        if not best_match:
            print("❌ No good match selected")
            return data

        spotify_id = best_match.get("id")

        print(f"✅ MATCH FOUND: {best_match.get('name')} → {spotify_id}")

        # ------------------------
        # RETURN MERGED DATA
        # ------------------------
        return {
            **data,
            "title": best_match.get("name") or data.get("title"),
            "artist": TrackResolver._extract_artist(best_match) or data.get("artist"),
            "spotify_id": spotify_id,
        }

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    @staticmethod
    def _build_query(title: str, artist: Optional[str]) -> str:
        """
        Build precise Spotify search query
        """
        if artist:
            return f"track:{title} artist:{artist}"
        return f"track:{title}"

    @staticmethod
    def _pick_best_match(items, title: str, artist: Optional[str]):
        """
        Simple MVP matching:
        - Exact title match first
        - Otherwise first result
        """
        title_lower = title.lower()

        for item in items:
            if item.get("name", "").lower() == title_lower:
                return item

        return items[0] if items else None

    @staticmethod
    def _extract_artist(track: Dict) -> Optional[str]:
        artists = track.get("artists")

        if isinstance(artists, list) and artists:
            return artists[0].get("name")

        return None