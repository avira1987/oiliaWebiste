# Generated by Django 4.2.20 on 2025-03-27 19:42

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('service_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='oil_filter_changed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='service',
            name='oil_quantity',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=4),
        ),
        migrations.AddField(
            model_name='service',
            name='owner_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='owner_phone',
            field=models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد', regex='^09\\d{9}$')]),
        ),
        migrations.AddField(
            model_name='service',
            name='plate_number',
            field=models.CharField(blank=True, max_length=7, null=True, validators=[django.core.validators.RegexValidator(message='شماره پلاک باید به فرمت 12ABC34 باشد', regex='^\\d{2}[A-Z]{3}\\d{2}$')]),
        ),
        migrations.AddField(
            model_name='smslog',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='smslog',
            name='scheduled_for',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='smslog',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='car',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='service_manager.car'),
        ),
        migrations.AlterField(
            model_name='smslog',
            name='phone_number',
            field=models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد', regex='^09\\d{9}$')]),
        ),
        migrations.AlterField(
            model_name='smslog',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='smslog',
            name='status',
            field=models.CharField(choices=[('pending', 'در انتظار'), ('sent', 'ارسال شده'), ('failed', 'ناموفق'), ('scheduled', 'برنامه\u200cریزی شده')], default='pending', max_length=20),
        ),
    ]
