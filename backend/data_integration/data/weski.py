from __future__ import annotations

from data_integration.business.weski_gpx_parser import WeskiGpxParser
from data_integration.business.weski_session_summary import WeskiSessionSummary


class WeskiGpxService:
    """Adapter for parsing weSki GPX uploads into session summaries."""

    def __init__(self, parser: type[WeskiGpxParser] | None = None):
        self.parser = parser or WeskiGpxParser

    def parse_gpx(self, gpx_content: str | bytes) -> WeskiSessionSummary:
        return self.parser.parse(gpx_content)
