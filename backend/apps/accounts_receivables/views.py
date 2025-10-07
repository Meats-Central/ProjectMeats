from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.accounts_receivables.models import AccountsReceivable
from apps.accounts_receivables.serializers import AccountsReceivableSerializer


class AccountsReceivableViewSet(viewsets.ModelViewSet):
    queryset = AccountsReceivable.objects.all()
    serializer_class = AccountsReceivableSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "customer", "due_date"]
    search_fields = ["invoice_number", "description", "customer__name"]
    ordering_fields = ["due_date", "created_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by customer if provided in query params
        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset
