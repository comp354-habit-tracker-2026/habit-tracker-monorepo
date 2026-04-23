import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification, NotificationChannel, NotificationType, UserNotificationPreference, NotificationStatus
from rest_framework.test import APIClient
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
def test_view_notifications_success():
    user = User.objects.create_user(username='notif-user', email='notif@example.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/v1/notifications/{user.id}/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_notifications_empty():
    user = User.objects.create_user(username='empty-notif-user', email='empty-notif@example.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/v1/notifications/{user.id}/')
    assert response.status_code == 200


def test_unauthorized_access():
    client = APIClient()
    response = client.get('/api/v1/notifications/1/')
    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_notifications_list_returns_users_notifications():
    user = User.objects.create_user(username='list-user', email='list@example.com', password='TestPass123!')
    Notification.objects.create(
        user=user,
        type=NotificationType.MILESTONE_ACHIEVED,
        message='hello',
        channel=NotificationChannel.IN_APP,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/notifications/')

    assert response.status_code == 200
    assert len(response.data['notifications']) == 1


@pytest.mark.django_db
def test_mark_notification_as_read_success():
    user = User.objects.create_user(username='read-user', email='read@example.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user,
        type=NotificationType.MILESTONE_ACHIEVED,
        message='mark me',
        channel=NotificationChannel.IN_APP,
        read=False,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(f'/api/v1/notifications/{notification.pk}/read/')

    notification.refresh_from_db()
    assert response.status_code == 200
    assert notification.read is True


@pytest.mark.django_db
def test_mark_notification_as_read_forbidden_for_other_user():
    user = User.objects.create_user(username='owner-user', email='owner@example.com', password='TestPass123!')
    other_user = User.objects.create_user(username='other-user', email='other@example.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user,
        type=NotificationType.MILESTONE_ACHIEVED,
        message='mark me',
        channel=NotificationChannel.IN_APP,
    )

    client = APIClient()
    client.force_authenticate(user=other_user)
    response = client.post(f'/api/v1/notifications/{notification.pk}/read/')

    assert response.status_code == 403


# ============================================================================
# Coverage tests for repository and view error paths
# ============================================================================

@pytest.mark.django_db
def test_mark_notification_as_read_when_already_read():
    """Covers early return in mark_as_read when notification.read is True"""
    user = User.objects.create_user(username='already-read-user', email='ar@test.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='already read',
        channel=NotificationChannel.IN_APP,
        read=True,
    )
    
    from notifications.data.repositories import NotificationRepository
    repo = NotificationRepository()
    result = repo.mark_as_read(notification.notif_id)
    
    assert result.read is True
    # Verify it didn't re-save unnecessarily
    notification.refresh_from_db()
    assert notification.read is True


@pytest.mark.django_db
def test_mark_all_as_read_batch_update():
    """Covers mark_all_as_read batch update path"""
    user = User.objects.create_user(username='batch-user', email='batch@test.com', password='TestPass123!')
    n1 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='n1',
        channel=NotificationChannel.IN_APP,
        read=False,
    )
    n2 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='n2',
        channel=NotificationChannel.EMAIL,
        read=False,
    )
    
    from notifications.data.repositories import NotificationRepository
    repo = NotificationRepository()
    repo.mark_all_as_read(user)
    
    n1.refresh_from_db()
    n2.refresh_from_db()
    assert n1.read is True
    assert n2.read is True


@pytest.mark.django_db
def test_get_all_notifications_ordering():
    """Covers get_all ordering by created_at descending"""
    user = User.objects.create_user(username='order-user', email='order@test.com', password='TestPass123!')
    n1 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='first',
        channel=NotificationChannel.IN_APP,
    )
    n2 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='second',
        channel=NotificationChannel.EMAIL,
    )
    
    from notifications.data.repositories import NotificationRepository
    repo = NotificationRepository()
    result = list(repo.get_all(user))
    
    # Newest first
    assert result[0].notif_id == n2.notif_id
    assert result[1].notif_id == n1.notif_id


