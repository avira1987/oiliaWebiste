from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Car, Service, SMSLog, Filter, Consumable

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'phone_number', 'is_mechanic')
    list_filter = ('is_mechanic', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'phone_number', 'email')}),
        ('دسترسی‌ها', {'fields': ('is_mechanic', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌های مهم', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'password1', 'password2', 'is_mechanic'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'phone_number')
    ordering = ('username',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'owner_name', 'owner_phone', 'created_at')
    search_fields = ('plate_number', 'owner_name', 'owner_phone')
    ordering = ('-created_at',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('car', 'mechanic', 'date', 'mileage', 'next_service_date')
    list_filter = ('mechanic', 'date', 'next_service_date')
    search_fields = ('car__plate_number', 'car__owner_name', 'mechanic__username')
    ordering = ('-date',)

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('service', 'phone_number', 'status', 'sent_at', 'scheduled_for')
    list_filter = ('status', 'sent_at', 'scheduled_for')
    search_fields = ('service__car__plate_number', 'phone_number', 'message')
    ordering = ('-created_at',)

@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'min_quantity', 'is_low_stock')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'min_quantity', 'is_low_stock')
    search_fields = ('name',)
    ordering = ('name',)
