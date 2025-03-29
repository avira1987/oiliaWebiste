from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone

class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True, validators=[
        RegexValidator(
            regex=r'^09\d{9}$',
            message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
        )
    ])
    is_mechanic = models.BooleanField(default=False)
    email = models.EmailField(unique=True, null=True, blank=True)  # اضافه کردن فیلد email به صورت اختیاری
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.phone_number if self.phone_number else 'بدون شماره'}"

class Car(models.Model):
    plate_number = models.CharField(max_length=8, unique=True, validators=[
        RegexValidator(
            regex=r'^\d{2}-\d{3}[مع]\d{2}$',
            message='شماره پلاک باید به فرمت 59-365م33 باشد'
        )
    ])
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=11, validators=[
        RegexValidator(
            regex=r'^09\d{9}$',
            message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
        )
    ])
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plate_number} - {self.owner_name}"

class Service(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    mechanic = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    date = models.DateTimeField(default=timezone.now)
    mileage = models.IntegerField()
    oil_type = models.CharField(max_length=100)
    oil_filter_changed = models.BooleanField(default=False)
    air_filter_changed = models.BooleanField(default=False)
    cabin_filter_changed = models.BooleanField(default=False)
    gearbox_oil_changed = models.BooleanField(default=False)
    next_service_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    
    # فیلدهای جدید
    radiator_water_checked = models.BooleanField(default=False, verbose_name='چک آب رادیاتور انجام شد')
    windshield_washer_filled = models.BooleanField(default=False, verbose_name='شیشه شور عقب و جلو پر شد')
    brake_fluid_checked = models.BooleanField(default=False, verbose_name='روغن ترمز چک شد')
    power_steering_fluid_checked = models.BooleanField(default=False, verbose_name='روغن هیدرولیک فرمان چک شد')
    gearbox_oil_checked = models.BooleanField(default=False, verbose_name='واسکازین چک شد')
    gearbox_oil_change_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تعویض واسکازین')

    def __str__(self):
        return f"{self.car.plate_number if self.car else 'بدون خودرو'} - {self.date.strftime('%Y/%m/%d')}"

    def save(self, *args, **kwargs):
        # اگر خودرو وجود نداشته باشد، یک خودرو جدید ایجاد می‌کنیم
        if not self.car:
            car, created = Car.objects.get_or_create(
                plate_number=self.plate_number,
                defaults={
                    'owner_name': self.owner_name,
                    'owner_phone': self.owner_phone,
                    'current_mileage': self.mileage
                }
            )
            self.car = car
        super().save(*args, **kwargs)

class ServiceLink(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='view_links')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"لینک مشاهده سرویس {self.service.car.plate_number}"

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

class SMSLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('sent', 'ارسال شده'),
        ('failed', 'ناموفق'),
        ('scheduled', 'برنامه‌ریزی شده')
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='sms_logs')
    phone_number = models.CharField(max_length=11, validators=[
        RegexValidator(
            regex=r'^09\d{9}$',
            message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
        )
    ])
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.car.plate_number} - {self.sent_at or self.scheduled_for}"

    def send(self):
        try:
            sms_service = SMSService()
            success = sms_service.send_sms(self.phone_number, self.message)
            if success:
                self.status = 'sent'
                self.sent_at = timezone.now()
                self.save()
                return True
            else:
                self.status = 'failed'
                self.save()
                return False
        except Exception as e:
            self.status = 'failed'
            self.save()
            return False

class Filter(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    def is_low_stock(self):
        return self.quantity <= self.min_quantity

class Consumable(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    def is_low_stock(self):
        return self.quantity <= self.min_quantity
