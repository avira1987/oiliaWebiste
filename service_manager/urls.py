from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'cars', views.CarViewSet, basename='car')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'sms-logs', views.SMSLogViewSet)
router.register(r'filters', views.FilterViewSet)
router.register(r'consumables', views.ConsumableViewSet)

urlpatterns = [
    # صفحات اصلی
    path('', views.home, name='home'),
    path('new-service/', views.new_service, name='new_service'),
    path('service-history/', views.service_history, name='service_history'),
    path('filters/', views.filters, name='filters'),
    path('profile/', views.profile, name='profile'),
    
    # احراز هویت
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # مدیریت سرویس‌ها
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('service/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('service/<int:service_id>/send-reminder/', views.send_reminder, name='send_reminder'),
    
    # مشاهده جزئیات سرویس برای مشتری
    path('service-details/<str:token>/', views.service_details, name='service_details'),
    
    # مدیریت فیلترها و لوازم مصرفی
    path('filters/add/', views.add_filter, name='add_filter'),
    path('consumables/add/', views.add_consumable, name='add_consumable'),
    path('filters/<int:filter_id>/edit/', views.edit_filter, name='edit_filter'),
    path('consumables/<int:consumable_id>/edit/', views.edit_consumable, name='edit_consumable'),
    path('items/<str:item_type>/<int:item_id>/add-stock/', views.add_stock, name='add_stock'),
    
    # API
    path('api/', include(router.urls)),
    
    # API مشتری
    path('customer/service-status/', views.CustomerServiceStatus.as_view(), name='customer-service-status'),
    
    # جستجوی خودرو
    path('api/cars/search/', views.search_cars, name='search_cars'),
] 