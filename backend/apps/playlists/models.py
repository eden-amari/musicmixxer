from django.db import models
from django.conf import settings
from django.db import models

class Playlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="playlists"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    spotify_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (User: {self.user_id})"



class PlaylistItem(models.Model):
    playlist = models.ForeignKey(
        "Playlist",
        on_delete=models.CASCADE,
        related_name="items"
    )

    
    track = models.ForeignKey(
        "tracks.Track",
        on_delete=models.CASCADE,
        related_name="playlist_items",
        null=True,    
        blank=True       
    )

    position = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "position"],
                name="unique_playlist_position"
            )
        ]
        indexes = [
            models.Index(fields=["playlist", "position"])
        ]

    def __str__(self):
        return f"Playlist {self.playlist_id} - Track {self.track_id} @ {self.position}"