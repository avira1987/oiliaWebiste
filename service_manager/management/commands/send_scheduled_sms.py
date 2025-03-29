from django.core.management.base import BaseCommand
from django.utils import timezone
from service_manager.models import SMSLog

class Command(BaseCommand):
    help = 'ارسال پیامک‌های برنامه‌ریزی شده'

    def handle(self, *args, **options):
        # پیدا کردن پیامک‌های برنامه‌ریزی شده که زمان ارسال آنها فرا رسیده است
        scheduled_sms = SMSLog.objects.filter(
            status='scheduled',
            scheduled_for__lte=timezone.now()
        )

        success_count = 0
        failed_count = 0

        for sms in scheduled_sms:
            if sms.send():
                success_count += 1
            else:
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'تعداد {success_count} پیامک با موفقیت ارسال شد و {failed_count} پیامک ناموفق بود.'
            )
        ) 