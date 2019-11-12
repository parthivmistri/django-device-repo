from abc import ABC

import coreapi
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response

from device.models import Device
from device.serializers import DeviceSerializer, SubscribeDeviceSerializer, AddDeviceSerializer


class SimpleFilterBackend(BaseFilterBackend, ABC):
    def get_schema_fields(self, view):
        return [coreapi.Field(
            name='is_engaged',
            location='query',
            required=False,
            description="Pass True to get Engaged Device and False to get Available device",
            type='boolean')]


class DeviceViewSet(viewsets.ModelViewSet):
    filter_backends = (SimpleFilterBackend,)
    queryset = Device.objects.all()

    def get_serializer_class(self):
        serializer_class = AddDeviceSerializer
        if self.action == 'subscribe_device':
            serializer_class = SubscribeDeviceSerializer
        if self.action == 'unsubscribe_device':
            serializer_class = SubscribeDeviceSerializer
        if self.action == 'list':
            serializer_class = DeviceSerializer
        return serializer_class

    def list(self, request, *args, **kwargs):
        is_engaged = request.GET.get('is_engaged')
        if is_engaged == 'true':
            device = Device.objects.filter(is_engaged__exact=True).values()
            return Response(device, status=status.HTTP_200_OK)
        elif is_engaged == 'false':
            device = Device.objects.filter(is_engaged__exact=False).values()
            return Response(device, status.HTTP_200_OK)
        else:
            device = Device.objects.values()
            return Response(device, status.HTTP_200_OK)

    @list_route(methods=['post'])
    def subscribe_device(self, request):
        if request.user and request.user.is_authenticated:
            serializer = self.get_serializer_class()(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            device_id = request.data['id']
            try:
                device = Device.objects.get(id=device_id)
            except Device.DoesNotExist:
                device = None
            if device is None:
                return Response({'message': 'In-valid Id'}, status=status.HTTP_400_BAD_REQUEST)
            elif device.is_engaged:
                return Response({'message': 'Device is in Use'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                device.is_engaged = True
                device.user = request.user
                device.save()
                return Response({'message': 'Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    @list_route(methods=['post'])
    def unsubscribe_device(self, request):
        if request.user and request.user.is_authenticated:
            serializer = self.get_serializer_class()(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            device_id = request.data['id']
            try:
                device = Device.objects.get(id=device_id)
            except Device.DoesNotExist:
                device = None
            if device is None:
                return Response({'message': 'In-valid Id'}, status=status.HTTP_400_BAD_REQUEST)
            elif not device.is_engaged:
                return Response({'message': 'Device is already Free'}, status=status.HTTP_400_BAD_REQUEST)
            elif request.user.pk != device.user_id:
                return Response({'message': 'Can not unsubscribe for other user'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                device.is_engaged = False
                device.user = None
                device.save()
                return Response({'message': 'Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
