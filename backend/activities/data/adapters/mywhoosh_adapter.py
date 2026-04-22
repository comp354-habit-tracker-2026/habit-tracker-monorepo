"""Name: Kabeya Ngoyi + Jeffrey Bringolf
    Student ID: 27214545 + 40282898
    File: mywhoosh_adapter.py
    
    Description: 
    This file contains the MyWhoosh adapter. It converts raw MyWhoosh
    activity into the unified Activity format used by the system."""

from .activity_adapter_base import ActivityAdapter
from .models import ActivitySource, MyWhooshActivity
from .config.config import AdapterConfig

class MyWhooshAdapter(ActivityAdapter):
    super().__init__(
            ActivitySource.MY_WHOOSH, 
            AdapterConfig.get_activity_schema(AdapterConfig.MY_WHOOSH_ADAPTER_SCHEMA_FILENAME), 
            MyWhooshActivity
            )
    