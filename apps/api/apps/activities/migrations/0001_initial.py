from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('tasks', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=30, choices=[('note', 'Заметка'), ('call', 'Звонок'), ('message', 'Сообщение'), ('status_change', 'Смена статуса'), ('stage_change', 'Смена стадии'), ('deal_created', 'Сделка создана'), ('task_created', 'Задача создана'), ('task_done', 'Задача выполнена')])),
                ('payload', models.JSONField(default=dict)),
                ('actor', models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)),
                ('customer', models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')),
                ('deal', models.ForeignKey('deals.Deal', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')),
                ('organization', models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='activities')),
                ('task', models.ForeignKey('tasks.Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')),
            ],
            options={'db_table': 'activities', 'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='activity',
            index=models.Index(fields=['organization', 'customer', '-created_at'], name='act_org_cust_created_idx'),
        ),
        migrations.AddIndex(
            model_name='activity',
            index=models.Index(fields=['organization', 'deal', '-created_at'], name='act_org_deal_created_idx'),
        ),
    ]
