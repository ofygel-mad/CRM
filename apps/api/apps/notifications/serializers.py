from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type',
            'entity_type', 'entity_id', 'is_read', 'read_at', 'created_at',
        ]
