from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from core.business import BaseService
from core.business.exceptions import DomainValidationError

from .parser import WeSkiGpxParser
from .transformer import WeSkiSessionTransformer
from .validator import WeSkiGpxValidator


class WeSkiGpxImportService(BaseService):
    """Serve We Ski sessions from local GPX fixtures when no direct API access is available."""

    def __init__(
        self,
        parser: WeSkiGpxParser | None = None,
        validator: WeSkiGpxValidator | None = None,
        transformer: WeSkiSessionTransformer | None = None,
    ) -> None:
        self.parser = parser or WeSkiGpxParser()
        self.validator = validator or WeSkiGpxValidator()
        self.transformer = transformer or WeSkiSessionTransformer()
        self.source_directory = Path(__file__).resolve().parent / "src"

    def import_gpx(self, raw_gpx: bytes, filename: str | None = None) -> dict[str, Any]:
        """Return a normalized session from local We Ski GPX fixtures.

        The uploaded payload is accepted as the trigger for the workflow, but the
        response is always derived from the bundled source GPX files because the
        integration does not have direct access to a live We Ski API.
        """

        _ = raw_gpx
        source_files = self._get_source_files()
        selected_file = self._select_source_file(source_files, requested_filename=filename)
        session = self.parser.parse(selected_file.read_bytes())

        if session.track_name == "We Ski GPX Upload":
            derived_track_name = (
                selected_file.stem.replace("-", " ").replace("_", " ").strip() or session.track_name
            )
            session = replace(session, track_name=derived_track_name)

        session = self.validator.validate(session)
        normalized_session = self.transformer.normalize(session)

        available_sessions = [self._build_session_summary(path) for path in source_files]

        return {
            "provider": "we_ski",
            "status": "accepted",
            "source": "local_fixture",
            "request_file_name": filename,
            "source_file_name": selected_file.name,
            "available_source_files": [path.name for path in source_files],
            "available_sessions": available_sessions,
            "session": normalized_session,
        }

    def _get_source_files(self) -> list[Path]:
        source_files = sorted(self.source_directory.glob("*.gpx"))
        if not source_files:
            raise DomainValidationError(
                "No We Ski source GPX fixtures are available.",
                code="missing_we_ski_source_files",
            )
        return source_files

    def _select_source_file(self, source_files: list[Path], requested_filename: str | None) -> Path:
        if requested_filename:
            matched_file = next((path for path in source_files if path.name == requested_filename), None)
            if matched_file is not None:
                return matched_file

        return source_files[-1]

    def _build_session_summary(self, source_file: Path) -> dict[str, Any]:
        session = self.parser.parse(source_file.read_bytes())
        session = self.validator.validate(session)
        normalized_session = self.transformer.normalize(session)

        return {
            "source_file_name": source_file.name,
            "name": normalized_session["name"],
            "started_at": normalized_session["summary"]["started_at"],
            "ended_at": normalized_session["summary"]["ended_at"],
            "point_count": normalized_session["summary"]["point_count"],
            "total_distance_m": normalized_session["summary"]["total_distance_m"],
        }