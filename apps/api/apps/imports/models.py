import uuid
from django.db import models


class ImportJob(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидание'
        MAPPING = 'mapping', 'Маппинг'
        MAPPING_CONFIRMED = 'mapping_confirmed', 'Маппинг подтверждён'
        PROCESSING = 'processing', 'Обработка'
        COMPLETED = 'completed', 'Завершён'
        FAILED = 'failed', 'Ошибка'

    class ImportType(models.TextChoices):
        CUSTOMER = 'customer', 'Клиент'
        DEAL = 'deal', 'Сделка'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='import_jobs')
    created_by = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)
    import_type = models.CharField(max_length=20, choices=ImportType.choices, default=ImportType.CUSTOMER)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    file_name = models.CharField(max_length=255)
    file_path = models.TextField(blank=True)
    total_rows = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    column_mapping = models.JSONField(default=dict)
    preview_json = models.JSONField(default=dict)
    result_json = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'import_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f'ImportJob({self.import_type}, {self.status}, {self.file_name})'
