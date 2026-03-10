from django.db import models

from apps.core.models import BaseModel
from apps.spreadsheets.domain import SpreadsheetVersionSourceType


class SpreadsheetVersion(BaseModel):
    document = models.ForeignKey(
        "spreadsheets.SpreadsheetDocument",
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    source_type = models.CharField(
        max_length=32,
        choices=SpreadsheetVersionSourceType.choices,
        default=SpreadsheetVersionSourceType.UPLOADED,
        db_index=True,
    )
    storage_key = models.CharField(max_length=1024)
    checksum = models.CharField(max_length=128, blank=True)
    created_by_user_id = models.UUIDField(db_index=True, null=True, blank=True)
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "spreadsheet_versions"
        indexes = [
            models.Index(fields=["document", "version_number"]),
            models.Index(fields=["document", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "version_number"],
                name="uq_spreadsheet_version_per_document",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.document_id} v{self.version_number}"
