import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def process_import_job(self, import_job_id: str):
    """
    Обрабатывает ImportJob: читает файл, валидирует, создаёт записи.
    Шаги: upload → preview → mapping → validate → import → result
    """
    from apps.imports.models import ImportJob
    from apps.imports.services.processor import ImportProcessor

    try:
        job = ImportJob.objects.select_related('organization', 'created_by').get(id=import_job_id)

        if job.status not in ('mapping_confirmed', 'pending'):
            logger.warning('ImportJob %s in wrong status: %s', import_job_id, job.status)
            return

        job.status = 'processing'
        job.save(update_fields=['status'])

        processor = ImportProcessor(job)
        result = processor.run()

        job.status = 'completed'
        job.result_json = result
        job.save(update_fields=['status', 'result_json'])

    except ImportJob.DoesNotExist:
        logger.error('ImportJob %s not found', import_job_id)
    except Exception as exc:
        logger.exception('ImportJob %s failed: %s', import_job_id, exc)
        try:
            from apps.imports.models import ImportJob

            ImportJob.objects.filter(id=import_job_id).update(
                status='failed',
                result_json={'error': str(exc)},
            )
        except Exception:
            pass
        raise self.retry(exc=exc)


@shared_task
def analyze_import_file(import_job_id: str):
    """Читает Excel/CSV файл и генерирует preview + auto-mapping."""
    from apps.imports.models import ImportJob
    from apps.imports.services.file_analyzer import analyze_file

    try:
        job = ImportJob.objects.get(id=import_job_id)
        preview_data = analyze_file(job.file_path, job.import_type)

        job.status = 'mapping'
        job.preview_json = preview_data
        job.save(update_fields=['status', 'preview_json'])

    except Exception as exc:
        logger.exception('Failed to analyze import file for job %s: %s', import_job_id, exc)
        ImportJob.objects.filter(id=import_job_id).update(status='failed')
