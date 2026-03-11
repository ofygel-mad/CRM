import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0004_add_email_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookEndpoint',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(max_length=500)),
                ('secret', models.CharField(blank=True, max_length=64)),
                ('events', models.JSONField(default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('failure_count', models.PositiveSmallIntegerField(default=0)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhooks', to='organizations.organization')),
            ],
            options={'db_table': 'webhook_endpoints'},
        ),
        migrations.CreateModel(
            name='WebhookDelivery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(max_length=100)),
                ('payload', models.JSONField()),
                ('status_code', models.PositiveSmallIntegerField(null=True)),
                ('response', models.TextField(blank=True)),
                ('duration_ms', models.PositiveIntegerField(null=True)),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField(default=False)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='webhooks.webhookendpoint')),
            ],
            options={
                'db_table': 'webhook_deliveries',
                'ordering': ['-attempted_at'],
                'indexes': [models.Index(fields=['endpoint', '-attempted_at'], name='webhook_deli_endpoin_5ec143_idx')],
            },
        ),
    ]
