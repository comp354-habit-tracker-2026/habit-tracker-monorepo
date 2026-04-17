from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from activities.models import Activity
from analytics.progess_series.cache import goal_progress_cache


def _activity_user_id(activity: Activity) -> int | None:
    if activity.account_id:
        return activity.account.user_id
    return None


@receiver(post_save, sender=Activity)
def invalidate_goal_progress_cache_on_save(sender, instance, **kwargs):
    user_id = _activity_user_id(instance)
    if user_id is not None:
        goal_progress_cache.invalidate_for_user(user_id)


@receiver(post_delete, sender=Activity)
def invalidate_goal_progress_cache_on_delete(sender, instance, **kwargs):
    user_id = _activity_user_id(instance)
    if user_id is not None:
        goal_progress_cache.invalidate_for_user(user_id)
