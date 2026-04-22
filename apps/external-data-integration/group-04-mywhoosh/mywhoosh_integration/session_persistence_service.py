# ChatGPT was used to generate some of the following code.
from __future__ import annotations
from typing import Iterable
from datetime import datetime, time
from mywhoosh_integration.models import SessionRecord


class SessionPersistenceService:
    @staticmethod
    def import_sessions(user_id: int, sessions: Iterable[object]) -> dict[str, int]:
        sessions_imported = 0
        duplicates_skipped = 0

        for session in sessions:
            if SessionPersistenceService._is_duplicate(user_id, session):
                duplicates_skipped += 1
                continue

            metrics = getattr(session, "metrics", None)
            data_quality = getattr(session, "data_quality", None)
            started_at = datetime.combine(session.date, time.min)

            SessionRecord.objects.create(
                user_id=user_id,
                provider=session.provider,
                external_session_id=getattr(session, "external_id", None),
                started_at=started_at,
                duration_seconds=getattr(metrics, "duration", None),
                title=getattr(session, "activity_type", None),
                session_type=getattr(session, "activity_type", None),
                distance_meters=getattr(metrics, "distance", None),
                calories=getattr(metrics, "calories", None),
                data_quality_status="missing_values" if getattr(data_quality, "has_missing_value", False) else "complete",
            )
            sessions_imported += 1

        return {
            "sessions_imported": sessions_imported,
            "duplicates_skipped": duplicates_skipped,
        }

    @staticmethod
    def _is_duplicate(user_id: int, session: object) -> bool:
        external_id = getattr(session, "external_id", None)

        if external_id:
            return SessionRecord.objects.filter(
                provider=session.provider,
                external_session_id=external_id,
            ).exists()

        metrics = getattr(session, "metrics", None)
        started_at = datetime.combine(session.date, time.min)

        return SessionRecord.objects.filter(
            user_id=user_id,
            started_at=started_at,
            duration_seconds=getattr(metrics, "duration", None),
        ).exists()