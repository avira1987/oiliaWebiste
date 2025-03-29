from kavenegar import KavenegarAPI
from django.conf import settings
from .models import SMSLog

class SMSService:
    def __init__(self):
        self.api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        self.sender = '1000210002'

    def send_sms(self, receptor, message, car=None, is_reminder=False):
        """ارسال پیامک به شماره موبایل"""
        try:
            params = {
                'sender': self.sender,
                'receptor': receptor,
                'message': message
            }
            self.api.sms_send(params)
            
            # ثبت لاگ پیامک
            if car:
                SMSLog.objects.create(
                    car=car,
                    message=message,
                    is_reminder=is_reminder
                )
            return True
        except Exception as e:
            print(f"خطا در ارسال پیامک: {str(e)}")
            return False

    def send_service_reminder(self, car):
        """ارسال یادآوری سرویس"""
        message = f"""مشتری گرامی
آیا خودروی شما با پلاک {car.plate_number} 5000 کیلومتر پیمایش داشته است؟
برای مشاهده وضعیت سرویس عدد 1 را ارسال کنید."""
        return self.send_sms(car.owner_phone, message, car, is_reminder=True)

    def send_service_status(self, car):
        """ارسال وضعیت آخرین سرویس"""
        last_service = car.services.order_by('-service_date').first()
        if not last_service:
            message = "سرویسی برای خودروی شما ثبت نشده است."
        else:
            message = f"""آخرین سرویس خودرو:
تاریخ: {last_service.service_date}
کیلومتر: {last_service.current_mileage}
نوع روغن: {last_service.oil_type}
تعویض فیلتر هوا: {'بله' if last_service.air_filter_changed else 'خیر'}
تعویض فیلتر کابین: {'بله' if last_service.cabin_filter_changed else 'خیر'}
تعویض روغن گیربکس: {'بله' if last_service.gearbox_oil_changed else 'خیر'}"""
        
        return self.send_sms(car.owner_phone, message, car) 