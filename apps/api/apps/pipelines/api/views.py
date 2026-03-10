from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from ..models import Pipeline, PipelineStage
from ..serializers import PipelineSerializer, PipelineStageSerializer
from apps.core.services import ensure_default_pipeline


class PipelineViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PipelineSerializer

    def get_queryset(self):
        return Pipeline.objects.filter(
            organization=self.request.user.organization,
            is_archived=False,
        ).prefetch_related('stages')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'], url_path='stages/reorder')
    def reorder_stages(self, request, pk=None):
        """
        { "order": ["stage-id-1", "stage-id-2", ...] }
        Обновляет position по порядку переданных id.
        """
        pipeline = self.get_object()
        order = request.data.get('order', [])

        with transaction.atomic():
            for position, stage_id in enumerate(order):
                PipelineStage.objects.filter(
                    id=stage_id,
                    pipeline=pipeline,
                ).update(position=position)

        return Response(PipelineSerializer(pipeline).data)

    @action(detail=True, methods=['post'], url_path='stages')
    def add_stage(self, request, pk=None):
        pipeline = self.get_object()
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'name': ['This field is required.']}, status=400)

        max_pos = pipeline.stages.order_by('-position').values_list('position', flat=True).first()
        stage = PipelineStage.objects.create(
            pipeline=pipeline,
            name=name,
            stage_type=request.data.get('stage_type', 'open'),
            color=request.data.get('color', '#6B7280'),
            position=(max_pos or 0) + 1,
        )
        return Response(PipelineStageSerializer(stage).data, status=201)

    @action(detail=True, methods=['patch'], url_path='stages/(?P<stage_id>[^/.]+)')
    def update_stage(self, request, pk=None, stage_id=None):
        pipeline = self.get_object()
        try:
            stage = PipelineStage.objects.get(id=stage_id, pipeline=pipeline)
        except PipelineStage.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

        for field in ('name', 'color', 'stage_type'):
            if field in request.data:
                setattr(stage, field, request.data[field])
        stage.save()
        return Response(PipelineStageSerializer(stage).data)

    @action(detail=True, methods=['delete'], url_path='stages/(?P<stage_id>[^/.]+)')
    def delete_stage(self, request, pk=None, stage_id=None):
        pipeline = self.get_object()
        try:
            stage = PipelineStage.objects.get(id=stage_id, pipeline=pipeline)
        except PipelineStage.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

        # Нельзя удалить если есть сделки
        if stage.deals.filter(deleted_at__isnull=True).exists():
            return Response({'detail': 'Cannot delete stage with active deals.'}, status=409)

        stage.delete()
        return Response(status=204)
