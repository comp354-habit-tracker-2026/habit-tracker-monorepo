from datetime import date, datetime
from mywhoosh_types import NormalizedSession, Metrics, DataQuality


def map_mywhoosh_session(raw: dict) -> NormalizedSession:
    raw_date = raw.get("date")

    if isinstance(raw_date, date):
        session_date = raw_date
    elif isinstance(raw_date, str):
        try:
            session_date = datetime.fromisoformat(raw_date).date()
        except ValueError:
            session_date = date.today()
    else:
        session_date = date.today()

    distance = raw.get("distance")
    calories = raw.get("calories")
    duration = raw.get("duration")

    if distance is not None and distance < 0:
        distance = None
    if calories is not None and calories < 0:
        calories = None
    if duration is not None and duration < 0:
        duration = None

    metrics = Metrics(
        distance=distance,
        calories=calories,
        duration=duration,
    )

    has_missing_value = (
    distance is None
    or calories is None
    or duration is None
    )

    data_quality = DataQuality(
        has_missing_value=has_missing_value
    )

    session = NormalizedSession(
        activity_type=raw.get("activity_type", "cycling"),
        date=session_date,
        external_id=raw.get("session_id"),
        metrics=metrics,
        data_quality=data_quality,
        raw_data=raw,
    )

    return session
