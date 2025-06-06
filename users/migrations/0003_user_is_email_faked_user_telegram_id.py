# Generated by Django 5.1.3 on 2025-01-16 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_friendshiprequest_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_email_faked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='telegram_id',
            field=models.BigIntegerField(blank=True, db_index=True, null=True),
        ),
    ]
