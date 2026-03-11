import hashlib
import hmac
import uuid

from django.db import models

from apps.core.models import BaseModel


class WebhookEndpoint(BaseModel):
    """URL назначения для webhook-уведомлений."""

    EVENTS = [
        'customer.created', 'customer.updated', 'customer.deleted',
        'deal.created', 'deal.updated', 'deal.won', 'deal.lost',
        'task.created', 'task.done',
        '*',
    ]

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='webhooks')
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=64, blank=True)
    events = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True)
    failure_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'webhook_endpoints'

    def sign(self, payload: bytes) -> str:
        return hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()

    def __str__(self):
        return f'{self.url} [{",".join(self.events)}]'


class WebhookDelivery(models.Model):
    """Лог каждой отправки."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.PositiveSmallIntegerField(null=True)
    response = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(null=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    class Meta:
        db_table = 'webhook_deliveries'
        ordering = ['-attempted_at']
        indexes = [models.Index(fields=['endpoint', '-attempted_at'])]
