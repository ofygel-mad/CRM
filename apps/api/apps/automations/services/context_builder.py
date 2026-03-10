"""
Строит контекст выполнения автоматизации из DomainEvent.
Контекст — плоский dict для использования в условиях и действиях.
"""
from __future__ import annotations
import logging
from apps.automations.models import DomainEvent

logger = logging.getLogger(__name__)


def build_context(event: DomainEvent) -> dict:
    """
    Возвращает контекст вида:
      {
        'event': { type, entity_type, entity_id, occurred_at },
        'entity': { ...поля объекта },
        'organization': { id, mode },
        'actor': { id, full_name } | None,
        'payload': { ...event payload },
      }
    """
    ctx: dict = {
        'event': {
            'type': event.event_type,
            'entity_type': event.entity_type,
            'entity_id': str(event.entity_id),
            'occurred_at': event.occurred_at.isoformat() if event.occurred_at else None,
        },
        'payload': event.payload_json or {},
        'organization': {
            'id': str(event.organization_id),
            'mode': event.organization.mode if event.organization_id else None,
        },
        'actor': None,
        'entity': {},
    }

    # Actor
    if event.actor_id:
        try:
            ctx['actor'] = {
                'id': str(event.actor_id),
                'full_name': event.actor.full_name if event.actor else '',
            }
        except Exception:
            pass

    # Entity hydration
    try:
        ctx['entity'] = _hydrate_entity(event.entity_type, event.entity_id)
    except Exception as exc:
        logger.warning('Could not hydrate entity %s:%s — %s', event.entity_type, event.entity_id, exc)

    return ctx


def _hydrate_entity(entity_type: str, entity_id) -> dict:
    if entity_type == 'customer':
        from apps.customers.models import Customer
        obj = Customer.objects.select_related('owner').get(id=entity_id)
        return {
            'id': str(obj.id),
            'full_name': obj.full_name,
            'status': obj.status,
            'source': obj.source or '',
            'phone': obj.phone or '',
            'email': obj.email or '',
            'company_name': obj.company_name or '',
            'owner_id': str(obj.owner_id) if obj.owner_id else None,
        }

    if entity_type == 'deal':
        from apps.deals.models import Deal
        obj = Deal.objects.select_related('stage', 'customer', 'owner').get(id=entity_id)
        return {
            'id': str(obj.id),
            'title': obj.title,
            'status': obj.status,
            'amount': float(obj.amount or 0),
            'stage_id': str(obj.stage_id) if obj.stage_id else None,
            'stage_name': obj.stage.name if obj.stage_id else '',
            'stage_type': obj.stage.stage_type if obj.stage_id else '',
            'customer_id': str(obj.customer_id) if obj.customer_id else None,
            'owner_id': str(obj.owner_id) if obj.owner_id else None,
        }

    if entity_type == 'task':
        from apps.tasks.models import Task
        obj = Task.objects.select_related('assigned_to').get(id=entity_id)
        return {
            'id': str(obj.id),
            'title': obj.title,
            'status': obj.status,
            'priority': obj.priority,
            'assigned_to_id': str(obj.assigned_to_id) if obj.assigned_to_id else None,
        }

    return {}