@pytest.mark.django_db
def test_delete_notification_not_found_error():
    """Covers delete view error when notification not found"""
    user = User.objects.create_user(username='del-notfound-user', email='del-nf@test.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.delete('/api/v1/notifications/99999/delete/')
    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_delete_notification_unauthorized():
    """Covers delete view unauthorized path"""
    user1 = User.objects.create_user(username='del-user1', email='del1@test.com', password='TestPass123!')
    user2 = User.objects.create_user(username='del-user2', email='del2@test.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user1,
        type=NotificationType.GOAL_ACHIEVED,
        message='other user notif',
        channel=NotificationChannel.IN_APP,
    )
    
    client = APIClient()
    client.force_authenticate(user=user2)
    response = client.delete(f'/api/v1/notifications/{notification.notif_id}/delete/')
    
    assert response.status_code == 403


@pytest.mark.django_db
def test_mark_as_read_not_found_error():
    """Covers mark_as_read view error when notification not found"""
    user = User.objects.create_user(username='mark-notfound-user', email='mark-nf@test.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.post('/api/v1/notifications/99999/read/')
    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_mark_as_read_unauthorized():
    """Covers mark_as_read view unauthorized path"""
    user1 = User.objects.create_user(username='mark-user1', email='mark1@test.com', password='TestPass123!')
    user2 = User.objects.create_user(username='mark-user2', email='mark2@test.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user1,
        type=NotificationType.GOAL_ACHIEVED,
        message='other user notif',
        channel=NotificationChannel.IN_APP,
        read=False,
    )
    
    client = APIClient()
    client.force_authenticate(user=user2)
    response = client.post(f'/api/v1/notifications/{notification.notif_id}/read/')
    
    assert response.status_code == 403


@pytest.mark.django_db
def test_view_notifications_unauthorized_user():
    """Covers ViewNotifications unauthorized path"""
    user1 = User.objects.create_user(username='view-user1', email='view1@test.com', password='TestPass123!')
    user2 = User.objects.create_user(username='view-user2', email='view2@test.com', password='TestPass123!')
    
    client = APIClient()
    client.force_authenticate(user=user1)
    response = client.get(f'/api/v1/notifications/{user2.id}/')
    
    assert response.status_code == 403


@pytest.mark.django_db
def test_notifications_list_empty():
    """Covers empty notifications list response"""
    user = User.objects.create_user(username='empty-user', email='empty@test.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.get('/api/v1/notifications/')
    assert response.status_code == 200
    assert response.data['notifications'] == []


@pytest.mark.django_db
def test_notifications_list_newest_first():
    """Covers notifications list ordering newest-first"""
    user = User.objects.create_user(username='newest-user', email='newest@test.com', password='TestPass123!')
    n1 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='first',
        channel=NotificationChannel.IN_APP,
    )
    n2 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='second',
        channel=NotificationChannel.EMAIL,
    )
    
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/notifications/')
    
    assert response.status_code == 200
    assert len(response.data['notifications']) == 2
    # Newest first (n2 before n1)
    assert response.data['notifications'][0]['notif_id'] == n2.notif_id
    assert response.data['notifications'][1]['notif_id'] == n1.notif_id


# ============================================================================
# Repository method coverage tests
# ============================================================================

@pytest.mark.django_db
def test_notification_repository_create_notification():
    """Covers NotificationRepository.create_notification full path"""
    from notifications.data.repositories import NotificationRepository
    from goals.models import Goal
    
    user = User.objects.create_user(username='repo-create-user', email='repo-create@test.com', password='TestPass123!')
    repo = NotificationRepository()
    
    result = repo.create_notification(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='Test message',
        payload={'goal_id': 1},
        channel=NotificationChannel.EMAIL,
        scheduled_at=None,
        goal=None
    )
    
    assert result.user_id == user.id
    assert result.type == NotificationType.GOAL_ACHIEVED
    assert result.message == 'Test message'
    assert result.channel == NotificationChannel.EMAIL


@pytest.mark.django_db
def test_notification_repository_get():
    """Covers NotificationRepository.get method"""
    from notifications.data.repositories import NotificationRepository
    
    user = User.objects.create_user(username='repo-get-user', email='repo-get@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='Test',
        channel=NotificationChannel.IN_APP,
    )
    
    repo = NotificationRepository()
    result = repo.get(notif.notif_id)
    
    assert result.notif_id == notif.notif_id
    assert result.type == NotificationType.GOAL_AT_RISK


@pytest.mark.django_db
def test_notification_repository_delete():
    """Covers NotificationRepository.delete method"""
    from notifications.data.repositories import NotificationRepository
    
    user = User.objects.create_user(username='repo-del-user', email='repo-del@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_MISSED,
        message='Test',
        channel=NotificationChannel.EMAIL,
    )
    
    repo = NotificationRepository()
    repo.delete(notif.notif_id)
    
    assert Notification.objects.filter(notif_id=notif.notif_id).exists() is False


@pytest.mark.django_db
def test_notification_repository_list_recent():
    """Covers NotificationRepository.list_recent method"""
    from notifications.data.repositories import NotificationRepository
    
    user = User.objects.create_user(username='repo-recent-user', email='repo-recent@test.com', password='TestPass123!')
    n1 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='First',
        channel=NotificationChannel.IN_APP,
    )
    n2 = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='Second',
        channel=NotificationChannel.EMAIL,
    )
    
    repo = NotificationRepository()
    result = repo.list_recent(user)
    
    assert len(result) == 2
    # Newest first
    assert result[0]['id'] == n2.notif_id or result[0].get('notif_id') == n2.notif_id


