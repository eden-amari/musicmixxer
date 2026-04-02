import hashlib

def generate_track_key(data):
    title = (data.get("title") or "").strip().lower()
    artist = (data.get("artist") or "").strip().lower()

    return f"{title}:{artist}"