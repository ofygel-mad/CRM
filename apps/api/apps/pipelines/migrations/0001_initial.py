from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('customers', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('is_default', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('organization', models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='pipelines')),
            ],
            options={'db_table': 'pipelines'},
        ),
        migrations.CreateModel(
            name='PipelineStage',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('stage_type', models.CharField(max_length=10, choices=[('open', 'Open'), ('won', 'Won'), ('lost', 'Lost')], default='open')),
                ('color', models.CharField(max_length=7, blank=True, default='')),
                ('pipeline', models.ForeignKey('pipelines.Pipeline', on_delete=models.CASCADE, related_name='stages')),
            ],
            options={'db_table': 'pipeline_stages', 'ordering': ['position']},
        ),
    ]
