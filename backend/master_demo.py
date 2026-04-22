"""
================================================================================
G15 ANALYTICS & NOTIFICATIONS: MASTER CONTROL PANEL
================================================================================

This is the central entry point for all G15 demos.
All actions are automated for a smooth presentation.

OPTIONS:
1. Setup -> Automatically creates an admin account (admin/admin123).
2. Seed  -> Fills DB with goal states (Achieved, At Risk, Missed, On Track).
3. Story -> Runs the 'Goal Achievement' narrative (Action -> Notification).
4. Vigil -> Runs the 'Ominous Observer' flow (Shadow Data -> API Alert).

By Gorav-K
"""

import os
import django
import asyncio
import traceback

# --- DJANGO SETUP ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


def _run_safe(fn, label):
    try:
        fn()
    except Exception as e:
        print(f"\n  [ERROR] [{label}] crashed: {e}")
        print("  Returning to menu safely. Full traceback below:")
        traceback.print_exc()

def create_superuser_demo():
    print("\n" + "="*49)
    print("   STEP 1: DATABASE ACCOUNT SETUP")
    print("   " + "="*46)

    username = "admin"
    password = "admin123"

    if User.objects.filter(username=username).exists():
        print(f"\n   [Status] User '{username}' already exists.")
    else:
        print(f"\n   [Action] Automatically creating user: {username}")
        User.objects.create_superuser(username, "admin@example.com", password)
        print(f"   [Success] Created superuser '{username}' with password '{password}'")

def seed_notifications_demo():
    print("\n" + "="*49)
    print("   STEP 2: DATA SEEDING (ALL STATES)")
    print("   " + "="*46)
    call_command('seed_notifications', clear=True)

def notifications_flow_demo():
    from notifications_demo import run_demo
    run_demo()

def ominous_observer_demo():
    from ominous_demo import run_demo
    # Run the async demo in a controlled way
    asyncio.run(run_demo())

def main_menu():
    while True:
        print("\n" + "="*54)
        print("   G15 ANALYTICS & NOTIFICATIONS: MASTER DEMO")
        print("="*54)
        print(" 1. [SETUP] Create Admin Account (Automated)")
        print(" 2. [SEED]  Generate All Goal States (Achieved/At Risk/etc.)")
        print(" 3. [STORY] Run Goal -> Notification Flow")
        print(" 4. [VIGIL] Run Ominous Observer (Shadow Data Detection)")
        print(" 5. [EXIT]  Close Control Panel")
        
        choice = input("\nSelect an option (1-5): ")

        if choice == '1':
            _run_safe(create_superuser_demo, "SETUP")
        elif choice == '2':
            _run_safe(seed_notifications_demo, "SEED")
        elif choice == '3':
            _run_safe(notifications_flow_demo, "STORY")
        elif choice == '4':
            _run_safe(ominous_observer_demo, "VIGIL")
        elif choice == '5':
            print("\nExiting. Good luck with the presentation!")
            break
        else:
            print("\nInvalid choice. Please select 1-5.")
        
        input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main_menu()
