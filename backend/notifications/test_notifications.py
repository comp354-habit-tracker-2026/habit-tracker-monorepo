import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification, NotificationChannel, NotificationType
from rest_framework.test import APIClient

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