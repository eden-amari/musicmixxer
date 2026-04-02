from typing import Dict, List, Tuple

from apps.tracks.services.enrichment_service import EnrichmentService
from apps.tracks.services.track_services import TrackService
from apps.tracks.services.resolver import TrackResolver

from apps.imports.domain.parsers.csv_parser import CSVParser
from apps.imports.domain.parsers.json_parser import JSONParser
from apps.imports.domain.parsers.spotify_parser import SpotifyParser

from apps.imports.domain.normalizer import Normalizer
from apps.imports.domain.validator import validate_track


class ImportService:
    """
    Orchestrates the full ingestion pipeline.

    FINAL PIPELINE:
        Parser → Normalize → Validate → Resolve → Enrich → Persist

    Design Principles:
    - Fail-safe (never break pipeline)
    - Batch processing for performance
    - Structured error reporting
    """

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
        batch_size: int = 50
    ) -> Dict:

        if file_type not in cls.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {file_type}")

        parser = cls._get_parser(file, file_type)

        return cls._run_pipeline(parser, access_token, batch_size)

    # =========================================================
    # SPOTIFY INGESTION
    # =========================================================
    @classmethod
    def import_spotify_playlist(
        cls,
        items,
        access_token: str,
        batch_size: int = 50
    ):
        parser = SpotifyParser.parse(items)
        return cls._run_pipeline(parser, access_token, batch_size)

    # =========================================================
    # CORE PIPELINE
    # =========================================================
    @classmethod
    def _run_pipeline(cls, parser, access_token: str, batch_size: int):

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
                # --------------------
                # NORMALIZE
                # --------------------
                normalized = Normalizer.normalize(raw_data)

                # --------------------
                # VALIDATE
                # --------------------
                validation_error = validate_track(normalized)
                if validation_error:
                    failed += 1
                    errors.append(cls._error(idx, "validation_error", validation_error))
                    continue

                buffer.append((idx, normalized))

                # --------------------
                # BATCH PROCESS
                # --------------------
                if len(buffer) >= batch_size:
                    s, f, d, e = cls._process_batch(buffer, access_token)
                    success += s
                    failed += f
                    duplicates += d
                    errors.extend(e)
                    buffer.clear()

            except Exception as e:
                failed += 1
                errors.append(cls._error(idx, "unexpected_error", str(e)))

        # process remaining
        if buffer:
            s, f, d, e = cls._process_batch(buffer, access_token)
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
    # BATCH PROCESSING (UPDATED 🔥)
    # =========================================================
    @classmethod
    def _process_batch(cls, batch, access_token):

        success, failed, duplicates = 0, 0, 0
        errors: List[Dict] = []

        for row_index, data in batch:
            try:
                # --------------------
                # RESOLVE
                # --------------------
                try:
                    resolved = TrackResolver.resolve(data, access_token) or data
                except Exception:
                    resolved = data

                # --------------------
                # ENRICHMENT
                # --------------------
                try:
                    enriched = EnrichmentService.enrich(resolved, access_token) or resolved
                except Exception:
                    enriched = resolved

                # --------------------
                # STORE
                # --------------------
                track, created = TrackService.create_safe(enriched)

                if created:
                    success += 1
                else:
                    duplicates += 1

            except Exception as e:
                failed += 1
                errors.append(cls._error(row_index, "processing_error", str(e)))

        return success, failed, duplicates, errors

    # =========================================================
    # PARSER FACTORY
    # =========================================================
    @staticmethod
    def _get_parser(file, file_type: str):

        if file_type == "csv":
            return CSVParser.parse(file)

        if file_type == "json":
            return JSONParser.parse(file)

        raise ValueError("Invalid parser type")

    # =========================================================
    # ERROR FORMATTER
    # =========================================================
    @staticmethod
    def _error(row: int, error_type: str, message: str) -> Dict:
        return {
            "row": row,
            "type": error_type,
            "message": message,
        }