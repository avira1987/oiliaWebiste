# Generated by Django 4.2.20 on 2025-03-27 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_manager', '0003_remove_service_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='email',
        ),
    ]
