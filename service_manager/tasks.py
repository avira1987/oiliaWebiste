from datetime import datetime, timedelta
from django.utils import timezone
from .models import Service
from .services import SMSService

def send_service_reminders():
    """ارسال یادآوری سرویس به مشتریان"""
    # خودروهایی که 3 ماه از آخرین سرویس آنها گذشته است
    three_months_ago = timezone.now() - timedelta(days=90)
    services = Service.objects.filter(
        service_date__lte=three_months_ago
    ).select_related('car')
    
    sms_service = SMSService()
    for service in services:
        sms_service.send_service_reminder(service.car) 