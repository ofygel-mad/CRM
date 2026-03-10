from rest_framework import serializers
from .models import (
    AutomationRule, AutomationConditionGroup, AutomationCondition,
    AutomationAction, AutomationExecution, AutomationTemplate,
)


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationCondition
        fields = ['id', 'field_path', 'operator', 'value_json']


class ConditionGroupSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(many=True, read_only=True)

    class Meta:
        model = AutomationConditionGroup
        fields = ['id', 'operator', 'conditions']


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationAction
        fields = ['id', 'action_type', 'config_json', 'position']


class AutomationRuleSerializer(serializers.ModelSerializer):
    condition_groups = ConditionGroupSerializer(many=True, read_only=True)
    actions = ActionSerializer(many=True, read_only=True)
    executions_count = serializers.SerializerMethodField()
    last_executed_at = serializers.SerializerMethodField()

    class Meta:
        model = AutomationRule
        fields = [
            'id', 'name', 'description', 'trigger_type', 'status',
            'is_template_based', 'template_code',
            'condition_groups', 'actions',
            'executions_count', 'last_executed_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_executions_count(self, obj):
        return obj.executions.count() if hasattr(obj, 'executions') else 0

    def get_last_executed_at(self, obj):
        last = obj.executions.order_by('-created_at').first()
        return last.created_at.isoformat() if last else None


class AutomationRuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = ['name', 'description', 'trigger_type', 'status']


class AutomationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationTemplate
        fields = ['id', 'code', 'name', 'description', 'trigger_type',
                  'default_conditions', 'default_actions']


class AutomationExecutionSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    action_logs = serializers.SerializerMethodField()

    class Meta:
        model = AutomationExecution
        fields = ['id', 'rule_name', 'status', 'entity_type', 'entity_id',
                  'started_at', 'finished_at', 'error_text', 'action_logs', 'created_at']

    def get_action_logs(self, obj):
        return [
            {
                'action_type': al.action_type,
                'status': al.status,
                'error_text': al.error_text,
            }
            for al in obj.action_logs.all()
        ]
