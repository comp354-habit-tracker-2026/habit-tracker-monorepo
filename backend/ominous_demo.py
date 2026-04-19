"""
================================================================================
G15 DEMO: THE OMINOUS OBSERVER (OUTBOX PATTERN)
================================================================================

This demo showcases how the Analytics API 'observes' the database for new
activities and alerts the user to refresh their view.

VISUAL FLOW:
[ 1. Baseline ]  ---> User checks dashboard. Everything is normal.
[ 2. Intrusion ] ---> External data (Strava) hits the database in the shadows.
[ 3. Detection ] ---> API detects the 'Pending' event and injects an alert.
[ 4. Refresh ]   ---> User refreshes; the ominous message vanishes.
"""

import asyncio
from datetime import datetime, timedelta
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from core.models import OutboxEvent
from activities.models import ConnectedAccount
from analytics.business.api_router import health_indicators_endpoint, HealthIndicatorsRequest

User = get_user_model()

async def run_demo():
    print("\n" + "="*50)
    print("   OMINOUS OBSERVER: DATABASE VIGILANCE DEMO")
    print("   " + "="*46)

    # --------------------------------------------------------------------------
    # STEP 0: INITIALIZATION
    # --------------------------------------------------------------------------
    # Use sync_to_async for all Django ORM calls inside an async function
    user, _ = await sync_to_async(User.objects.get_or_create)(
        username="demo_stalker",
        defaults={"email": "stalker@example.com"},
    )
    account, _ = await sync_to_async(ConnectedAccount.objects.get_or_create)(
        user=user, 
        provider="strava", 
        external_user_id="12345"
    )
    
    # Reset state for clean demo
    await sync_to_async(lambda: OutboxEvent.objects.filter(payload__user_id=str(user.id)).delete())()

    req = HealthIndicatorsRequest(
        user_id=str(user.id),
        from_date=datetime.now() - timedelta(days=7),
        to_date=datetime.now(),
        target_workouts=3
    )

    # --------------------------------------------------------------------------
    # STEP 1: THE BASELINE (Static View)
    # --------------------------------------------------------------------------
    print("\n[Step 1] Baseline: User checks dashboard.")
    print("         Action: GET /api/v1/analytics/health-indicators")
    res = await health_indicators_endpoint(req)
    messages = res["data"]["messages"]
    print(f"         Response Messages: {messages if messages else 'None (Dashboard is up to date)'}")

    # --------------------------------------------------------------------------
    # STEP 2: THE INTRUSION (Background Import)
    # --------------------------------------------------------------------------
    print("\n[Step 2] Intrusion: New data arrives from Strava in the shadows.")
    print("         Action: INSERT INTO outbox_events (status='PENDING')")
    await sync_to_async(OutboxEvent.objects.create)(
        event_type="activity.imported",
        payload={"user_id": str(user.id), "activity_id": "999"},
        status=OutboxEvent.Status.PENDING
    )

    # --------------------------------------------------------------------------
    # STEP 3: THE DETECTION (Ominous Alert)
    # --------------------------------------------------------------------------
    print("\n[Step 3] Detection: User hits API again. The Observer is watching.")
    print("         Action: GET /api/v1/analytics/health-indicators")
    res = await health_indicators_endpoint(req)
    messages = res["data"]["messages"]
    
    if any("detected" in m or "refresh" in m.lower() for m in messages):
        print(f"         [ALERT DETECTED] API injected message: \"{messages[-1]}\"")
        print("         Visual: A red/blue glow or toast notification on the UI.")
    else:
        print("         [ERROR] No alert detected.")

    # --------------------------------------------------------------------------
    # STEP 4: THE RESOLUTION (Post-Refresh)
    # --------------------------------------------------------------------------
    print("\n[Step 4] Resolution: User refreshes. The shadows recede.")
    print("         Action: UPDATE outbox_events SET status='PUBLISHED'")
    await sync_to_async(lambda: OutboxEvent.objects.filter(payload__user_id=str(user.id)).update(status=OutboxEvent.Status.PUBLISHED))()

    res = await health_indicators_endpoint(req)
    messages = res["data"]["messages"]
    print(f"         Response Messages: {messages if messages else 'None (Clean state)'}")
    print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(run_demo())
