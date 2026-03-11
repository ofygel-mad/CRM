import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_add_branches'),
        ('users', '0002_membership'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationmembership',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='organizations.branch'),
        ),
    ]
