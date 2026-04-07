from django.db import models


class Track(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)

    # 🔥 Spotify source of truth
    spotify_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )

    # 🔥 deterministic dedup key (VERY IMPORTANT)
    unique_key = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
    )

    # enrichment fields (nullable for now)
    bpm = models.FloatField(null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)
    danceability = models.FloatField(null=True, blank=True)
    loudness = models.FloatField(null=True, blank=True)
    valence = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    # Enrichment Status
    @property
    def is_enriched(self) -> bool:
        """
        A track is considered enriched if the core
        audio features have been filled in.
        """
        return all([
            self.bpm is not None,
            self.energy is not None,
            self.genre is not None,
        ])