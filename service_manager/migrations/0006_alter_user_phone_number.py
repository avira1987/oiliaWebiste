# Generated by Django 4.2.20 on 2025-03-27 20:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_manager', '0005_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=11, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد', regex='^09\\d{9}$')]),
        ),
    ]
