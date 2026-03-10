import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('import_type', models.CharField(choices=[('customer', 'Клиент'), ('deal', 'Сделка')], default='customer', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Ожидание'), ('mapping', 'Маппинг'), ('mapping_confirmed', 'Маппинг подтверждён'), ('processing', 'Обработка'), ('completed', 'Завершён'), ('failed', 'Ошибка')], default='pending', max_length=30)),
                ('file_name', models.CharField(max_length=255)),
                ('file_path', models.TextField(blank=True)),
                ('total_rows', models.IntegerField(default=0)),
                ('imported_rows', models.IntegerField(default=0)),
                ('failed_rows', models.IntegerField(default=0)),
                ('column_mapping', models.JSONField(default=dict)),
                ('preview_json', models.JSONField(default=dict)),
                ('result_json', models.JSONField(default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='import_jobs', to='organizations.organization')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'import_jobs', 'ordering': ['-created_at']},
        ),
    ]
