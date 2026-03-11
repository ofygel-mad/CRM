from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_custom_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='currency',
            field=models.CharField(default='KZT', max_length=3),
        ),
    ]
