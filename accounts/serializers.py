from rest_framework import serializers

from accounts.models import User
from device.serializers import DeviceSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'last_name', 'email', 'first_name', 'password')


class UserDeviceSerializer(serializers.ModelSerializer):
    user_device = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'last_name', 'email', 'first_name', 'user_device')


class ConfirmSignUpSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('otp', 'email')


class InitiateResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('email',)


class ResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('email', 'password', 'otp')
