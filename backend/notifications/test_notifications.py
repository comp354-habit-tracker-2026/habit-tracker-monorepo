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