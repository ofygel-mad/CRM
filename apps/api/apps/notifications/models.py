import uuid
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        AUTOMATION = 'automation', 'Автоматизация'
        TASK = 'task', 'Задача'
        DEAL = 'deal', 'Сделка'
        SYSTEM = 'system', 'Система'
        MENTION = 'mention', 'Упоминание'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE, related_name='notifications',
    )
    recipient = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='notifications',
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    notification_type = models.CharField(max_length=30, choices=Type.choices, default=Type.SYSTEM)
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
        ]

    def __str__(self):
        return f'{self.title} → {self.recipient_id}'
