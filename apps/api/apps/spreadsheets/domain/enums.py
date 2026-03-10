from django.db import models


class SpreadsheetDocumentStatus(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded"
    ANALYZING = "analyzing", "Analyzing"
    READY = "ready", "Ready"
    SYNC_ERROR = "sync_error", "Sync error"
    ARCHIVED = "archived", "Archived"


class SpreadsheetVersionSourceType(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded"
    REGENERATED = "regenerated", "Regenerated"
    SYNCED_FROM_DB = "synced_from_db", "Synced from DB"
    AI_MODIFIED = "ai_modified", "AI modified"


class SpreadsheetSyncDirection(models.TextChoices):
    TO_DB = "to_db", "To DB"
    FROM_DB = "from_db", "From DB"
    BIDIRECTIONAL = "bidirectional", "Bidirectional"


class SpreadsheetJobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    PARTIAL = "partial", "Partial"
    FAILED = "failed", "Failed"


class SpreadsheetMappingEntityType(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    DEAL = "deal", "Deal"
    TASK = "task", "Task"
    ACTIVITY = "activity", "Activity"
    CUSTOM = "custom", "Custom"


class SpreadsheetMappingSyncMode(models.TextChoices):
    IMPORT_ONLY = "import_only", "Import only"
    EXPORT_ONLY = "export_only", "Export only"
    BIDIRECTIONAL = "bidirectional", "Bidirectional"
    TEMPLATE_ONLY = "template_only", "Template only"


class SpreadsheetAIAnalysisType(models.TextChoices):
    MAPPING_SUGGESTION = "mapping_suggestion", "Mapping suggestion"
    ANOMALY_REPORT = "anomaly_report", "Anomaly report"
    FORMULA_EXPLANATION = "formula_explanation", "Formula explanation"
    SYNC_RECOMMENDATION = "sync_recommendation", "Sync recommendation"
