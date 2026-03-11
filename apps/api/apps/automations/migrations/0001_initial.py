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
            name='AutomationAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('action_type', models.CharField(max_length=100)),
                ('config_json', models.JSONField(default=dict)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('is_enabled', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'automation_rule_actions',
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='AutomationTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('trigger_type', models.CharField(max_length=100)),
                ('default_conditions', models.JSONField(default=list)),
                ('default_actions', models.JSONField(default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'automation_templates',
            },
        ),
        migrations.CreateModel(
            name='DomainEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('event_type', models.CharField(db_index=True, max_length=100)),
                ('entity_type', models.CharField(max_length=50)),
                ('entity_id', models.UUIDField()),
                ('source', models.CharField(default='system', max_length=50)),
                ('payload_json', models.JSONField(default=dict)),
                ('occurred_at', models.DateTimeField()),
                ('dedupe_key', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('is_processed', models.BooleanField(db_index=True, default=False)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.organization')),
            ],
            options={
                'db_table': 'domain_events',
            },
        ),
        migrations.CreateModel(
            name='AutomationRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('trigger_type', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('active', 'Активно'), ('paused', 'Приостановлено'), ('archived', 'Архив')], default='active', max_length=20)),
                ('is_template_based', models.BooleanField(default=False)),
                ('template_code', models.CharField(blank=True, max_length=100)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='users.user')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automation_rules', to='organizations.organization')),
            ],
            options={
                'db_table': 'automation_rules',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AutomationExecution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('entity_type', models.CharField(max_length=50)),
                ('entity_id', models.UUIDField()),
                ('status', models.CharField(choices=[('pending', 'Ожидает'), ('running', 'Выполняется'), ('completed', 'Выполнено'), ('partial', 'Частично'), ('failed', 'Ошибка'), ('skipped', 'Пропущено')], default='pending', max_length=20)),
                ('attempts', models.PositiveSmallIntegerField(default=0)),
                ('idempotency_key', models.CharField(max_length=255, unique=True)),
                ('execution_depth', models.PositiveSmallIntegerField(default=0)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('error_text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='executions', to='automations.domainevent')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.organization')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='executions', to='automations.automationrule')),
                ('triggered_by_execution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='automations.automationexecution')),
            ],
            options={
                'db_table': 'automation_executions',
            },
        ),
        migrations.CreateModel(
            name='AutomationExecutionAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('action_type', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Ожидает'), ('completed', 'Выполнено'), ('failed', 'Ошибка')], default='pending', max_length=20)),
                ('attempts', models.PositiveSmallIntegerField(default=0)),
                ('result_json', models.JSONField(blank=True, null=True)),
                ('error_text', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='automations.automationaction')),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='automations.automationexecution')),
            ],
            options={
                'db_table': 'automation_execution_actions',
            },
        ),
        migrations.CreateModel(
            name='AutomationConditionGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('operator', models.CharField(default='AND', max_length=10)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='condition_groups', to='automations.automationrule')),
            ],
            options={
                'db_table': 'automation_rule_condition_groups',
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='AutomationCondition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('field_path', models.CharField(max_length=255)),
                ('operator', models.CharField(max_length=50)),
                ('value_json', models.JSONField(blank=True, null=True)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='automations.automationconditiongroup')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='automations.automationrule')),
            ],
            options={
                'db_table': 'automation_rule_conditions',
                'ordering': ['position'],
            },
        ),
        migrations.AddField(
            model_name='automationaction',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='automations.automationrule'),
        ),
        migrations.AddIndex(
            model_name='automationrule',
            index=models.Index(fields=['organization', 'trigger_type', 'status'], name='automation__organiz_63f42d_idx'),
        ),
        migrations.AddIndex(
            model_name='domainevent',
            index=models.Index(fields=['organization', 'event_type', '-occurred_at'], name='domain_even_organiz_57c8c2_idx'),
        ),
        migrations.AddIndex(
            model_name='domainevent',
            index=models.Index(fields=['organization', 'entity_type', 'entity_id'], name='domain_even_organiz_050634_idx'),
        ),
        migrations.AddIndex(
            model_name='automationexecution',
            index=models.Index(fields=['organization', 'rule', '-created_at'], name='automation__organiz_82389b_idx'),
        ),
        migrations.AddIndex(
            model_name='automationexecution',
            index=models.Index(fields=['status', '-created_at'], name='automation__status_7e3d58_idx'),
        ),
    ]
