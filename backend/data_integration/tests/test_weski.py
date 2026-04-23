from datetime import datetime, timezone
from unittest.mock import Mock
from io import BytesIO

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from data_integration.business.weski_gpx_parser import WeskiGpxParser
from data_integration.business.weski_session_summary import WeskiSessionSummary
from data_integration.data.weski import WeskiGpxService


# This file keeps the GPX fixtures inline so each test can show the specific
# parser edge case it is asserting without jumping between helper files.

# ---------------------------------------------------------------------------
# Sample GPX content for tests
# ---------------------------------------------------------------------------

SAMPLE_GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <name>Morning Ski Session</name>
    <trkseg>
      <trkpt lat="45.5000" lon="-73.5000">
        <ele>800.0</ele>
        <speed>0.5</speed>
        <time>2026-01-25T11:00:00Z</time>
      </trkpt>
      <trkpt lat="45.5010" lon="-73.5010">
        <ele>790.0</ele>
        <speed>5.0</speed>
        <time>2026-01-25T11:00:10Z</time>
      </trkpt>
      <trkpt lat="45.5020" lon="-73.5020">
        <ele>780.0</ele>
        <speed>6.0</speed>
        <time>2026-01-25T11:00:20Z</time>
      </trkpt>
      <trkpt lat="45.5030" lon="-73.5030">
        <ele>770.0</ele>
        <speed>4.0</speed>
        <time>2026-01-25T11:00:30Z</time>
      </trkpt>
      <trkpt lat="45.5040" lon="-73.5040">
        <ele>785.0</ele>
        <speed>1.0</speed>
        <time>2026-01-25T11:00:40Z</time>
      </trkpt>
      <trkpt lat="45.5050" lon="-73.5050">
        <ele>810.0</ele>
        <speed>0.3</speed>
        <time>2026-01-25T11:00:50Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

SAMPLE_GPX_BYTES = SAMPLE_GPX.encode("utf-8")

SAMPLE_GPX_BOM = b"\xef\xbb\xbf" + SAMPLE_GPX_BYTES

EMPTY_GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <name>Empty Session</name>
    <trkseg>
    </trkseg>
  </trk>
