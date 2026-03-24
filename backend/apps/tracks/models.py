from django.db import models

class Track(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    bpm = models.FloatField()
    genre = models.CharField(max_length=100)
    energy = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"
