from django.contrib.auth import logout, login, authenticate
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import UserSerializer, UserDeviceSerializer


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
            user = User.objects.create(
                email=user_email,
                first_name=first_name,
                last_name=last_name,
                username=user_email,
            )
            user.set_password(password)
            user.username = user_email
            token, created = Token.objects.get_or_create(user=user)
            user.save()
            return Response({
                'token': token.key,
                'id': user.pk,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        serializer_class = UserSerializer
        if self.action == 'login':
            serializer_class = AuthTokenSerializer
        if self.action == 'list':
            serializer_class = UserDeviceSerializer
        return serializer_class

    def list(self, request, **kwargs):
        queryset = User.objects.filter(user_device__device_name__isnull=False)
        serializer = UserDeviceSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def logout(self, request):
        return logout_user(request)

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def login(self, request):
        if request.user and request.user.is_authenticated:
            return Response({'message': 'Already Logged In'}, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer_class()(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            authenticate(request, username=user.username, password=user.password)
            return Response({
                'id': request.user.pk,
                'email': request.user.email,
                'token': token.key,
            }, status=status.HTTP_200_OK)


def logout_user(request):
    if request.user and request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'message': 'Successfully Logged out'}, status=status.HTTP_200_OK)
    else:
        return Response(status=401)
