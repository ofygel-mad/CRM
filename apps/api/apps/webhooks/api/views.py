import secrets

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsOrgAdmin
from apps.webhooks.models import WebhookDelivery, WebhookEndpoint


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'url', 'events', 'is_active', 'description', 'failure_count', 'created_at']
        read_only_fields = ['id', 'failure_count', 'created_at']

    def create(self, validated_data):
        validated_data['secret'] = secrets.token_hex(32)
        return super().create(validated_data)


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = ['id', 'event_type', 'status_code', 'success', 'duration_ms', 'attempted_at', 'response']


class WebhookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrgAdmin]
    serializer_class = WebhookSerializer

    def get_queryset(self):
        return WebhookEndpoint.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['get'], url_path='deliveries')
    def deliveries(self, request, pk=None):
        endpoint = self.get_object()
        queryset = endpoint.deliveries.all()[:50]
        return Response(DeliverySerializer(queryset, many=True).data)

    @action(detail=True, methods=['post'], url_path='test')
    def test(self, request, pk=None):
        from apps.webhooks.tasks import deliver_webhook

        endpoint = self.get_object()
        deliver_webhook.delay(str(endpoint.id), 'test.ping', {'message': 'Тестовый webhook от CRM'})
        return Response({'detail': 'Отправлено'})
