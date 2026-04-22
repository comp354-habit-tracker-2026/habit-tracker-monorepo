import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.notifications.models import NotificationType

logger = logging.getLogger(__name__)


@receiver(post_save, sender='activities.Activity')
def evaluate_achievements_on_activity(sender, instance, created, **kwargs):
    """When a new activity is saved, evaluate badges, streaks, and milestones."""
    if not created:
        return

    # If the activity has no connected account (e.g. seeded/legacy data), skip gamification
    if not instance.account_id:
        return

    from gamification.business.services import GamificationService

    service = GamificationService()
    user = instance.account.user  # user is reached through the connected account

    # Update streak
    streak = service.update_streak(user, instance.date)
    logger.info("Streak updated for user %s: %d days", user.pk, streak.current_count)

    # Evaluate badges
    new_badges = service.evaluate_badges(user, instance)
    for badge in new_badges:
        logger.info("User %s earned badge: %s", user.pk, badge.name)
        _send_achievement_event(user, 'badge_earned', {
            'badge_id': badge.pk,
            'badge_name': badge.name,
            'points': badge.points,
        })

    # Evaluate milestones
    new_milestones = service.evaluate_milestones(user)
    for milestone in new_milestones:
        logger.info("User %s reached milestone: %s", user.pk, milestone.name)
        _send_achievement_event(user, 'milestone_reached', {
            'milestone_id': milestone.pk,
            'milestone_name': milestone.name,
            'points': milestone.points,
        })



def _send_achievement_event(user, event_type, payload):
    """Send an achievement event to Group 23's notification system.

    This is the contract between Group 24 and Group 23:
    - event_type: 'badge_earned' | 'milestone_reached' | 'streak_milestone'
    - payload: dict with achievement details

    Currently calls Group 23's NotificationService if available,
    otherwise logs the event for later integration.
    """
    try:
        from notifications.business.services import NotificationService
        service = NotificationService()
        service.notify(None, "Milestone reached!", payload, user.user_id, NotificationType.MILESTONE_ACHIEVED)
    except (ImportError, AttributeError):
        # Group 23 hasn't implemented this yet -- just log it
        logger.info(
            "Achievement event (pending notification integration): "
            "user=%s type=%s payload=%s",
            user.pk, event_type, payload,
        )
