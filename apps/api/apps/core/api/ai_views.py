import logging

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def _build_context(org, customer_id=None, deal_id=None) -> str:
    parts = [f'Организация: {org.name} (режим: {org.mode}, валюта: {org.currency})']

    if customer_id:
        try:
            from apps.activities.models import Activity
            from apps.customers.models import Customer

            customer = Customer.objects.get(id=customer_id, organization=org)
            parts.append(
                f'Клиент: {customer.full_name}, компания: {customer.company_name or "—"}, '
                f'статус: {customer.status}, источник: {customer.source or "—"}'
            )
            activities = Activity.objects.filter(customer=customer).order_by('-created_at')[:10]
            if activities:
                parts.append('Последние 10 активностей:')
                for activity in activities:
                    body = (activity.payload or {}).get('body', activity.type)
                    parts.append(f'  [{activity.created_at.strftime("%d.%m.%Y")}] {activity.type}: {str(body)[:150]}')
        except Exception as exc:
            logger.debug('AI ctx customer error: %s', exc)

    if deal_id:
        try:
            from apps.deals.models import Deal

            deal = Deal.objects.select_related('stage', 'pipeline', 'customer').get(id=deal_id, organization=org)
            parts.append(
                f'Сделка: {deal.title}, сумма: {deal.amount} {deal.currency}, '
                f'этап: {deal.stage.name}, воронка: {deal.pipeline.name}, статус: {deal.status}'
            )
        except Exception as exc:
            logger.debug('AI ctx deal error: %s', exc)

    return '\n'.join(parts)


SYSTEM_PROMPT = """Ты — ИИ-ассистент CRM системы для казахстанского бизнеса.
Отвечай на русском языке. Будь кратким, деловым и полезным.
Используй контекст о клиентах и сделках, который тебе предоставлен.
Не придумывай данные которых нет в контексте. Формат ответа — plain text."""


class AiAssistantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = (request.data.get('message') or '').strip()
        customer_id = request.data.get('customer_id')
        deal_id = request.data.get('deal_id')
        history = request.data.get('history', [])

        if not message:
            return Response({'error': 'message обязателен'}, status=400)

        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        if not api_key:
            return Response({'error': 'ANTHROPIC_API_KEY не настроен'}, status=503)

        context = _build_context(request.user.organization, customer_id=customer_id, deal_id=deal_id)
        messages = list(history[-10:])
        messages.append({'role': 'user', 'content': message})

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model='claude-3-5-haiku-20241022',
                max_tokens=1024,
                system=f'{SYSTEM_PROMPT}\n\nТекущий контекст:\n{context}',
                messages=messages,
            )
            reply = response.content[0].text
            return Response({
                'reply': reply,
                'tokens': response.usage.input_tokens + response.usage.output_tokens,
                'history': [*history, {'role': 'user', 'content': message}, {'role': 'assistant', 'content': reply}],
            })
        except Exception as exc:
            logger.error('AI request failed: %s', exc)
            return Response({'error': f'Ошибка ИИ: {exc}'}, status=502)
