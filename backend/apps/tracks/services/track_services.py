from apps.tracks.models import Track

class TrackService:

    @staticmethod
    def create_track(title, artist, bpm, genre, energy = None):
        if not title:
            raise ValueError("Title is required")
        if not artist:
            raise ValueError("Artist is required.")
        if not bpm:
            raise ValueError("BPM is required.")
        if not genre:
            raise ValueError("Genre is required.")
        return Track.objects.create(
            title = title,
            artist = artist,
            bpm = bpm,
            genre = genre,
            energy = genre
        )
    
    @staticmethod
    def fetch_track(track_id):
        return Track.objects.get(id = track_id)
    
    @staticmethod
    def bulk_fetch(track_ids):
        return Track.objects.filter(id__in = track_ids)
    
    @staticmethod
    def search_tracks(query):
        return Track.objects.filter(title__icontains=query) | \
               Track.objects.filter(artist__icontains=query)