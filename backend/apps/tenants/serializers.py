from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tenant, TenantUser


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""

    user_count = serializers.SerializerMethodField()
    is_trial_expired = serializers.ReadOnlyField()

    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "slug",
            "domain",
            "contact_email",
            "contact_phone",
            "is_active",
            "is_trial",
            "trial_ends_at",
            "user_count",
            "is_trial_expired",
            "created_at",
            "updated_at",
            "settings",
            "logo",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_user_count(self, obj):
        """Get the number of active users for this tenant."""
        return obj.users.filter(is_active=True).count()

    def validate_slug(self, value):
        """Ensure slug is lowercase and unique."""
        if value:
            value = value.lower()
            if (
                Tenant.objects.filter(slug=value)
                .exclude(pk=self.instance.pk if self.instance else None)
                .exists()
            ):
                raise serializers.ValidationError(
                    "A tenant with this slug already exists."
                )
        return value


class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new tenants."""

    owner_email = serializers.EmailField(write_only=True, required=False)
    owner_first_name = serializers.CharField(
        max_length=30, write_only=True, required=False
    )
    owner_last_name = serializers.CharField(
        max_length=30, write_only=True, required=False
    )

    class Meta:
        model = Tenant
        fields = [
            "name",
            "slug",
            "domain",
            "contact_email",
            "contact_phone",
            "is_trial",
            "trial_ends_at",
            "settings",
            "owner_email",
            "owner_first_name",
            "owner_last_name",
        ]

    def create(self, validated_data):
        """Create tenant and optionally create owner user."""
        # Extract owner data
        owner_email = validated_data.pop("owner_email", None)
        owner_first_name = validated_data.pop("owner_first_name", "")
        owner_last_name = validated_data.pop("owner_last_name", "")

        # Create tenant
        validated_data["created_by"] = self.context["request"].user
        tenant = super().create(validated_data)

        # Create or associate owner user
        if owner_email:
            owner_user, created = User.objects.get_or_create(
                email=owner_email,
                defaults={
                    "username": owner_email,
                    "first_name": owner_first_name,
                    "last_name": owner_last_name,
                },
            )
            TenantUser.objects.create(tenant=tenant, user=owner_user, role="owner")

        return tenant


class TenantUserSerializer(serializers.ModelSerializer):
    """Serializer for TenantUser associations."""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = TenantUser
        fields = [
            "id",
            "tenant",
            "user",
            "role",
            "is_active",
            "username",
            "email",
            "first_name",
            "last_name",
            "tenant_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserTenantSerializer(serializers.ModelSerializer):
    """Serializer to show tenant info from user perspective."""

    tenant_id = serializers.UUIDField(source="tenant.id", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    tenant_slug = serializers.CharField(source="tenant.slug", read_only=True)
    is_trial = serializers.BooleanField(source="tenant.is_trial", read_only=True)

    class Meta:
        model = TenantUser
        fields = [
            "tenant_id",
            "tenant_name",
            "tenant_slug",
            "role",
            "is_active",
            "is_trial",
            "created_at",
        ]