</gpx>
"""

# GPX with missing coords to exercise interpolation
GPX_MISSING_COORDS = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="45.5000" lon="-73.5000">
        <ele>800.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:00Z</time>
      </trkpt>
      <trkpt>
        <ele>795.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:05Z</time>
      </trkpt>
      <trkpt lat="45.5010" lon="-73.5010">
        <ele>790.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:10Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

# GPX with out-of-range coords
GPX_BAD_COORDS = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="999.0" lon="-73.5000">
        <ele>800.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

# GPX with a spike (point far from neighbors, neighbors close together)
GPX_WITH_SPIKE = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="45.5000" lon="-73.5000">
        <ele>800.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:00Z</time>
      </trkpt>
      <trkpt lat="46.5000" lon="-74.5000">
        <ele>800.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:05Z</time>
      </trkpt>
      <trkpt lat="45.5001" lon="-73.5001">
        <ele>800.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:10Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

# GPX with missing time on a point (no interpolation possible)
GPX_NO_TIME = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="45.5000" lon="-73.5000">
        <ele>800.0</ele>
        <speed>3.0</speed>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

# GPX where points have a large time gap (>60s default) so interpolation skips
GPX_LARGE_GAP = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="45.5000" lon="-73.5000">
        <ele>800.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:00:00Z</time>
      </trkpt>
      <trkpt>
        <ele>795.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:05:00Z</time>
      </trkpt>
      <trkpt lat="45.5010" lon="-73.5010">
        <ele>790.0</ele>
        <speed>3.0</speed>
        <time>2026-01-25T11:10:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

# GPX with a run (descending with speed) followed by a lift (ascending)
GPX_RUN_AND_LIFT = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
  <trk>
    <name>Run and Lift</name>
    <trkseg>
      <trkpt lat="45.5000" lon="-73.5000">
        <ele>900.0</ele>
        <speed>1.0</speed>
        <time>2026-01-25T11:00:00Z</time>
      </trkpt>
      <trkpt lat="45.5010" lon="-73.5010">
        <ele>888.0</ele>
        <speed>8.0</speed>
        <time>2026-01-25T11:00:10Z</time>
      </trkpt>
      <trkpt lat="45.5020" lon="-73.5020">
        <ele>875.0</ele>
        <speed>10.0</speed>
        <time>2026-01-25T11:00:20Z</time>
      </trkpt>
      <trkpt lat="45.5030" lon="-73.5030">
        <ele>860.0</ele>
        <speed>9.0</speed>
        <time>2026-01-25T11:00:30Z</time>
      </trkpt>
      <trkpt lat="45.5040" lon="-73.5040">
        <ele>870.0</ele>
        <speed>2.0</speed>
        <time>2026-01-25T11:00:40Z</time>
      </trkpt>
      <trkpt lat="45.5050" lon="-73.5050">
        <ele>900.0</ele>
        <speed>2.0</speed>
        <time>2026-01-25T11:00:50Z</time>
      </trkpt>
      <trkpt lat="45.5060" lon="-73.5060">
        <ele>888.0</ele>
        <speed>8.0</speed>
        <time>2026-01-25T11:01:00Z</time>
      </trkpt>
      <trkpt lat="45.5070" lon="-73.5070">
        <ele>870.0</ele>
        <speed>9.0</speed>
        <time>2026-01-25T11:01:10Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

# Bytes that cannot be decoded as UTF-8. The parser accepts raw bytes, so this
# fixture exercises the decode step before XML parsing even begins.
INVALID_UTF8_BYTES = b"\xff\xfe\xfa\xfb"


# ===================================================================
# WeskiGpxParser tests
# ===================================================================


class TestWeskiGpxParser:

  # High-level parser entry points -------------------------------------------------

    def test_parse_string_returns_session_summary(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX)
        assert isinstance(summary, WeskiSessionSummary)
        assert summary.track_name == "Morning Ski Session"
        assert summary.external_id.startswith("weski-")

    def test_parse_bytes_returns_session_summary(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX_BYTES)
        assert isinstance(summary, WeskiSessionSummary)
        assert summary.track_name == "Morning Ski Session"

    def test_parse_bytes_with_bom(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX_BOM)
        assert isinstance(summary, WeskiSessionSummary)
        assert summary.track_name == "Morning Ski Session"

    def test_parse_empty_gpx_returns_zero_metrics(self):
        summary = WeskiGpxParser.parse(EMPTY_GPX)
        assert summary.total_distance_km == 0.0
        assert summary.total_elevation_gain_meters == 0.0
        assert summary.number_of_runs == 0
        assert summary.total_time_seconds == 0.0
        assert summary.average_speed_kmh == 0.0
        assert summary.max_speed_kmh == 0.0
        assert summary.start_time is None

    def test_parse_calculates_distance(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX)
        assert summary.total_distance_km > 0

    def test_parse_calculates_elevation_gain(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX)
        assert summary.total_elevation_gain_meters > 0

    def test_parse_calculates_speed(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX)
        assert summary.max_speed_kmh > 0
        assert summary.average_speed_kmh > 0

    def test_parse_calculates_time(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX)
        assert summary.total_time_seconds == 50.0
        assert summary.start_time == datetime(2026, 1, 25, 11, 0, 0, tzinfo=timezone.utc)

    def test_same_content_produces_same_external_id(self):
        s1 = WeskiGpxParser.parse(SAMPLE_GPX)
        s2 = WeskiGpxParser.parse(SAMPLE_GPX)
        assert s1.external_id == s2.external_id

    def test_different_content_produces_different_external_id(self):
        s1 = WeskiGpxParser.parse(SAMPLE_GPX)
        s2 = WeskiGpxParser.parse(EMPTY_GPX)
        assert s1.external_id != s2.external_id

    def test_parse_interpolates_missing_coords(self):
        summary = WeskiGpxParser.parse(GPX_MISSING_COORDS)
        assert summary.total_distance_km > 0

    def test_parse_skips_out_of_range_coords(self):
        summary = WeskiGpxParser.parse(GPX_BAD_COORDS)
        assert summary.total_distance_km == 0.0

    def test_parse_handles_spike_detection(self):
        summary = WeskiGpxParser.parse(GPX_WITH_SPIKE)
        assert summary.total_distance_km < 1.0

    def test_parse_handles_missing_time(self):
        summary = WeskiGpxParser.parse(GPX_NO_TIME)
        assert summary.total_time_seconds == 0.0

    def test_parse_skips_interpolation_for_large_gap(self):
        summary = WeskiGpxParser.parse(GPX_LARGE_GAP)
        assert summary.total_distance_km >= 0

    def test_parse_counts_runs(self):
        summary = WeskiGpxParser.parse(GPX_RUN_AND_LIFT)
        assert summary.number_of_runs >= 1

    def test_parse_detects_second_run_after_lift(self):
        summary = WeskiGpxParser.parse(GPX_RUN_AND_LIFT)
        assert summary.number_of_runs >= 2

    def test_parse_raw_data_included(self):
        summary = WeskiGpxParser.parse(SAMPLE_GPX)
        assert isinstance(summary.raw_data, dict)
        assert "track_name" in summary.raw_data

    def test_parse_returns_expected_summary_output(self):
      summary = WeskiGpxParser.parse(SAMPLE_GPX)

      assert summary.track_name == "Morning Ski Session"
      assert summary.start_time == datetime(2026, 1, 25, 11, 0, 0, tzinfo=timezone.utc)
      assert summary.total_time_seconds == 50.0
      assert summary.number_of_runs == 1
      assert summary.total_distance_km == pytest.approx(0.68, rel=0.05)
      assert summary.total_elevation_gain_meters == pytest.approx(40.0)
      assert summary.average_speed_kmh == pytest.approx(11.736)
      assert summary.max_speed_kmh == pytest.approx(21.6)
      assert summary.raw_data == {
        "track_name": "Morning Ski Session",
        "start_time": datetime(2026, 1, 25, 11, 0, 0, tzinfo=timezone.utc),
        "total_elevation_gain_meters": pytest.approx(40.0),
        "total_distance_km": pytest.approx(0.68, rel=0.05),
        "number_of_runs": 1,
        "total_time_seconds": 50.0,
            "average_speed_kmh": pytest.approx(11.736),
        "max_speed_kmh": pytest.approx(21.6),
      }

    def test_parse_file(self, tmp_path):
        gpx_file = tmp_path / "test.gpx"
        gpx_file.write_text(SAMPLE_GPX, encoding="utf-8")
        summary = WeskiGpxParser.parse_file(str(gpx_file))
        assert isinstance(summary, WeskiSessionSummary)
        assert summary.track_name == "Morning Ski Session"

    def test_parse_invalid_xml_raises(self):
        with pytest.raises(Exception):
            WeskiGpxParser.parse("this is not xml")

    def test_parse_invalid_utf8_bytes_raises(self):
      with pytest.raises(UnicodeDecodeError):
        WeskiGpxParser.parse(INVALID_UTF8_BYTES)

    def test_parse_file_missing_path_raises(self):
      with pytest.raises(FileNotFoundError):
        WeskiGpxParser.parse_file("missing-session.gpx")

    # Helper method tests ------------------------------------------------------------
    def test_float_or_none_returns_float(self):
        assert WeskiGpxParser._float_or_none("3.14") == pytest.approx(3.14)

    def test_float_or_none_returns_none_for_none(self):
        assert WeskiGpxParser._float_or_none(None) is None

    def test_float_or_none_returns_none_for_empty(self):
        assert WeskiGpxParser._float_or_none("") is None

    def test_float_or_none_returns_none_for_invalid(self):
        assert WeskiGpxParser._float_or_none("abc") is None

    def test_dt_or_none_returns_datetime(self):
        dt = WeskiGpxParser._dt_or_none("2026-01-25T11:00:00Z")
        assert dt == datetime(2026, 1, 25, 11, 0, 0, tzinfo=timezone.utc)

    def test_dt_or_none_returns_none_for_none(self):
        assert WeskiGpxParser._dt_or_none(None) is None

    def test_dt_or_none_returns_none_for_empty(self):
        assert WeskiGpxParser._dt_or_none("") is None

    def test_dt_or_none_returns_none_for_invalid(self):
        assert WeskiGpxParser._dt_or_none("not-a-date") is None

    def test_text_or_none_returns_none_for_none(self):
        assert WeskiGpxParser._text_or_none(None) is None

    def test_distance_m_same_point_is_zero(self):
        assert WeskiGpxParser._distance_m(45.0, -73.0, 45.0, -73.0) == 0.0

    def test_distance_m_known_distance(self):
        # Roughly 111 km per degree of latitude
        d = WeskiGpxParser._distance_m(45.0, -73.0, 46.0, -73.0)
        assert 110_000 < d < 112_000


# ===================================================================
# WeskiGpxService tests
# ===================================================================


class TestWeskiGpxService:

    def test_default_parser(self):
        service = WeskiGpxService()
        assert service.parser is WeskiGpxParser

    def test_custom_parser(self):
        mock_parser = Mock()
        service = WeskiGpxService(parser=mock_parser)
        assert service.parser is mock_parser

    def test_parse_gpx_delegates_to_parser(self):
        mock_parser = Mock()
        expected = Mock(spec=WeskiSessionSummary)
        mock_parser.parse.return_value = expected

        service = WeskiGpxService(parser=mock_parser)
        result = service.parse_gpx(SAMPLE_GPX)

        mock_parser.parse.assert_called_once_with(SAMPLE_GPX)
        assert result is expected

    def test_parse_gpx_with_bytes(self):
        service = WeskiGpxService()
        summary = service.parse_gpx(SAMPLE_GPX_BYTES)
        assert isinstance(summary, WeskiSessionSummary)


# ===================================================================
# WeskiUploadViewSet tests
# ===================================================================


@pytest.mark.django_db
class TestWeskiUploadView:

    def _make_gpx_file(self, content=SAMPLE_GPX_BYTES, name="session.gpx"):
    # BytesIO matches DRF's expected uploaded-file interface closely enough
    # for view tests without needing to hit the filesystem.
        f = BytesIO(content)
        f.name = name
        return f

    def _get_authed_client(self):
    # Keep auth setup local to the test class so each test remains explicit
    # about whether it is exercising authenticated or anonymous behavior.
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username="skitest", password="pass1234")
        client = APIClient()
        client.force_authenticate(user=user)
        return client, user

    def test_upload_requires_authentication(self):
        client = APIClient()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file()},
            format="multipart",
        )
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_upload_requires_file(self):
        client, _ = self._get_authed_client()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {},
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "file" in response.data["error"].lower() or "GPX" in response.data["error"]

    def test_upload_rejects_non_gpx(self):
        client, _ = self._get_authed_client()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file(name="data.txt")},
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "gpx" in response.data["error"].lower()

    def test_upload_success(self):
        client, _ = self._get_authed_client()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file()},
            format="multipart",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["activity_type"] == "skiing"
        assert response.data["provider"] == "weski"
        assert "id" in response.data
        assert "distance_km" in response.data
        assert "number_of_runs" in response.data

    def test_upload_success_returns_expected_output_values(self):
        client, _ = self._get_authed_client()
        expected_summary = WeskiGpxParser.parse(SAMPLE_GPX_BYTES)

        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file()},
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {
            "id": response.data["id"],
            "activity_type": "skiing",
            "date": "2026-01-25",
            "duration_minutes": 0,
            "distance_km": pytest.approx(round(expected_summary.total_distance_km, 2)),
            "provider": "weski",
            "external_id": expected_summary.external_id,
            "track_name": expected_summary.track_name,
            "number_of_runs": expected_summary.number_of_runs,
            "total_elevation_gain_meters": pytest.approx(expected_summary.total_elevation_gain_meters),
            "average_speed_kmh": pytest.approx(expected_summary.average_speed_kmh),
            "max_speed_kmh": pytest.approx(expected_summary.max_speed_kmh),
        }

    def test_upload_duplicate_returns_conflict(self):
        client, _ = self._get_authed_client()
        gpx = SAMPLE_GPX_BYTES
        # First upload
        client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file(gpx)},
            format="multipart",
        )
        # Second upload with same content
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file(gpx)},
            format="multipart",
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data == {"error": "This GPX session has already been uploaded."}

    def test_upload_invalid_gpx_returns_400(self):
        client, _ = self._get_authed_client()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file(b"not xml at all")},
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parse" in response.data["error"].lower() or "GPX" in response.data["error"]

    def test_upload_empty_gpx_returns_400(self):
        client, _ = self._get_authed_client()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file(b"")},
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parse" in response.data["error"].lower() or "GPX" in response.data["error"]

    def test_upload_invalid_utf8_gpx_returns_400(self):
        client, _ = self._get_authed_client()
        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file(INVALID_UTF8_BYTES)},
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parse" in response.data["error"].lower() or "GPX" in response.data["error"]

    def test_upload_creates_activity_record(self):
        from activities.models import Activity
        client, user = self._get_authed_client()
        client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file()},
            format="multipart",
        )
        activity = Activity.objects.get(provider="weski", user=user)
        assert activity.activity_type == "skiing"
        assert activity.distance > 0
        assert activity.raw_data is not None
        assert "number_of_runs" in activity.raw_data

    def test_upload_activity_record_matches_summary_output(self):
        from activities.models import Activity

        client, user = self._get_authed_client()
        expected_summary = WeskiGpxParser.parse(SAMPLE_GPX_BYTES)

        response = client.post(
            "/api/v1/data-integrations/weski/upload/",
            {"file": self._make_gpx_file()},
            format="multipart",
        )

        activity = Activity.objects.get(provider="weski", user=user)
        assert response.status_code == status.HTTP_201_CREATED
        assert activity.external_id == expected_summary.external_id
        assert activity.activity_type == "skiing"
        assert float(activity.distance) == pytest.approx(round(expected_summary.total_distance_km, 2))
        assert activity.raw_data == {
          "track_name": expected_summary.track_name,
          "total_elevation_gain_meters": pytest.approx(expected_summary.total_elevation_gain_meters),
          "number_of_runs": expected_summary.number_of_runs,
          "total_time_seconds": expected_summary.total_time_seconds,
          "average_speed_kmh": pytest.approx(expected_summary.average_speed_kmh),
          "max_speed_kmh": pytest.approx(expected_summary.max_speed_kmh),
        }
