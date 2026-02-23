from datetime import datetime
from typing import Optional, List, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET


from models import TrackPoint, ParsedSession

NS = {"gpx":"http://www.topografix.com/GPX/1/1"}
def parse_gpx(gpx_path: str | Path) -> ParsedSession:

    gpx_path = Path(gpx_path)

    # utf-8-sig removes BOM if present
    xml_text = gpx_path.read_text(encoding='utf-8-sig')
    root = ET.fromstring(xml_text)

    track_name = _text_or_none(root.find("gpx:trk/gpx:name",NS))

    points: List[TrackPoint] = []

    for trkpt in root.findall(".//gpx:trkpt", NS):
        lat = _float_or_none(trkpt.attrib.get("lat"))
        lon = _float_or_none(trkpt.attrib.get("lon"))

        ele = _float_or_none(_text_or_none(trkpt.find("gpx:ele",NS)))
        speed = _float_or_none(_text_or_none(trkpt.find("gpx:speed",NS)))
        time = _dt_or_none(_text_or_none(trkpt.find("gpx:time",NS)))

        points.append(
            TrackPoint(
                time=time,
                lat=lat,
                lon=lon,
                ele=ele,
                speed_mps= speed
            )
        )
    start_time, end_time = _infer_time_bounds(points)
    bounds = _compute_bounds(points)

    return ParsedSession(
        start_time=start_time,
        end_time=end_time,
        points=points,
        bounds=bounds,
        track_name=track_name
    )
def _text_or_none(element: Optional[ET.Element]) -> Optional[str]:
    if element is None or element.text is None:
        return None
    return element.text.strip()

def _float_or_none(txt: Optional[str]) -> Optional[float]:
    if txt is None or txt =="":
        return None
    try:
        return float(txt)
    except ValueError:
        return None

def _dt_or_none(dt: Optional[str]) -> Optional[datetime]:
    if dt is None or dt =="":
        return None
    s = dt.replace("Z","+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None

def _infer_time_bounds(points: List[TrackPoint]) -> tuple[Optional[datetime],Optional[datetime]]:
    times = [p.time for p in points if p.time is not None]
    if not times:
        return None,None
    return min(times),max(times)

def _compute_bounds(points: List[TrackPoint]) -> Optional[Tuple[float,float,float,float]]:
    if not points:
        return None
    lats = [p.lat for p in points if p.lat is not None]
    lons = [p.lon for p in points if p.lon is not None]
    return (min(lats),min(lons),max(lats),max(lons))

if __name__ == "__main__":
    session = parse_gpx("../data/2026-01-25 11-16 AM We Ski Session.gpx")
    print(session.points,session.start_time,session.track_name)
