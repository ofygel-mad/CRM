from django.db import models

from apps.core.models import BaseModel


class SpreadsheetStyleSnapshot(BaseModel):
    version = models.ForeignKey(
        "spreadsheets.SpreadsheetVersion",
        on_delete=models.CASCADE,
        related_name="style_snapshots",
    )
    sheet_name = models.CharField(max_length=255)
    range_ref = models.CharField(max_length=64)
    style_json = models.JSONField(default=dict, blank=True)
    merged_ranges_json = models.JSONField(default=list, blank=True)
    column_widths_json = models.JSONField(default=dict, blank=True)
    row_heights_json = models.JSONField(default=dict, blank=True)
    conditional_formats_json = models.JSONField(default=list, blank=True)
    data_validations_json = models.JSONField(default=list, blank=True)
    freeze_panes_json = models.JSONField(default=dict, blank=True)
    filters_json = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "spreadsheet_style_snapshots"
        indexes = [models.Index(fields=["version", "sheet_name"])]

    def __str__(self) -> str:
        return f"{self.sheet_name}:{self.range_ref}"
