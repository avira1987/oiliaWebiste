from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Car, Service, SMSLog, Filter, Consumable

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    mechanic = UserSerializer(read_only=True)

    class Meta:
        model = Service
        fields = '__all__'

class SMSLogSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = SMSLog
        fields = '__all__'

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'

class ConsumableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumable
        fields = '__all__' 