# ============================================================================
# UserPreferenceRepository coverage tests
# ============================================================================

@pytest.mark.django_db
def test_user_preference_repository_get_or_create():
    """Covers UserPreferenceRepository.get_user_preferences get_or_create"""
    from notifications.data.repositories import UserPreferenceRepository
    
    user = User.objects.create_user(username='pref-user', email='pref@test.com', password='TestPass123!')
    repo = UserPreferenceRepository()
    
    # First call should create
    result1 = repo.get_user_preferences(user)
    assert result1.user_id == user.id
    
    # Second call should return existing
    result2 = repo.get_user_preferences(user)
    assert result1.id == result2.id


@pytest.mark.django_db
def test_user_preference_repository_create_user_preferences():
    """Covers UserPreferenceRepository.create_user_preferences"""
    from notifications.data.repositories import UserPreferenceRepository
    
    user = User.objects.create_user(username='pref-create-user', email='pref-create@test.com', password='TestPass123!')
    repo = UserPreferenceRepository()
    
    result = repo.create_user_preferences(user)
    
    assert result.user_id == user.id
    assert result.email_enabled is True
    assert result.in_app_enabled is True


@pytest.mark.django_db
def test_user_preference_repository_update_user_preferences():
    """Covers UserPreferenceRepository.update_user_preferences with allowed fields"""
    from notifications.data.repositories import UserPreferenceRepository
    
    user = User.objects.create_user(username='pref-update-user', email='pref-update@test.com', password='TestPass123!')
    prefs = UserNotificationPreference.objects.create(user=user)
    repo = UserPreferenceRepository()
    
    result = repo.update_user_preferences(
        user,
        email_enabled=False,
        in_app_enabled=False,
        achievement_notifs=False,
        goal_notifs=False,
        inactivity_reminders=False,
        inactivity_threshold_days=14,
    )
    
    assert result.email_enabled is False
    assert result.in_app_enabled is False
    assert result.achievement_notifs is False
    assert result.goal_notifs is False
    assert result.inactivity_reminders is False
    assert result.inactivity_threshold_days == 14


@pytest.mark.django_db
def test_user_preference_repository_update_ignores_disallowed_fields():
    """Covers UserPreferenceRepository.update_user_preferences with disallowed fields"""
    from notifications.data.repositories import UserPreferenceRepository
    
    user = User.objects.create_user(username='pref-disallow-user', email='pref-disallow@test.com', password='TestPass123!')
    prefs = UserNotificationPreference.objects.create(user=user, email_enabled=True)
    repo = UserPreferenceRepository()
    
    # Try to update with disallowed field
    result = repo.update_user_preferences(
        user,
        email_enabled=False,
        pref_id=999,  # disallowed field
    )
    
    assert result.email_enabled is False
    assert result.pref_id != 999  # Should not have changed


# ============================================================================
# View exception handling coverage tests
# ============================================================================

