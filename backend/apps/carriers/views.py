from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.carriers.models import Carrier
from apps.carriers.serializers import CarrierSerializer

class CarrierViewSet(viewsets.ModelViewSet):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['carrier_type', 'is_active', 'city', 'state']
    search_fields = ['name', 'code', 'contact_person', 'phone', 'email', 'mc_number', 'dot_number']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by active carriers by default unless specified
        is_active = self.request.query_params.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)
        return queryset
