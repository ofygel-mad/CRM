from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_currency_default_kzt'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='email_from',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='organization',
            name='email_host',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='organization',
            name='email_password',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name='organization',
            name='email_port',
            field=models.PositiveSmallIntegerField(default=587),
        ),
        migrations.AddField(
            model_name='organization',
            name='email_use_tls',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='email_username',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
