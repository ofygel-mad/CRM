from django.db import models

from apps.core.models import BaseModel
from apps.spreadsheets.domain import SpreadsheetDocumentStatus


class SpreadsheetDocument(BaseModel):
    organization_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=512)
    mime_type = models.CharField(max_length=255, blank=True)
    uploaded_by_user_id = models.UUIDField(db_index=True, null=True, blank=True)
    current_version = models.ForeignKey(
        "spreadsheets.SpreadsheetVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    storage_key = models.CharField(max_length=1024)
    checksum = models.CharField(max_length=128, blank=True)
    status = models.CharField(
        max_length=32,
        choices=SpreadsheetDocumentStatus.choices,
        default=SpreadsheetDocumentStatus.UPLOADED,
        db_index=True,
    )
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "spreadsheet_documents"
        indexes = [
            models.Index(fields=["organization_id", "status"]),
            models.Index(fields=["organization_id", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.original_filename})"
