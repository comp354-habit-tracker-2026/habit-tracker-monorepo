# Generated with assistance from ChatGPT (OpenAI), adapted for project needs.

from __future__ import annotations

from typing import Optional

from mywhoosh_integration.models import SyncStatus


class SyncStatusService:
    """
    Service responsible for recording and retrieving synchronization status.
    This keeps sync-status responsibilities separate from API-fetching,
    mapping, or persistence logic.
    """

    @staticmethod
    def record_success(
        user_id: int,
        sessions_imported: int,
        duplicates_skipped: int = 0,
    ) -> SyncStatus:
        return SyncStatus.objects.create(
            user_id=user_id,
            status=SyncStatus.STATUS_SUCCESS,
            sessions_imported=sessions_imported,
            duplicates_skipped=duplicates_skipped,
            error_message=None,
        )

    @staticmethod
    def record_partial(
        user_id: int,
        sessions_imported: int,
        duplicates_skipped: int = 0,
        error_message: Optional[str] = None,
    ) -> SyncStatus:
        return SyncStatus.objects.create(
            user_id=user_id,
            status=SyncStatus.STATUS_PARTIAL,
            sessions_imported=sessions_imported,
            duplicates_skipped=duplicates_skipped,
            error_message=error_message,
        )

    @staticmethod
    def record_failure(
        user_id: int,
        error_message: str,
        sessions_imported: int = 0,
        duplicates_skipped: int = 0,
    ) -> SyncStatus:
        return SyncStatus.objects.create(
            user_id=user_id,
            status=SyncStatus.STATUS_FAILED,
            sessions_imported=sessions_imported,
            duplicates_skipped=duplicates_skipped,
            error_message=error_message,
        )

    @staticmethod
    def get_latest_for_user(user_id: int) -> Optional[SyncStatus]:
        return SyncStatus.objects.filter(user_id=user_id).first()
