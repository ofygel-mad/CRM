from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0002_activity_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='currency',
            field=models.CharField(default='KZT', max_length=3),
        ),
    ]
