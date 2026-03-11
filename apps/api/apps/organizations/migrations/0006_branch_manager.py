import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_add_branches'),
        ('users', '0003_membership_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_branches', to='users.user'),
        ),
    ]
