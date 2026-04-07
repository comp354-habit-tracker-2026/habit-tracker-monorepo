""" Name: Kabeya Ngoyi + Jeffrey Bringolf
    Student ID: 27214545 + 40282898
    File: weski_adapter.py
    
    Description: 
    This file contains the WeSki adapter. It converts raw WeSki activity
    into the unified Activity format used by the system. """

from .activity_adapter_base import ActivityAdapter
from .models import ActivitySource, WeSkiActivity
from .config.config import AdapterConfig

class WeSkiAdapter(ActivityAdapter):
    def __init__(self):
        super().__init__(
            ActivitySource.WE_SKI, 
            AdapterConfig.get_activity_schema(AdapterConfig.WE_SKI_ADAPTER_SCHEMA_FILENAME), 
            WeSkiActivity
            )

    