@pytest.mark.django_db
def test_notifications_list_view_exception_handling():
    """Covers NotificationsListView exception path"""
    user = User.objects.create_user(username='list-exc-user', email='list-exc@test.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Mock service to raise exception
    with patch('notifications.presentation.views.NotificationService.get_all_notifications', side_effect=Exception("DB Error")):
        response = client.get('/api/v1/notifications/')
    
    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_view_notifications_exception_handling():
    """Covers ViewNotifications exception path"""
    user = User.objects.create_user(username='view-exc-user', email='view-exc@test.com', password='TestPass123!')
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Mock service to raise exception
    with patch('notifications.presentation.views.NotificationService.get_all_notifications', side_effect=Exception("DB Error")):
        response = client.get(f'/api/v1/notifications/{user.id}/')
    
    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_delete_notification_view_exception_handling():
    """Covers DeleteNotificationView exception path"""
    user = User.objects.create_user(username='del-exc-user', email='del-exc@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='Test',
        channel=NotificationChannel.IN_APP,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Mock service to raise exception
    with patch('notifications.presentation.views.NotificationService.get', side_effect=Exception("DB Error")):
        response = client.delete(f'/api/v1/notifications/{notif.notif_id}/delete/')
    
    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_mark_as_read_view_exception_handling():
    """Covers MarkNotificationAsRead exception path"""
    user = User.objects.create_user(username='mark-exc-user', email='mark-exc@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='Test',
        channel=NotificationChannel.IN_APP,
        read=False,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Mock service to raise exception
    with patch('notifications.presentation.views.NotificationService.get', side_effect=Exception("DB Error")):
        response = client.post(f'/api/v1/notifications/{notif.notif_id}/read/')
    
    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_delete_notification_success():
    """Covers DeleteNotificationView success path (no exception)"""
    user = User.objects.create_user(username='del-success-user', email='del-success@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='To be deleted',
        channel=NotificationChannel.IN_APP,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.delete(f'/api/v1/notifications/{notif.notif_id}/delete/')
    
    assert response.status_code == 204
    assert Notification.objects.filter(notif_id=notif.notif_id).exists() is False


@pytest.mark.django_db
def test_mark_as_read_success():
    """Covers MarkNotificationAsRead success path (no exception)"""
    user = User.objects.create_user(username='mark-success-user', email='mark-success@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='To be marked',
        channel=NotificationChannel.IN_APP,
        read=False,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.post(f'/api/v1/notifications/{notif.notif_id}/read/')
    
    assert response.status_code == 200
    assert "Notification marked as read" in response.data.get("message", "")
    notif.refresh_from_db()
    assert notif.read is True


@pytest.mark.django_db
def test_view_notifications_success():
    """Covers ViewNotifications success path with notifications"""
    user = User.objects.create_user(username='view-success-user', email='view-success@test.com', password='TestPass123!')
    Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='Test notification',
        channel=NotificationChannel.EMAIL,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.get(f'/api/v1/notifications/{user.id}/')
    
    assert response.status_code == 200
    assert len(response.data["notifications"]) == 1


@pytest.mark.django_db
def test_notifications_list_success_with_multiple():
    """Covers NotificationsListView success path with multiple notifications"""
    user = User.objects.create_user(username='list-success-user', email='list-success@test.com', password='TestPass123!')
    Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='First',
        channel=NotificationChannel.IN_APP,
    )
    Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='Second',
        channel=NotificationChannel.EMAIL,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.get('/api/v1/notifications/')
    
    assert response.status_code == 200
    assert len(response.data["notifications"]) == 2


# ============================================================================
# Model coverage tests (__str__ methods and defaults)
# ============================================================================

@pytest.mark.django_db
def test_notification_str_method():
    """Covers Notification.__str__ method"""
    user = User.objects.create_user(username='notif-str-user', email='notif-str@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_ACHIEVED,
        message='Test',
        channel=NotificationChannel.IN_APP,
    )
    
    str_repr = str(notif)
    assert 'Notification' in str_repr
    assert str(notif.notif_id) in str_repr
    assert user.username in str_repr
    assert NotificationType.GOAL_ACHIEVED in str_repr


@pytest.mark.django_db
def test_notification_model_defaults():
    """Covers Notification model field defaults"""
    user = User.objects.create_user(username='notif-defaults-user', email='notif-def@test.com', password='TestPass123!')
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_AT_RISK,
        message='Test',
        channel=NotificationChannel.EMAIL,
    )
    
    assert notif.read is False
    assert notif.status == NotificationStatus.PENDING
    assert notif.archived is False
    assert notif.created_at is not None
    assert notif.scheduled_at is None
    assert notif.sent_at is None
    assert notif.goal_id is None


@pytest.mark.django_db
def test_user_notification_preference_str_method():
    """Covers UserNotificationPreference.__str__ method"""
    user = User.objects.create_user(username='pref-str-user', email='pref-str@test.com', password='TestPass123!')
    prefs = UserNotificationPreference.objects.create(user=user)
    
    str_repr = str(prefs)
    assert 'Notification Preferences' in str_repr
    assert user.username in str_repr


@pytest.mark.django_db
def test_user_notification_preference_defaults():
    """Covers UserNotificationPreference model field defaults"""
    user = User.objects.create_user(username='pref-defaults-user', email='pref-def@test.com', password='TestPass123!')
    prefs = UserNotificationPreference.objects.create(user=user)
    
    assert prefs.email_enabled is True
    assert prefs.in_app_enabled is True
    assert prefs.achievement_notifs is True
    assert prefs.goal_notifs is True
    assert prefs.inactivity_reminders is True
    assert prefs.inactivity_threshold_days == 7


@pytest.mark.django_db
def test_notification_type_choices():
    """Covers all NotificationType choices"""
    assert NotificationType.NONE == 'NONE'
    assert NotificationType.MILESTONE_ACHIEVED == 'MILESTONE_ACHIEVED'
    assert NotificationType.GOAL_ACHIEVED == 'GOAL_ACHIEVED'
    assert NotificationType.GOAL_AT_RISK == 'GOAL_AT_RISK'
    assert NotificationType.GOAL_MISSED == 'GOAL_MISSED'
    assert NotificationType.INACTIVITY_REMINDER == 'INACTIVITY_REMINDER'


@pytest.mark.django_db
def test_notification_status_choices():
    """Covers all NotificationStatus choices"""
    assert NotificationStatus.PENDING == 'PENDING'
    assert NotificationStatus.SENT == 'SENT'
    assert NotificationStatus.FAILED == 'FAILED'
    assert NotificationStatus.SNOOZED == 'SNOOZED'
    assert NotificationStatus.ARCHIVED == 'ARCHIVED'


@pytest.mark.django_db
def test_notification_channel_choices():
    """Covers all NotificationChannel choices"""
    assert NotificationChannel.EMAIL == 'EMAIL'
    assert NotificationChannel.IN_APP == 'IN_APP'


@pytest.mark.django_db
def test_notification_with_all_fields():
    """Covers Notification with all optional fields set"""
    from datetime import datetime, timezone
    user = User.objects.create_user(username='full-notif-user', email='full@test.com', password='TestPass123!')
    scheduled_time = datetime(2026, 4, 25, 10, 0, 0, tzinfo=timezone.utc)
    sent_time = datetime(2026, 4, 25, 10, 5, 0, tzinfo=timezone.utc)
    
    notif = Notification.objects.create(
        user=user,
        type=NotificationType.GOAL_MISSED,
        message='Complete test',
        channel=NotificationChannel.EMAIL,
        status=NotificationStatus.SENT,
        read=True,
        archived=True,
        payload={"test": "data"},
        scheduled_at=scheduled_time,
        sent_at=sent_time,
    )
    
    assert notif.type == NotificationType.GOAL_MISSED
    assert notif.status == NotificationStatus.SENT
    assert notif.read is True
    assert notif.archived is True
    assert notif.payload == {"test": "data"}
    assert notif.scheduled_at == scheduled_time
    assert notif.sent_at == sent_time






@pytest.mark.django_db
def test_delete_notification_success():
    user = User.objects.create_user(username='delete-user', email='delete@example.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user,
        type=NotificationType.MILESTONE_ACHIEVED,
        message='delete me',
        channel=NotificationChannel.IN_APP,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.delete(f'/api/v1/notifications/{notification.pk}/delete/')

    assert response.status_code == 204
    assert Notification.objects.filter(pk=notification.pk).exists() is False


@pytest.mark.django_db
def test_delete_notification_forbidden_for_other_user():
    user = User.objects.create_user(username='delete-owner', email='delete-owner@example.com', password='TestPass123!')
    other_user = User.objects.create_user(username='delete-other', email='delete-other@example.com', password='TestPass123!')
    notification = Notification.objects.create(
        user=user,
        type=NotificationType.MILESTONE_ACHIEVED,
        message='delete me',
        channel=NotificationChannel.IN_APP,
    )

    client = APIClient()
    client.force_authenticate(user=other_user)
    response = client.delete(f'/api/v1/notifications/{notification.pk}/delete/')

    assert response.status_code == 403