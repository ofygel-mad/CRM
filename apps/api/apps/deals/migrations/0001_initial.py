from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('pipelines', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)),
                ('currency', models.CharField(max_length=3, default='RUB')),
                ('status', models.CharField(max_length=10, choices=[('open', 'Открыта'), ('won', 'Выиграна'), ('lost', 'Проиграна'), ('paused', 'Пауза')], default='open')),
                ('expected_close_date', models.DateField(null=True, blank=True)),
                ('closed_at', models.DateTimeField(null=True, blank=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('customer', models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='deals')),
                ('organization', models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='deals')),
                ('owner', models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_deals')),
                ('pipeline', models.ForeignKey('pipelines.Pipeline', on_delete=models.CASCADE, related_name='deals')),
                ('stage', models.ForeignKey('pipelines.PipelineStage', on_delete=models.CASCADE, related_name='deals')),
            ],
            options={'db_table': 'deals'},
        ),
        migrations.AddIndex(
            model_name='deal',
            index=models.Index(fields=['organization', 'pipeline', 'stage'], name='deals_org_pipe_stage_idx'),
        ),
        migrations.AddIndex(
            model_name='deal',
            index=models.Index(fields=['organization', 'status'], name='deals_org_status_idx'),
        ),
    ]
