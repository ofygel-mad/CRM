from rest_framework import serializers
from .models import ImportJob


class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportJob
        fields = [
            'id', 'import_type', 'status', 'file_name',
            'total_rows', 'imported_rows', 'failed_rows',
            'column_mapping', 'preview_json', 'result_json',
            'error_message', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
