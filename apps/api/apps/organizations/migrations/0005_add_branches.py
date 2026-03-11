import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_add_email_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='organizations.organization')),
            ],
            options={'db_table': 'branches', 'ordering': ['name']},
        ),
    ]
