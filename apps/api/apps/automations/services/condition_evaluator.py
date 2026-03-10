"""
Оценивает условия AutomationRule против контекста события.

Поддерживаемые операторы:
  eq, neq, contains, not_contains, starts_with, ends_with,
  gt, gte, lt, lte, is_empty, is_not_empty, in, not_in
"""
from __future__ import annotations
import logging
from typing import Any
from apps.automations.models import AutomationRule, DomainEvent

logger = logging.getLogger(__name__)


def evaluate_rule(rule: AutomationRule, event: DomainEvent, context: dict) -> bool:
    """Возвращает True если rule должен выполняться для данного события/контекста."""
    groups = list(rule.condition_groups.prefetch_related('conditions').all())

    if not groups:
        # Нет условий — всегда выполняется
        return True

    # Группы соединяются через AND
    for group in groups:
        if not _evaluate_group(group, context):
            return False
    return True


def _evaluate_group(group, context: dict) -> bool:
    conditions = list(group.conditions.all())
    if not conditions:
        return True

    results = [_evaluate_condition(c, context) for c in conditions]

    if group.operator == 'OR':
        return any(results)
    # Default AND
    return all(results)


def _evaluate_condition(condition, context: dict) -> bool:
    try:
        actual = _resolve_path(condition.field_path, context)
        expected = condition.value_json

        op = condition.operator
        return _apply_operator(op, actual, expected)

    except Exception as exc:
        logger.warning('Condition eval error (field=%s op=%s): %s', condition.field_path, condition.operator, exc)
        return False


def _resolve_path(path: str, ctx: dict) -> Any:
    """
    Поддерживает dotted paths: 'entity.status', 'payload.amount', 'event.type'
    """
    parts = path.split('.')
    value = ctx
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def _apply_operator(op: str, actual: Any, expected: Any) -> bool:
    if op == 'is_empty':
        return actual is None or actual == '' or actual == []
    if op == 'is_not_empty':
        return actual is not None and actual != '' and actual != []

    if op == 'eq':
        return str(actual) == str(expected) if actual is not None else expected is None
    if op == 'neq':
        return str(actual) != str(expected)

    if op == 'contains':
        return expected in str(actual) if actual else False
    if op == 'not_contains':
        return expected not in str(actual) if actual else True
    if op == 'starts_with':
        return str(actual).startswith(str(expected)) if actual else False
    if op == 'ends_with':
        return str(actual).endswith(str(expected)) if actual else False

    if op in ('gt', 'gte', 'lt', 'lte'):
        try:
            a, e = float(actual), float(expected)
        except (TypeError, ValueError):
            return False
        return {'gt': a > e, 'gte': a >= e, 'lt': a < e, 'lte': a <= e}[op]

    if op == 'in':
        vals = expected if isinstance(expected, list) else [expected]
        return actual in vals
    if op == 'not_in':
        vals = expected if isinstance(expected, list) else [expected]
        return actual not in vals

    logger.warning('Unknown operator: %s', op)
    return False
