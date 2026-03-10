from django.db import models

from apps.core.models import BaseModel
from apps.spreadsheets.domain import SpreadsheetJobStatus


class SpreadsheetExportJob(BaseModel):
    organization_id = models.UUIDField(db_index=True)
    document = models.ForeignKey(
        "spreadsheets.SpreadsheetDocument",
        on_delete=models.CASCADE,
        related_name="export_jobs",
    )
    version = models.ForeignKey(
        "spreadsheets.SpreadsheetVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="export_jobs",
    )
    status = models.CharField(
        max_length=32,
        choices=SpreadsheetJobStatus.choices,
        default=SpreadsheetJobStatus.PENDING,
        db_index=True,
    )
    output_storage_key = models.CharField(max_length=1024, blank=True)
    summary_json = models.JSONField(default=dict, blank=True)
    error_text = models.TextField(blank=True)
    created_by_user_id = models.UUIDField(db_index=True, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "spreadsheet_export_jobs"
        indexes = [
            models.Index(fields=["organization_id", "status", "created_at"]),
            models.Index(fields=["document", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_id}:{self.status}"
