from datetime import datetime, timedelta
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# This class manages provider tokens using the database session
def _log_permission_check(user_id: int, provider_name: str, scope: str, caller_service: str, allowed: bool, reason: str):
    print({
        "timestamp": datetime.now().isoformat(),
        "caller_service": caller_service,
        "user_id": user_id,
        "provider_name": provider_name,
        "scope": scope,
        "allowed": allowed,
        "reason": reason
        # NOTE: no tokens or secrets logged here
    })

def verify_provider_token(self, user_id: int, provider_name: str, scope: str = "",
                          caller_service: str = "") -> dict:


    def _deny(reason: str) -> dict:
        result = {
            "allowed": False,
            "reason": reason,
            "user_id": user_id,
            "provider_name": provider_name
        }
        _log_permission_check(user_id, provider_name, scope, caller_service, False, reason)
        return result

    bind = self.database_session.get_bind()
    inspector = inspect(bind)

    try:
        available_tables = set(inspector.get_table_names())
    except SQLAlchemyError:
        logger.exception("Failed to inspect database schema while verifying provider token")
        return _deny("VERIFICATION_BACKEND_UNAVAILABLE")

    users_table = "users"
    consent_table = "data_integration_data_consent"

    if users_table not in available_tables:
        logger.warning(
            "Skipping user verification because table '%s' is not available on the current database connection",
            users_table
        )
        return _deny("IDENTITY_STORE_UNAVAILABLE")

    if consent_table not in available_tables:
        logger.warning(
            "Skipping consent verification because table '%s' is not available on the current database connection",
            consent_table
        )
        return _deny("CONSENT_STORE_UNAVAILABLE")

    try:
        user_columns = {column["name"] for column in inspector.get_columns(users_table)}
        consent_columns = {column["name"] for column in inspector.get_columns(consent_table)}
    except SQLAlchemyError:
        logger.exception("Failed to inspect required table columns while verifying provider token")
        return _deny("VERIFICATION_BACKEND_UNAVAILABLE")

    if "id" not in user_columns or "is_active" not in user_columns:
        logger.warning("Users table is missing required columns for token verification")
        return _deny("IDENTITY_STORE_UNAVAILABLE")

    if "user_id" not in consent_columns or "provider" not in consent_columns or "consent_granted" not in consent_columns:
        logger.warning("Consent table is missing required columns for token verification")
        return _deny("CONSENT_STORE_UNAVAILABLE")

    try:
        # --- CHECK USER IS ACTIVE (Users table) ---
        user_row = self.database_session.execute(
            text("SELECT is_active FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()

        if not user_row:
            return _deny("ACCOUNT_NOT_FOUND")

        if not user_row[0]:  # is_active is False
            return _deny("ACCOUNT_DELETED")

        # --- CHECK CONSENT TABLE (#11) ---
        consent_row = self.database_session.execute(
            text(
                "SELECT consent_granted FROM data_integration_data_consent WHERE user_id = :user_id AND provider = :provider"),
            {"user_id": user_id, "provider": provider_name}
        ).fetchone()
    except SQLAlchemyError:
        logger.exception("Database error while verifying user/consent state for provider token")
        return _deny("VERIFICATION_BACKEND_UNAVAILABLE")

    if not consent_row:
        return _deny("CONSENT_NOT_FOUND")

    if not consent_row[0]:  # consent_granted is False
        return _deny("CONSENT_REVOKED")

    # --- CHECK TOKEN TABLE (#12) ---
    token = self.database_session.query(ProviderToken).filter_by(
        user_id=user_id, provider_name=provider_name
    ).first()

    if not token or token.token_status != "ACTIVE":
        result = {"allowed": False, "reason": "NO_ACTIVE_TOKEN", "user_id": user_id, "provider_name": provider_name}
    else:
        result = {"allowed": True, "reason": "APPROVED", "user_id": user_id, "provider_name": provider_name}

    _log_permission_check(user_id, provider_name, scope, caller_service, result["allowed"], result["reason"])
    return result