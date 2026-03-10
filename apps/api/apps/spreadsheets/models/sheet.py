from django.db import models

from apps.core.models import BaseModel


class SpreadsheetSheet(BaseModel):
    version = models.ForeignKey(
        "spreadsheets.SpreadsheetVersion",
        on_delete=models.CASCADE,
        related_name="sheets",
    )
    name = models.CharField(max_length=255)
    position = models.PositiveIntegerField()
    max_row = models.PositiveIntegerField(default=0)
    max_col = models.PositiveIntegerField(default=0)
    metadata_json = models.JSONField(default=dict, blank=True)
    detected_table_ranges_json = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "spreadsheet_sheets"
        indexes = [models.Index(fields=["version", "position"])]
        constraints = [
            models.UniqueConstraint(
                fields=["version", "name"],
                name="uq_spreadsheet_sheet_name_per_version",
            ),
            models.UniqueConstraint(
                fields=["version", "position"],
                name="uq_spreadsheet_sheet_position_per_version",
            ),
        ]

    def __str__(self) -> str:
        return self.name
