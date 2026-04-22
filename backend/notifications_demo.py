"""
================================================================================
G15 DEMO: GOAL PROGRESS NOTIFICATIONS (STORY MODE)
================================================================================

This demo tells the story of a user who sets a goal, achieves it, and 
immediately sees a system-generated notification.

VISUAL FLOW:
[ 1. Intent ]     ---> User creates a 'Run 10 km' Goal. (State: ON_TRACK)
[ 2. Effort ]     ---> User uploads data. Value jumps from 0 to 10.5 km.
[ 3. Transition ] ---> Analytics Engine detects state change to 'ACHIEVED'.
[ 4. Reward ]     ---> System injects a Notification into the user's feed.
"""

import json
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from goals.models import Goal
from notifications.models import Notification
from analytics.business.goal_progress import GoalProgressService

User = get_user_model()

def run_demo():
    print("\n" + "="*50)
    print("   GOAL PROGRESS: FROM ACTION TO NOTIFICATION")
    print("   " + "="*46)

    # --------------------------------------------------------------------------
    # STEP 0: SETUP
    # --------------------------------------------------------------------------
    user, _ = User.objects.get_or_create(username="notif_hero", email="hero@example.com")
    
    # Cleanup for clean demo
    Goal.objects.filter(user=user, title__contains="[Demo]").delete()
    Notification.objects.filter(user=user).delete()

    # --------------------------------------------------------------------------
    # STEP 1: THE INTENT (Goal Creation)
    # --------------------------------------------------------------------------
    print("\n[Step 1] Intent: User sets a new challenge.")
    print("         Action: POST /api/v1/goals/ ('Run 10 km')")
    goal = Goal.objects.create(
        user=user,
        title="[Demo] Run 10 km",
        goal_type="distance",
        target_value=10.0,
        current_value=0.0,
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=7)
    )
    print(f"         Goal Active! Current Progress: {goal.current_value}/{goal.target_value} km")

    # --------------------------------------------------------------------------
    # STEP 2: THE EFFORT (Progress Update)
    # --------------------------------------------------------------------------
    print("\n[Step 2] Effort: User completes a massive run.")
    print("         Action: Activity Import -> goal.current_value = 10.5")
    goal.current_value = 10.5
    goal.save()

    # --------------------------------------------------------------------------
    # STEP 3: THE TRANSITION (Analytics Evaluation)
    # --------------------------------------------------------------------------
    print("\n[Step 3] Transition: Analytics Engine evaluates the new state.")
    print("         Action: GoalProgressService.evaluate_goal(goal)")
    svc = GoalProgressService()
    result = svc.evaluate_goal(goal)
    
    print(f"         New State Detected: {result['state']}")
    if result['notification_created']:
        print("         [SUCCESS] Notification triggered automatically!")

    # --------------------------------------------------------------------------
    # STEP 4: THE REWARD (Inbox Check)
    # --------------------------------------------------------------------------
    print("\n[Step 4] Reward: User checks their notifications.")
    print("         Action: GET /api/v1/notifications/")
    notifs = Notification.objects.filter(user=user)
    
    if notifs.exists():
        for n in notifs:
            print(f"         [NOTIF] {n.title.upper()}")
            print(f"         Message: {n.message}")
    else:
        print("         [ERROR] No notification found.")

    print("\n" + "="*50)

if __name__ == "__main__":
    run_demo()
