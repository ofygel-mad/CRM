from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_add_bin_iin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, db_index=True, max_length=32),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['organization', '-created_at'], name='customers_org_created_desc_idx'),
        ),
    ]
