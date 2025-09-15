from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.plants.models import Plant
from apps.plants.serializers import PlantSerializer

class PlantViewSet(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['plant_type', 'is_active', 'city', 'state']
    search_fields = ['name', 'code', 'address', 'city', 'state', 'manager']
    ordering_fields = ['name', 'code', 'created_at', 'capacity']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by active plants by default unless specified
        is_active = self.request.query_params.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)
        return queryset
