import os
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from apps.imports.models import ImportJob
from apps.imports.serializers import ImportJobSerializer
from apps.imports.services.file_analyzer import analyze_file

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'imports')
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}


class ImportJobViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ImportJobSerializer

    def get_queryset(self):
        return ImportJob.objects.filter(organization=self.request.user.organization)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'Файл обязателен'}, status=400)
        if file.size > MAX_FILE_SIZE:
            return Response({'error': 'Максимальный размер файла — 10 МБ'}, status=400)

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response({'error': f'Поддерживаются: {", ".join(ALLOWED_EXTENSIONS)}'}, status=400)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        safe_name = f"{request.user.id}_{file.name.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        import_type = request.data.get('import_type', 'customer')
        job = ImportJob.objects.create(
            organization=request.user.organization,
            created_by=request.user,
            import_type=import_type,
            file_name=file.name,
            file_path=file_path,
            status=ImportJob.Status.PENDING,
        )

        from apps.imports.tasks import analyze_import_file

        analyze_import_file.delay(str(job.id))

        return Response(ImportJobSerializer(job).data, status=201)

    @action(detail=True, methods=['post'])
    def confirm_mapping(self, request, pk=None):
        job = self.get_object()
        if job.status not in (ImportJob.Status.MAPPING, ImportJob.Status.PENDING):
            return Response({'error': f'Нельзя подтвердить в статусе {job.status}'}, status=400)

        mapping = request.data.get('column_mapping')
        if not mapping:
            return Response({'error': 'column_mapping обязателен'}, status=400)

        job.column_mapping = mapping
        job.status = ImportJob.Status.MAPPING_CONFIRMED
        job.save(update_fields=['column_mapping', 'status'])

        from apps.imports.tasks import process_import_job

        process_import_job.delay(str(job.id))

        return Response(ImportJobSerializer(job).data)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        job = self.get_object()
        return Response({
            'id': str(job.id),
            'status': job.status,
            'total_rows': job.total_rows,
            'imported_rows': job.imported_rows,
            'failed_rows': job.failed_rows,
            'result_json': job.result_json,
            'error_message': job.error_message,
        })
