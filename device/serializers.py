from rest_framework import serializers

from device.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'device_name', 'IMEI_no', 'device_type', 'is_engaged', 'user')


class AddDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'device_name', 'IMEI_no', 'device_type')


class SubscribeDeviceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Device
        fields = ('id',)
