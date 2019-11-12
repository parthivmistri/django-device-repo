import math
import random

from django.contrib.auth import logout, login, authenticate
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import UserSerializer, UserDeviceSerializer, ConfirmSignUpSerializer, \
    InitiateResetPasswordSerializer, ResetPasswordSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        password = request.data['password']
        user_email = request.data['email']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        user = User.objects.filter(email__iexact=user_email).first()
        if user:
            return Response({'message': 'You are already registered with us. Please log into your account.'},
                            status=status.HTTP_200_OK)
        elif not user:
            otp = generateOTP()
            user = User.objects.create(
                email=user_email,
                first_name=first_name,
                last_name=last_name,
                username=user_email,
                otp=otp,
                is_verified=False
            )
            user.set_password(password)
            user.username = user_email
            user.save()
            send_mail('Device Repo',
                      'Your OTP is ' + str(user.otp),
                      'pmistri@codal.com',
                      [user_email],
                      fail_silently=False,
                      )
            return Response({
                'message': 'Please check you email inbox for the otp', }, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        serializer_class = UserSerializer
        if self.action == 'login':
            serializer_class = AuthTokenSerializer
        if self.action == 'list':
            serializer_class = UserDeviceSerializer
        if self.action == 'confirm_signup':
            serializer_class = ConfirmSignUpSerializer
        if self.action == 'initiate_reset_password':
            serializer_class = InitiateResetPasswordSerializer
        if self.action == 'reset_password':
            serializer_class = ResetPasswordSerializer
        return serializer_class

    def list(self, request, **kwargs):
        queryset = User.objects.filter(user_device__device_name__isnull=False)
        serializer = UserDeviceSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'])
    def confirm_signup(self, request):
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        otp = request.data['otp']
        email = request.data['email']
        user = User.objects.get(email=email)
        if user is not None:
            if user.otp == otp:
                token, created = Token.objects.get_or_create(user=user)
                user.is_verified = True
                user.otp = None
                user.save()
                login(request, user)
                authenticate(request, username=user.username, password=user.password)
                return Response({'message': 'Verified',
                                 'id': user.pk,
                                 'first_name': user.first_name,
                                 'last_name': user.last_name,
                                 'email': user.email,
                                 'token': token.key, }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'OTP is invalid',
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User does not exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def login(self, request):
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if request.user and request.user.is_authenticated:
            return Response({'message': 'Already Logged In'}, status=status.HTTP_200_OK)
        elif not user.is_verified:
            send_mail(
                'Device Repo',
                'Your OTP is ' + str(user.otp),
                'pmistri@codal.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Not verified we have sent otp to your email'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            authenticate(request, username=user.username, password=user.password)
            return Response({
                'id': request.user.pk,
                'email': request.user.email,
                'token': token.key,
            }, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def initiate_reset_password(self, request):
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data['email']
        user = User.objects.get(email=email)
        if user is not None:
            user.otp = generateOTP()    
            user.save()
            send_mail(
                'Device Repo',
                'Your OTP to reset password ' + str(user.otp),
                'pmistri@codal.com',
                [user.email],
                fail_silently=False,
            )
            return Response({
                'message': 'Please check you email inbox for the otp',
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User does not exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def reset_password(self, request):
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data['email']
        password = request.data['password']
        otp = request.data['otp']
        user = User.objects.get(email=email)
        if user is not None:
            if user.otp == otp:
                user.otp = None
                user.set_password(password)
                user.save()
                return Response({
                    'message': 'Password Changed',
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'OTP is invalid',
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User does not exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def logout(self, request):
        return logout_user(request)


def logout_user(request):
    if request.user and request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'message': 'Successfully Logged out'}, status=status.HTTP_200_OK)
    else:
        return Response(status=401)


def generateOTP():
    digits = "123456789"
    otp = ""
    for i in range(4):
        otp += digits[math.floor(random.random() * 10)]
    return otp
