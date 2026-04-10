from typing import Dict, Optional
import logging

from apps.integrations.spotify.client import SpotifyClient


logger = logging.getLogger(__name__)


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
            logger.debug("Skipping track resolution because no Spotify access token was provided")
            return data

        title = data.get("title")
        artist = data.get("artist")

        if not title:
            logger.debug("Skipping track resolution because title is missing")
            return data

        client = SpotifyClient(access_token)

        # 🔥 IMPROVED QUERY
        query = TrackResolver._build_query(title, artist)
        logger.debug("Resolving track with Spotify search query: %s", query)

        # ------------------------
        # CALL SPOTIFY
        # ------------------------
        try:
            response = client.search_tracks(query)
        except Exception as e:
            logger.warning("Spotify search failed while resolving track '%s': %s", title, e)
            return data

        items = response.get("tracks", {}).get("items", [])
        logger.debug("Spotify search returned %s candidate tracks", len(items))

        if not items:
            logger.info("No Spotify match found for track '%s'", title)
            return data

        # ------------------------
        # PICK BEST MATCH
        # ------------------------
        best_match = TrackResolver._pick_best_match(items, title, artist)

        if not best_match:
            logger.info("Spotify search returned candidates but no suitable match for '%s'", title)
            return data

        spotify_id = best_match.get("id")
        logger.info(
            "Resolved track '%s' to Spotify track '%s' (%s)",
            title,
            best_match.get("name"),
            spotify_id,
        )

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
