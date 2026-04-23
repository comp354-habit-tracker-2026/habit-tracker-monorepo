
import logging

logger = logging.getLogger(__name__)


def handle_activity_imported(payload):
    logger.info("Handling activity.imported for activity_id=%s", payload.get("activity_id"))
    print(f"[HANDLER] activity.imported -> {payload}")
    return {"status": "ok", "event": "activity.imported"}


def handle_activity_updated(payload):
    logger.info("Handling activity.updated for activity_id=%s", payload.get("activity_id"))
    print(f"[HANDLER] activity.updated -> {payload}")
    return {"status": "ok", "event": "activity.updated"}


EVENT_HANDLERS = {
    "activity.imported": handle_activity_imported,
    "activity.updated": handle_activity_updated,
}
