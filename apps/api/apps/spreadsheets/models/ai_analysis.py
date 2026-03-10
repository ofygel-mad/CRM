from django.db import models

from apps.core.models import BaseModel
from apps.spreadsheets.domain import SpreadsheetAIAnalysisType


class SpreadsheetAIAnalysis(BaseModel):
    document = models.ForeignKey(
        "spreadsheets.SpreadsheetDocument",
        on_delete=models.CASCADE,
        related_name="ai_analyses",
    )
    version = models.ForeignKey(
        "spreadsheets.SpreadsheetVersion",
        on_delete=models.CASCADE,
        related_name="ai_analyses",
    )
    analysis_type = models.CharField(
        max_length=64,
        choices=SpreadsheetAIAnalysisType.choices,
        db_index=True,
    )
    result_json = models.JSONField(default=dict)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "spreadsheet_ai_analyses"
        indexes = [
            models.Index(fields=["document", "analysis_type", "created_at"]),
            models.Index(fields=["version", "analysis_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.analysis_type}:{self.document_id}"
