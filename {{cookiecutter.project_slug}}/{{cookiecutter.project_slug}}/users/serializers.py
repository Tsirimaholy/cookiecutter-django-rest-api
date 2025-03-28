from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core import exceptions as django_exceptions
from django.db import transaction
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from rest_framework.settings import api_settings

from {{ cookiecutter.project_slug }}.users import utils
from {{ cookiecutter.project_slug }}.users.models import Role
from {{ cookiecutter.project_slug }}.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    roles = serializers.SerializerMethodField(method_name="get_roles")
    class Meta:
        model = User
        fields = ["id", "username", "email", "roles"]
        {%- if cookiecutter.username_type == "email" %}
        extra_kwargs = {
            "url": {"lookup_field": "pk"},
        }
        {%- else %}
        extra_kwargs = {
            "url": {"lookup_field": "username"},
        }
        {%- endif %}

    def get_roles(self, obj)->list[str]:
        return [role.name for role in obj.role_set.all()]
# TODO: check if there is any necessary email/username check required
class UserCreateSerializer(BaseUserCreateSerializer):
    roles:serializers.ListSerializer[serializers.CharField] = (
        serializers.ListSerializer(child=serializers.CharField(), write_only=True)
    )
    email = serializers.EmailField(required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ["id", "username", "password", "email", "roles"]

    def validate(self, attrs):
        roles = attrs.pop("roles", None)
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]},
            ) from e
        attrs["roles"] = roles
        return attrs

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        with transaction.atomic():
            if Role.ADMIN in roles:
                user = User.objects.create_superuser(**validated_data)
            else:
                user = User.objects.create_user(**validated_data)

            # Create roles for the user
            mapped_roles = [
                {"name": role, "user": user.id} for role in roles if role != Role.ADMIN
            ]
            mapped_roles_serializer = RoleSerializer(many=True, data=mapped_roles)
            mapped_roles_serializer.is_valid(raise_exception=True)
            mapped_roles_serializer.save()
            self.instance = user
        return self.instance

    def save(self, **kwargs):
        return super().save(**kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["roles"] = [role.name for role in instance.role_set.all()]
        return representation


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "user"]


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    default_error_messages = {
        "invalid_token": "INVALID_TOKEN_ERROR",
        "invalid_uid": "INVALID UID",
    }

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        # uid validation have to be here, because validate_<field_name>
        # doesn't work with model serializer
        try:
            uid = utils.decode_uid(self.initial_data.get("uid", ""))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError) as err:
            key_error = "invalid_uid"
            raise serializers.ValidationError(
                {"uid": [self.error_messages[key_error]]},
                code=key_error,
            ) from err

        is_token_valid = self.context["view"].token_generator.check_token(
            self.user,
            self.initial_data.get("token", ""),
        )
        if is_token_valid:
            return validated_data
        key_error = "invalid_token"
        raise serializers.ValidationError(
            {"token": [self.error_messages[key_error]]},
            code=key_error,
        )


class ActivationSerializer(UidAndTokenSerializer):
    default_error_messages = {
        "stale_token": "STALE_TOKEN",
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not self.user.is_active:
            return attrs
        raise exceptions.PermissionDenied(self.error_messages["stale_token"])
