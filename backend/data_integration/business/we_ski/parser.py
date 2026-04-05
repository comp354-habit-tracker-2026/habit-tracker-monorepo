from __future__ import annotations

from datetime import datetime
import re
import xml.etree.ElementTree as ET

from core.business.exceptions import DomainValidationError

from .domain import ParsedSession, TrackPoint


class WeSkiGpxParser:
    """Parse GPX payloads exported by We Ski into domain objects."""

    def parse(self, raw_gpx: bytes) -> ParsedSession:
        try:
            root = ET.fromstring(raw_gpx)
        except ET.ParseError as exc:
            raise DomainValidationError(
                "Uploaded file is not valid GPX XML.",
                code="invalid_gpx_xml",
            ) from exc

        namespace = self._extract_namespace(root.tag)
        track_node = root.find(self._qualify("trk", namespace))
        if track_node is None:
            raise DomainValidationError(
                "GPX document does not contain a track.",
                code="missing_track",
            )

        name = self._read_text(track_node.find(self._qualify("name", namespace)))
        points = self._parse_points(track_node, namespace)

        if not points:
            raise DomainValidationError(
                "GPX document does not contain any track points.",
                code="missing_track_points",
            )

        started_at = next((point.time for point in points if point.time), None)
        ended_at = next(
            (point.time for point in reversed(points) if point.time),
            None,
        )
        bounds = self._calculate_bounds(points)

        return ParsedSession(
            start_time=started_at,
            end_time=ended_at,
            points=points,
            bounds=bounds,
            track_name=name or "We Ski GPX Upload",
        )

    def _parse_points(self, track_node: ET.Element, namespace: str) -> list[TrackPoint]:
        points: list[TrackPoint] = []
        for segment_node in track_node.findall(self._qualify("trkseg", namespace)):
            for point_node in segment_node.findall(self._qualify("trkpt", namespace)):
                try:
                    latitude = float(point_node.attrib["lat"])
                    longitude = float(point_node.attrib["lon"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise DomainValidationError(
                        "Each GPX track point must include valid latitude and longitude coordinates.",
                        code="invalid_coordinates",
                    ) from exc

                elevation_node = point_node.find(self._qualify("ele", namespace))
                time_node = point_node.find(self._qualify("time", namespace))
                speed_node = point_node.find(self._qualify("speed", namespace))
                points.append(
                    TrackPoint(
                        time=self._parse_datetime(self._read_text(time_node)),
                        lat=latitude,
                        lon=longitude,
                        ele=self._parse_float(self._read_text(elevation_node)),
                        speed_mps=self._parse_float(self._read_text(speed_node)),
                    )
                )

        return points

    @staticmethod
    def _extract_namespace(tag_name: str) -> str:
        match = re.match(r"\{(?P<namespace>.+)\}", tag_name)
        return match.group("namespace") if match else ""

    @staticmethod
    def _qualify(tag_name: str, namespace: str) -> str:
        return f"{{{namespace}}}{tag_name}" if namespace else tag_name

    @staticmethod
    def _read_text(node: ET.Element | None) -> str | None:
        if node is None or node.text is None:
            return None
        value = node.text.strip()
        return value or None

    @staticmethod
    def _parse_float(value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _calculate_bounds(points: list[TrackPoint]) -> tuple[float, float, float, float] | None:
        coordinates = [
            (point.lat, point.lon)
            for point in points
            if point.lat is not None and point.lon is not None
        ]
        if not coordinates:
            return None

        latitudes = [lat for lat, _ in coordinates]
        longitudes = [lon for _, lon in coordinates]
        return (min(latitudes), min(longitudes), max(latitudes), max(longitudes))