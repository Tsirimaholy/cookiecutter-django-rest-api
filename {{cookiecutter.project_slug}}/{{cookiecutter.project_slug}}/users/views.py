from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import User, Role
from .serializers import UserCreateSerializer, ActivationSerializer
from .permissions import IsAdmin
from .email import ConfirmationEmail, ActivationEmail
from .utils import get_user_email


class UserAccountViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    {%- if cookiecutter.username_type == "email" %}
    lookup_field = "pk"
    {%- else %}
    lookup_field = "username"
    {%- endif %}

    def get_permissions(self):
        if self.action == "signup":
            return [IsAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()
        if self.action == "list" and not (
            user.is_staff or Role.ADMIN in user.role_set.all() or user.is_superuser
        ):
            assert isinstance(self.request.user.id, int)
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "signup":
            return UserCreateSerializer
        if self.action == "activation":
            return ActivationSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


    def create(self, request, *args, **kwargs):
        request_data = request.data
        serializer = self.get_serializer(data=request_data)
        # we need to validate password, so we need to write password
        # as early as possible into the serializer
        if "password" not in request_data or not request_data["password"]:
            serializer.initial_data["password"] = User.objects.make_random_password(8)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        context = {"user": user, "password": serializer.validated_data.get("password")}
        to = [get_user_email(user)]
        ActivationEmail(self.request, context).send(to)

    @action(["post"], detail=False)
    def signup(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        self.instance = user
        context = {"user": user}
        to = [get_user_email(user)]
        ConfirmationEmail(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
