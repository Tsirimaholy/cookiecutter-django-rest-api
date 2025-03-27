from .utils import get_user_email
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .email import ConfirmationEmail, ActivationEmail
from .models import User
from .permissions import IsAdmin
from .serializers import ActivationSerializer
from .serializers import UserCreateSerializer


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
        return super().get_queryset().prefetch_related("role_set")

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
        context = {"user": user}
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
