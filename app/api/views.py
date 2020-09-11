from rest_framework import viewsets, status, permissions
from .serializers import AddressSerializer
from ..models import Address, Website
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .permissions import IsOwnerOrStaff


class AddresListView(viewsets.ModelViewSet):

    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaff,)

    def get_queryset(self):
        queryset = Address.objects.all()
        if not self.request.user.is_staff:
            queryset = Address.objects.filter(user_id=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

    def list(self, request):
        queryset = Address.objects.all()
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AddressSerializer(data=request.data)
        website = Website.objects.get(id=request.data['uri_id'])
        if (serializer.is_valid() and
            ((website.user_id == self.request.user and
              self.request.user.id == int(request.data['user_id'])) or
             self.request.user.is_staff)):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Address.objects.all()
        address = get_object_or_404(queryset, pk=pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def update(self, request, pk=None):
        address = self.get_object()
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        address = self.get_object()
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
