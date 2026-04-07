# ChatGPT was used to generate some of the following code.
from __future__ import annotations
from typing import Iterable
from mywhoosh_integration.models import SessionRecord


class SessionPersistenceService:
    """
    Service responsible for storing normalized MyWhoosh sessions
    while preventing duplicate entries.
    """

    @staticmethod
    def import_sessions(gituser_id: int, sessions: Iterable[object]) -> dict[str, int]:
        sessions_imported = 0
        duplicates_skipped = 0

        for session in sessions:
            if SessionPersistenceService._is_duplicate(user_id, session):
                duplicates_skipped += 1
                continue

            metrics = getattr(session, "metrics", None)
            data_quality = getattr(session, "data_quality", None)

            SessionRecord.objects.create(
                user_id=user_id,
                provider=session.provider,
                external_session_id=getattr(session, "external_session_id", None),
                started_at=session.started_at,
                duration_seconds=session.duration_seconds,
                title=getattr(session, "title", None),
                session_type=getattr(session, "session_type", None),
                distance_meters=getattr(metrics, "distance_meters", None),
                calories=getattr(metrics, "calories", None),
                average_power_watts=getattr(metrics, "average_power_watts", None),
                average_cadence_rpm=getattr(metrics, "average_cadence_rpm", None),
                average_heart_rate=getattr(metrics, "average_heart_rate", None),
                data_quality_status=getattr(data_quality, "status", "complete"),
            )
            sessions_imported += 1

        return {
            "sessions_imported": sessions_imported,
            "duplicates_skipped": duplicates_skipped,
        }

    @staticmethod
    def _is_duplicate(user_id: int, session: object) -> bool:
        external_session_id = getattr(session, "external_session_id", None)

        if external_session_id:
            return SessionRecord.objects.filter(
                provider=session.provider,
                external_session_id=external_session_id,
            ).exists()

        return SessionRecord.objects.filter(
            user_id=user_id,
            started_at=session.started_at,
            duration_seconds=session.duration_seconds,
        ).exists()