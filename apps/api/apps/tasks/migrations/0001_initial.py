from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('deals', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True)),
                ('priority', models.CharField(max_length=10, choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')], default='medium')),
                ('status', models.CharField(max_length=15, choices=[('open', 'Открыта'), ('done', 'Завершена'), ('cancelled', 'Отменена')], default='open')),
                ('due_at', models.DateTimeField(null=True, blank=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('assigned_to', models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')),
                ('created_by', models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')),
                ('customer', models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')),
                ('deal', models.ForeignKey('deals.Deal', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')),
                ('organization', models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='tasks')),
            ],
            options={'db_table': 'tasks'},
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['organization', 'assigned_to', 'status'], name='tasks_org_assignee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['organization', 'due_at'], name='tasks_org_due_idx'),
        ),
    ]
