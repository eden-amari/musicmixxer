from typing import Dict, List, Tuple
from django.db import transaction

from apps.tracks.services.enrichment_service import EnrichmentService
from apps.tracks.services.track_services import TrackService
from apps.tracks.services.resolver import TrackResolver

from apps.imports.domain.parsers.csv_parser import CSVParser
from apps.imports.domain.parsers.json_parser import JSONParser

from apps.imports.domain.normalizer import Normalizer
from apps.imports.domain.validator import validate_track

from apps.playlists.services.playlist_service import PlaylistService
from apps.playlists.services.playlist_item_service import PlaylistItemService


class ImportService:

    SUPPORTED_TYPES = {"csv", "json"}

    # =========================================================
    # FILE INGESTION
    # =========================================================
    @classmethod
    def import_file(
        cls,
        file,
        file_type: str,
        access_token: str,
        user,
        playlist_id: int = None,
        batch_size: int = 50
    ) -> Dict:

        if file_type not in cls.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {file_type}")

        parser = cls._get_parser(file, file_type)

        # 🔥 PLAYLIST HANDLING
        if playlist_id:
            playlist = PlaylistService.get_playlist(playlist_id, user)
        else:
            playlist = PlaylistService.create_playlist(
                user=user,
                title="Imported Playlist",
                description="Created from file import"
            )

        result = cls._run_pipeline(parser, access_token, playlist, batch_size)

        return {
            "playlist_id": playlist.id,
            **result
        }

    # =========================================================
    # CORE PIPELINE
    # =========================================================
    @classmethod
    @transaction.atomic
    def _run_pipeline(cls, parser, access_token: str, playlist, batch_size: int):

        total, success, failed, duplicates = 0, 0, 0, 0
        errors: List[Dict] = []

        buffer: List[Tuple[int, Dict]] = []

        for idx, (raw_data, parse_error) in enumerate(parser):
            total += 1

            if parse_error:
                failed += 1
                errors.append(cls._error(idx, "parse_error", parse_error))
                continue

            try:
                normalized = Normalizer.normalize(raw_data)

                validation_error = validate_track(normalized)
                if validation_error:
                    failed += 1
                    errors.append(cls._error(idx, "validation_error", validation_error))
                    continue

                buffer.append((idx, normalized))

                if len(buffer) >= batch_size:
                    s, f, d, e = cls._process_batch(buffer, access_token, playlist)
                    success += s
                    failed += f
                    duplicates += d
                    errors.extend(e)
                    buffer.clear()

            except Exception as e:
                failed += 1
                errors.append(cls._error(idx, "unexpected_error", str(e)))

        if buffer:
            s, f, d, e = cls._process_batch(buffer, access_token, playlist)
            success += s
            failed += f
            duplicates += d
            errors.extend(e)

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "duplicates": duplicates,
            "errors": errors[:50],
        }

    # =========================================================
    # 🔥 BATCH PROCESSING + PLAYLIST ATTACH
    # =========================================================
    @classmethod
    def _process_batch(cls, batch, access_token, playlist):

        success, failed, duplicates = 0, 0, 0
        errors: List[Dict] = []

        # 🔥 IMPORTANT: handle existing playlist size
        existing_count = PlaylistItemService.get_playlist_length(playlist.id)

        for i, (row_index, data) in enumerate(batch):
            try:
                # --------------------
                # RESOLVE
                # --------------------
                try:
                    resolved = TrackResolver.resolve(data, access_token) or data
                except Exception:
                    resolved = data

                spotify_id = resolved.get("spotify_id")

                # --------------------
                # DEDUPE
                # --------------------
                if spotify_id:
                    existing = TrackService.get_by_spotify_id(spotify_id)

                    if existing:
                        track_obj = existing
                        duplicates += 1
                    else:
                        enriched = cls._maybe_enrich(resolved, access_token)
                        track_obj, created = TrackService.create_safe(enriched)

                        if created:
                            success += 1
                        else:
                            duplicates += 1
                else:
                    enriched = cls._maybe_enrich(resolved, access_token)
                    track_obj, created = TrackService.create_safe(enriched)

                    if created:
                        success += 1
                    else:
                        duplicates += 1

                # 🔥 ATTACH TO PLAYLIST
                PlaylistItemService.add_song_to_playlist(
                    playlist_id=playlist.id,
                    track_id=track_obj.id,
                    user=playlist.user,
                    position=existing_count + i + 1  # 🔥 IMPORTANT (1-based index)
                )

            except Exception as e:
                failed += 1
                errors.append(cls._error(row_index, "processing_error", str(e)))

        return success, failed, duplicates, errors

    # =========================================================
    # HELPERS
    # =========================================================
    @staticmethod
    def _maybe_enrich(data, access_token):
        if not (data.get("bpm") and data.get("energy")):
            try:
                return EnrichmentService.enrich(data, access_token) or data
            except Exception:
                return data
        return data

    @staticmethod
    def _get_parser(file, file_type: str):
        if file_type == "csv":
            return CSVParser.parse(file)
        if file_type == "json":
            return JSONParser.parse(file)
        raise ValueError("Invalid parser type")

    @staticmethod
    def _error(row: int, error_type: str, message: str) -> Dict:
        return {
            "row": row,
            "type": error_type,
            "message": message,
        }