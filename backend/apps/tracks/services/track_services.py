from django.db import IntegrityError
from django.db.models import Q

from apps.tracks.models import Track
from apps.imports.domain.utils import generate_track_key


class TrackService:
    """
    Service layer for Track operations.

    Responsibilities:
    - Idempotent track creation
    - Deduplication (Spotify-first using spotify_id)
    - Fallback deduplication using content-based key (title + artist)
    - Safe handling of race conditions
    - Incremental enrichment updates (bpm, energy, etc.)

    Design Philosophy:
    - spotify_id is PRIMARY identity when available
    - unique_key is fallback identity
    - Never create duplicates
    - Allow progressive enrichment (fill missing fields over time)
    """

    # =========================================================
    # LOOKUP
    # =========================================================
    @staticmethod
    def get_by_spotify_id(spotify_id: str):
        """
        Fetch track by spotify_id.

        Returns:
            Track | None
        """
        if not spotify_id:
            return None

        try:
            return Track.objects.get(spotify_id=spotify_id)
        except Track.DoesNotExist:
            return None

    # =========================================================
    # CREATE (SAFE + IDEMPOTENT)
    # =========================================================
    @staticmethod
    def create_safe(data: dict):
        """
        Idempotent track creation.

        Strategy:
        1. Try Spotify ID (primary identity)
        2. Fallback to unique_key (title + artist)
        3. Update enrichment if already exists

        Returns:
            (Track, created: bool)
        """
        title = data.get("title")
        artist = data.get("artist")
        spotify_id = data.get("spotify_id")

        if not title:
            raise ValueError("Title is required")

        # --------------------------------------------------
        # PRIMARY: SPOTIFY ID
        # --------------------------------------------------
        if spotify_id:
            try:
                obj, created = Track.objects.get_or_create(
                    spotify_id=spotify_id,
                    defaults={
                        "title": title,
                        "artist": artist,
                        "bpm": data.get("bpm"),
                        "genre": data.get("genre"),
                        "energy": data.get("energy"),
                        "unique_key": generate_track_key(data),
                    }
                )

                if not created:
                    TrackService._update_enrichment(obj, data)

                return obj, created

            except IntegrityError:
                # Handle race condition safely
                try:
                    obj = Track.objects.get(spotify_id=spotify_id)
                    TrackService._update_enrichment(obj, data)
                    return obj, False
                except Track.DoesNotExist:
                    pass  # fallback to unique_key

        # --------------------------------------------------
        # FALLBACK: CONTENT KEY
        # --------------------------------------------------
        unique_key = generate_track_key(data)

        try:
            obj, created = Track.objects.get_or_create(
                unique_key=unique_key,
                defaults={
                    "title": title,
                    "artist": artist,
                    "bpm": data.get("bpm"),
                    "genre": data.get("genre"),
                    "energy": data.get("energy"),
                    "spotify_id": spotify_id,  # preserve if exists
                }
            )

            if not created:
                TrackService._update_enrichment(obj, data)

            return obj, created

        except IntegrityError:
            obj = Track.objects.get(unique_key=unique_key)
            TrackService._update_enrichment(obj, data)
            return obj, False

    # =========================================================
    # ENRICHMENT UPDATE
    # =========================================================
    @staticmethod
    def _update_enrichment(obj: Track, data: dict):
        """
        Incrementally update enrichment fields ONLY if missing.

        This ensures:
        - No overwriting good data
        - Safe progressive enrichment
        """
        updated = False

        if data.get("bpm") and not obj.bpm:
            obj.bpm = data["bpm"]
            updated = True

        if data.get("energy") and not obj.energy:
            obj.energy = data["energy"]
            updated = True

        if data.get("genre") and not obj.genre:
            obj.genre = data["genre"]
            updated = True

        if data.get("danceability") and not getattr(obj, "danceability", None):
            obj.danceability = data["danceability"]
            updated = True

        if data.get("valence") and not getattr(obj, "valence", None):
            obj.valence = data["valence"]
            updated = True

        if data.get("loudness") and not getattr(obj, "loudness", None):
            obj.loudness = data["loudness"]
            updated = True

        if updated:
            obj.save()

    # =========================================================
    # FETCH
    # =========================================================
    @staticmethod
    def fetch_track(track_id: int):
        """
        Fetch single track by ID.
        """
        return Track.objects.get(id=track_id)

    @staticmethod
    def bulk_fetch(track_ids):
        """
        Fetch multiple tracks.
        """
        return Track.objects.filter(id__in=track_ids)

    # =========================================================
    # SEARCH
    # =========================================================
    @staticmethod
    def search_tracks(query: str):
        """
        Search tracks by title or artist.
        """
        return Track.objects.filter(
            Q(title__icontains=query) |
            Q(artist__icontains=query)
        ).distinct()

    # =========================================================
    # BULK INSERT (OPTIONAL OPTIMIZATION)
    # =========================================================
    @staticmethod
    def bulk_create_safe(data_list):
        """
        Bulk insert tracks (fast path).

        Note:
        - Ignores duplicates (via DB constraints)
        - Does NOT handle enrichment updates
        """
        objects = []

        for data in data_list:
            objects.append(
                Track(
                    title=data.get("title"),
                    artist=data.get("artist"),
                    bpm=data.get("bpm"),
                    genre=data.get("genre"),
                    energy=data.get("energy"),
                    spotify_id=data.get("spotify_id"),
                    unique_key=generate_track_key(data),
                )
            )

        Track.objects.bulk_create(
            objects,
            ignore_conflicts=True
        )