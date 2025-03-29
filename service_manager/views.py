from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Car, Service, SMSLog, Filter, Consumable, ServiceLink
from .serializers import UserSerializer, CarSerializer, ServiceSerializer, SMSLogSerializer, FilterSerializer, ConsumableSerializer
from .services import SMSService
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
import re
import secrets
import string

# Create your views here.

class IsMechanic(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_mechanic

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated, IsMechanic]

    def get_queryset(self):
        queryset = Car.objects.all()
        phone = self.request.query_params.get('phone', None)
        plate = self.request.query_params.get('plate', None)
        
        if phone:
            queryset = queryset.filter(owner_phone__icontains=phone)
        if plate:
            queryset = queryset.filter(plate_number__icontains=plate)
        
        return queryset

    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        car = self.get_object()
        sms_service = SMSService()
        success = sms_service.send_service_reminder(car)
        
        if success:
            return Response({'status': 'یادآوری ارسال شد'})
        return Response(
            {'error': 'خطا در ارسال پیامک'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsMechanic]

    def get_queryset(self):
        # فیلتر کردن سرویس‌ها بر اساس کاربر لاگین شده
        return Service.objects.filter(mechanic=self.request.user).select_related('car', 'mechanic')

    def perform_create(self, serializer):
        serializer.save(mechanic=self.request.user)

class SMSLogViewSet(viewsets.ModelViewSet):
    queryset = SMSLog.objects.all()
    serializer_class = SMSLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsMechanic]

# ویو برای استعلام وضعیت سرویس توسط مشتری
from rest_framework.views import APIView

