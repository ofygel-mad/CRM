import pytest


@pytest.mark.django_db
class TestNotifications:
    def test_list_empty_initially(self, api_client):
        r = api_client.get('/api/v1/notifications/')
        assert r.status_code == 200
        assert r.data['count'] == 0

    def test_mark_all_read(self, api_client, org, user):
        from apps.notifications.models import Notification

        Notification.objects.create(
            organization=org, recipient=user,
            title='Test', body='Body',
            notification_type='info',
        )
        r = api_client.post('/api/v1/notifications/read_all/')
        assert r.status_code == 200
        assert Notification.objects.filter(
            recipient=user, is_read=False
        ).count() == 0

    def test_unread_filter(self, api_client, org, user):
        from apps.notifications.models import Notification

        Notification.objects.create(
            organization=org, recipient=user,
            title='Unread', body='x', notification_type='info',
        )
        Notification.objects.create(
            organization=org, recipient=user,
            title='Read', body='x', notification_type='info',
            is_read=True,
        )
        r = api_client.get('/api/v1/notifications/?unread=1')
        assert r.status_code == 200
        assert r.data['count'] == 1
