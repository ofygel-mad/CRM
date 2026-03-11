import json
import logging
import time

import requests
from celery import shared_task
from django.db import models

logger = logging.getLogger(__name__)

MAX_FAILURES = 5
TIMEOUT = 10


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_webhook(self, endpoint_id: str, event_type: str, payload: dict):
    from apps.webhooks.models import WebhookDelivery, WebhookEndpoint

    try:
        ep = WebhookEndpoint.objects.get(id=endpoint_id, is_active=True)
    except WebhookEndpoint.DoesNotExist:
        return

    body = json.dumps(payload, ensure_ascii=False, default=str).encode()
    headers = {
        'Content-Type': 'application/json',
        'X-CRM-Event': event_type,
        'X-CRM-Delivery': str(self.request.id or ''),
        'X-CRM-Signature-256': f'sha256={ep.sign(body)}',
    }

    start = time.monotonic()
    delivery = WebhookDelivery(endpoint=ep, event_type=event_type, payload=payload)
    try:
        response = requests.post(ep.url, data=body, headers=headers, timeout=TIMEOUT)
        delivery.status_code = response.status_code
        delivery.response = response.text[:2000]
        delivery.success = 200 <= response.status_code < 300
        delivery.duration_ms = int((time.monotonic() - start) * 1000)
        delivery.save()

        if delivery.success:
            WebhookEndpoint.objects.filter(id=endpoint_id).update(failure_count=0)
        else:
            ep.failure_count += 1
            if ep.failure_count >= MAX_FAILURES:
                ep.is_active = False
                logger.warning('Webhook %s disabled after %d failures', ep.url, ep.failure_count)
            ep.save(update_fields=['failure_count', 'is_active'])
            raise self.retry()
    except requests.RequestException as exc:
        delivery.response = str(exc)[:2000]
        delivery.save()
        raise self.retry(exc=exc)


def dispatch_webhooks(organization_id, event_type: str, payload: dict):
    from apps.webhooks.models import WebhookEndpoint

    endpoints = WebhookEndpoint.objects.filter(
        organization_id=organization_id,
        is_active=True,
    ).filter(models.Q(events__contains=[event_type]) | models.Q(events__contains=['*']))

    for endpoint in endpoints:
        deliver_webhook.delay(str(endpoint.id), event_type, payload)
