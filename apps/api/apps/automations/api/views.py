from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from apps.automations.models import (
    AutomationRule, AutomationConditionGroup, AutomationCondition,
    AutomationAction, AutomationExecution, AutomationTemplate,
)
from apps.automations.serializers import (
    AutomationRuleSerializer, AutomationRuleWriteSerializer,
    AutomationTemplateSerializer, AutomationExecutionSerializer,
)


class AutomationRuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AutomationRule.objects.filter(
            organization=self.request.user.organization,
        ).prefetch_related(
            'condition_groups__conditions', 'actions', 'executions',
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return AutomationRuleWriteSerializer
        return AutomationRuleSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle_status(self, request, pk=None):
        rule = self.get_object()
        if rule.status == AutomationRule.Status.ACTIVE:
            rule.status = AutomationRule.Status.PAUSED
        else:
            rule.status = AutomationRule.Status.ACTIVE
        rule.save(update_fields=['status'])
        return Response(AutomationRuleSerializer(rule).data)

    @action(detail=True, methods=['post'], url_path='conditions')
    def set_conditions(self, request, pk=None):
        """
        Принимает:
          { "groups": [ { "operator": "AND", "conditions": [ { "field_path", "operator", "value_json" } ] } ] }
        Полностью заменяет условия правила.
        """
        rule = self.get_object()
        groups_data = request.data.get('groups', [])

        with transaction.atomic():
            rule.condition_groups.all().delete()
            for g_data in groups_data:
                group = AutomationConditionGroup.objects.create(
                    rule=rule,
                    operator=g_data.get('operator', 'AND'),
                )
                for c_data in g_data.get('conditions', []):
                    AutomationCondition.objects.create(
                        group=group,
                        field_path=c_data['field_path'],
                        operator=c_data['operator'],
                        value_json=c_data.get('value_json'),
                    )

        return Response(AutomationRuleSerializer(rule).data)

    @action(detail=True, methods=['post'], url_path='actions')
    def set_actions(self, request, pk=None):
        """
        Принимает:
          { "actions": [ { "action_type", "config_json", "position" } ] }
        """
        rule = self.get_object()
        actions_data = request.data.get('actions', [])

        with transaction.atomic():
            rule.actions.all().delete()
            for i, a_data in enumerate(actions_data):
                AutomationAction.objects.create(
                    rule=rule,
                    action_type=a_data['action_type'],
                    config_json=a_data.get('config_json', {}),
                    position=a_data.get('position', i),
                )

        return Response(AutomationRuleSerializer(rule).data)

    @action(detail=False, methods=['get'])
    def templates(self, request):
        templates = AutomationTemplate.objects.filter(is_active=True)
        return Response(AutomationTemplateSerializer(templates, many=True).data)

    @action(detail=False, methods=['post'], url_path='from_template')
    def create_from_template(self, request):
        """Создаёт AutomationRule из шаблона по его коду."""
        template_code = request.data.get('template_code')
        try:
            template = AutomationTemplate.objects.get(code=template_code, is_active=True)
        except AutomationTemplate.DoesNotExist:
            return Response({'detail': 'Template not found'}, status=404)

        with transaction.atomic():
            rule = AutomationRule.objects.create(
                organization=request.user.organization,
                name=template.name,
                description=template.description,
                trigger_type=template.trigger_type,
                status=AutomationRule.Status.ACTIVE,
                is_template_based=True,
                template_code=template.code,
                created_by=request.user,
            )
            # Создаём условия
            for g_data in (template.default_conditions or []):
                group = AutomationConditionGroup.objects.create(
                    rule=rule,
                    operator=g_data.get('operator', 'AND'),
                )
                for c_data in g_data.get('conditions', []):
                    AutomationCondition.objects.create(
                        group=group,
                        field_path=c_data['field_path'],
                        operator=c_data['operator'],
                        value_json=c_data.get('value_json'),
                    )
            # Создаём действия
            for i, a_data in enumerate(template.default_actions or []):
                AutomationAction.objects.create(
                    rule=rule,
                    action_type=a_data['action_type'],
                    config_json=a_data.get('config_json', {}),
                    position=i,
                )

        return Response(AutomationRuleSerializer(rule).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def executions(self, request):
        qs = AutomationExecution.objects.filter(
            organization=request.user.organization,
        ).select_related('rule').prefetch_related('action_logs').order_by('-created_at')[:50]
        return Response(AutomationExecutionSerializer(qs, many=True).data)