class CustomerServiceStatus(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response(
                {'error': 'شماره موبایل الزامی است'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cars = Car.objects.filter(owner_phone=phone)
        if not cars.exists():
            return Response(
                {'error': 'خودرویی با این شماره موبایل یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        if cars.count() == 1:
            car = cars.first()
            sms_service = SMSService()
            success = sms_service.send_service_status(car)
            
            if success:
                return Response({'status': 'وضعیت سرویس ارسال شد'})
            return Response(
                {'error': 'خطا در ارسال پیامک'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # اگر مشتری چند خودرو داشته باشد
        cars_list = [
            {'plate': car.plate_number, 'id': car.id} 
            for car in cars
        ]
        return Response({
            'message': 'لطفاً خودروی مورد نظر را انتخاب کنید',
            'cars': cars_list
        })

def home(request):
    context = {
        'total_services': Service.objects.count(),
        'total_cars': Car.objects.count(),
        'total_mechanics': User.objects.filter(is_mechanic=True).count(),
    }
    return render(request, 'home.html', context)

def generate_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@login_required
def new_service(request):
    if request.method == 'POST':
        try:
            # محاسبه تاریخ سرویس بعدی (3 ماه بعد)
            next_service_date = timezone.now() + timezone.timedelta(days=90)
            
            # دریافت اطلاعات خودرو
            plate_number = request.POST.get('plate_number')
            owner_name = request.POST.get('owner_name')
            owner_phone = request.POST.get('owner_phone')
            
            # جستجوی خودرو با شماره پلاک
            car, created = Car.objects.get_or_create(
                plate_number=plate_number,
                defaults={
                    'owner_name': owner_name,
                    'owner_phone': owner_phone
                }
            )
            
            # اگر خودرو قبلاً وجود داشته باشد، اطلاعات مالک را به‌روزرسانی می‌کنیم
            if not created:
                car.owner_name = owner_name
                car.owner_phone = owner_phone
                car.save()
            
            service = Service.objects.create(
                car=car,
                mechanic=request.user,
                date=timezone.now(),
                mileage=request.POST.get('mileage'),
                oil_type=request.POST.get('oil_type'),
                oil_filter_changed=request.POST.get('oil_filter_changed') == 'on',
                air_filter_changed=request.POST.get('air_filter_changed') == 'on',
                cabin_filter_changed=request.POST.get('cabin_filter_changed') == 'on',
                next_service_date=next_service_date,
                notes=request.POST.get('notes'),
                # فیلدهای جدید
                radiator_water_checked=request.POST.get('radiator_water_checked') == 'on',
                windshield_washer_filled=request.POST.get('windshield_washer_filled') == 'on',
                brake_fluid_checked=request.POST.get('brake_fluid_checked') == 'on',
                power_steering_fluid_checked=request.POST.get('power_steering_fluid_checked') == 'on',
                gearbox_oil_checked=request.POST.get('gearbox_oil_checked') == 'on',
                gearbox_oil_change_date=request.POST.get('gearbox_oil_change_date') or None
            )
            
            # ایجاد لینک یکبار مصرف برای مشاهده جزئیات سرویس
            service_link = ServiceLink.objects.create(
                service=service,
                token=generate_token(),
                expires_at=timezone.now() + timezone.timedelta(days=7)  # لینک تا 7 روز معتبر است
            )
            
            # ساخت URL کامل برای مشاهده جزئیات سرویس
            service_url = request.build_absolute_uri(reverse('service_details', kwargs={'token': service_link.token}))
            
            # ارسال پیامک به مالک خودرو
            sms_service = SMSService()
            message = (
                f"سلام {car.owner_name} عزیز.\n"
                f"سرویس خودرو شما با موفقیت ثبت شد.\n"
                f"تاریخ سرویس بعدی: {service.next_service_date.strftime('%Y/%m/%d')}\n"
                f"برای مشاهده جزئیات سرویس به لینک زیر مراجعه کنید:\n"
                f"{service_url}"
            )
            sms_service.send_sms(car.owner_phone, message)
            
            # تنظیم یادآوری برای 7 روز قبل از تاریخ سرویس
            reminder_date = service.next_service_date - timezone.timedelta(days=7)
            SMSLog.objects.create(
                service=service,
                phone_number=car.owner_phone,
                message=f"سلام {car.owner_name} عزیز. یادآوری می‌کنیم که تاریخ سرویس بعدی خودرو شما {service.next_service_date.strftime('%Y/%m/%d')} است.",
                status='scheduled',
                scheduled_for=reminder_date
            )
            
            messages.success(request, 'سرویس با موفقیت ثبت شد.')
            return redirect('service_history')
            
        except Exception as e:
            messages.error(request, f'خطا در ثبت سرویس: {str(e)}')
            return redirect('new_service')
    
    return render(request, 'new_service.html')

@login_required
def service_history(request):
    # فیلتر کردن سرویس‌ها بر اساس کاربر لاگین شده
    services = Service.objects.filter(mechanic=request.user).select_related('car', 'mechanic').order_by('-date')
    return render(request, 'service_history.html', {'services': services})

@login_required
def service_detail(request, service_id):
    # بررسی دسترسی کاربر به سرویس
    service = get_object_or_404(Service, id=service_id, mechanic=request.user)
    return JsonResponse(ServiceSerializer(service).data)

@login_required
@require_POST
def send_reminder(request, service_id):
    # بررسی دسترسی کاربر به سرویس
    service = get_object_or_404(Service, id=service_id, mechanic=request.user)
    try:
        # ارسال پیامک
        message = f"سلام {service.car.owner_name} عزیز. یادآوری می‌کنیم که تاریخ سرویس بعدی خودرو شما {service.next_service_date} است."
        # TODO: Implement SMS sending logic
        
        SMSLog.objects.create(
            service=service,
            phone_number=service.car.owner_phone,
            message=message,
            status='success'
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def filters(request):
    filters = Filter.objects.all()
    consumables = Consumable.objects.all()
    return render(request, 'filters.html', {
        'filters': filters,
        'consumables': consumables
    })

@login_required
@require_POST
def add_filter(request):
    Filter.objects.create(
        name=request.POST['name'],
        quantity=request.POST['quantity'],
        min_quantity=request.POST['min_quantity']
    )
    messages.success(request, 'فیلتر با موفقیت اضافه شد.')
    return redirect('filters')

@login_required
@require_POST
def add_consumable(request):
    Consumable.objects.create(
        name=request.POST['name'],
        quantity=request.POST['quantity'],
        min_quantity=request.POST['min_quantity']
    )
    messages.success(request, 'کالا با موفقیت اضافه شد.')
    return redirect('filters')

@login_required
@require_POST
def edit_filter(request, filter_id):
    filter_obj = get_object_or_404(Filter, id=filter_id)
    filter_obj.name = request.POST['name']
    filter_obj.quantity = request.POST['quantity']
    filter_obj.min_quantity = request.POST['min_quantity']
    filter_obj.save()
    messages.success(request, 'فیلتر با موفقیت ویرایش شد.')
    return redirect('filters')

@login_required
@require_POST
def edit_consumable(request, consumable_id):
    consumable = get_object_or_404(Consumable, id=consumable_id)
    consumable.name = request.POST['name']
    consumable.quantity = request.POST['quantity']
    consumable.min_quantity = request.POST['min_quantity']
    consumable.save()
    messages.success(request, 'کالا با موفقیت ویرایش شد.')
    return redirect('filters')

@login_required
@require_POST
def add_stock(request, item_id, item_type):
    if item_type == 'filter':
        item = get_object_or_404(Filter, id=item_id)
    else:
        item = get_object_or_404(Consumable, id=item_id)
    
    item.quantity += int(request.POST['quantity'])
    item.save()
    messages.success(request, 'موجودی با موفقیت اضافه شد.')
    return redirect('filters')

# API Views
class FilterViewSet(viewsets.ModelViewSet):
    queryset = Filter.objects.all()
    serializer_class = FilterSerializer

class ConsumableViewSet(viewsets.ModelViewSet):
    queryset = Consumable.objects.all()
    serializer_class = ConsumableSerializer

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'رمز عبور و تکرار آن مطابقت ندارند.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'این ایمیل قبلاً ثبت شده است.')
            return redirect('register')
            
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'این شماره موبایل قبلاً ثبت شده است.')
            return redirect('register')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                phone_number=phone_number,
                password=password
            )
            login(request, user)
            messages.success(request, 'ثبت نام با موفقیت انجام شد.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'خطا در ثبت نام: {str(e)}')
            return redirect('register')
    
    return render(request, 'register.html')

@login_required
def car_list(request):
    cars = Car.objects.all().order_by('-created_at')
    return render(request, 'car_list.html', {'cars': cars})

@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    services = car.services.all().order_by('-date')
    return render(request, 'car_detail.html', {'car': car, 'services': services})

@require_http_methods(["POST"])
def new_car(request):
    try:
        # اعتبارسنجی شماره پلاک
        plate_number = request.POST.get('plate_number')
        if not re.match(r'^\d{2}[A-Z]{3}\d{2}$', plate_number):
            return JsonResponse({
                'status': 'error',
                'message': 'شماره پلاک باید به فرمت 12ABC34 باشد'
            })
        
        # اعتبارسنجی شماره موبایل
        owner_phone = request.POST.get('owner_phone')
        if not re.match(r'^09[0-9]{9}$', owner_phone):
            return JsonResponse({
                'status': 'error',
                'message': 'شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            })
        
        # ایجاد خودرو جدید
        car = Car.objects.create(
            plate_number=plate_number,
            owner_name=request.POST.get('owner_name'),
            owner_phone=owner_phone,
            current_mileage=request.POST.get('current_mileage')
        )
        
        return JsonResponse({
            'status': 'success',
            'car': {
                'id': car.id,
                'plate_number': car.plate_number,
                'owner_name': car.owner_name
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        # دریافت داده‌های فرم
        car_id = request.POST.get('car')
        mileage = request.POST.get('mileage')
        oil_type = request.POST.get('oil_type')
        oil_quantity = request.POST.get('oil_quantity')
        oil_filter_changed = request.POST.get('oil_filter_changed') == 'on'
        air_filter_changed = request.POST.get('air_filter_changed') == 'on'
        fuel_filter_changed = request.POST.get('fuel_filter_changed') == 'on'
        notes = request.POST.get('notes')
        
        # بروزرسانی سرویس
        service.car_id = car_id
        service.mileage = mileage
        service.oil_type = oil_type
        service.oil_quantity = oil_quantity
        service.oil_filter_changed = oil_filter_changed
        service.air_filter_changed = air_filter_changed
        service.fuel_filter_changed = fuel_filter_changed
        service.notes = notes
        service.save()
        
        messages.success(request, 'سرویس با موفقیت بروزرسانی شد.')
        return redirect('service_history')
    
    # دریافت لیست خودروها برای فرم
    cars = Car.objects.all().order_by('-created_at')
    
    context = {
        'service': service,
        'cars': cars,
    }
    return render(request, 'edit_service.html', context)

@login_required
@require_GET
def search_cars(request):
    phone = request.GET.get('phone')
    if not phone:
        return JsonResponse({'error': 'شماره موبایل الزامی است'}, status=400)
    
    cars = Car.objects.filter(owner_phone=phone).values('id', 'plate_number', 'owner_name', 'owner_phone')
    return JsonResponse({'cars': list(cars)})

def service_details(request, token):
    try:
        service_link = ServiceLink.objects.get(token=token)
        if not service_link.is_valid():
            messages.error(request, 'این لینک منقضی شده یا قبلاً استفاده شده است.')
            return redirect('home')
        
        # علامت‌گذاری لینک به عنوان استفاده شده
        service_link.is_used = True
        service_link.used_at = timezone.now()
        service_link.save()
        
        return render(request, 'service_details.html', {
            'service': service_link.service
        })
    except ServiceLink.DoesNotExist:
        messages.error(request, 'لینک نامعتبر است.')
        return redirect('home')
