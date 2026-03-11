import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('organizations', '0002_custom_fields'),
        ('users', '0002_membership'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True)),
                ('notification_type', models.CharField(choices=[('automation', 'Автоматизация'), ('task', 'Задача'), ('deal', 'Сделка'), ('system', 'Система'), ('mention', 'Упоминание')], default='system', max_length=30)),
                ('entity_type', models.CharField(blank=True, max_length=50)),
                ('entity_id', models.UUIDField(blank=True, null=True)),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='organizations.organization')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='users.user')),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read', '-created_at'], name='notificatio_recipie_6c406f_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['organization', '-created_at'], name='notificatio_organiz_378f7a_idx'),
        ),
    ]
