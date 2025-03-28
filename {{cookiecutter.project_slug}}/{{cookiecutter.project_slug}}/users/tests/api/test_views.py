import pytest
from rest_framework.test import APIRequestFactory

from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.views import UserAccountViewSet as UserViewSet


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request
        view.action = "me"

        {%- if cookiecutter.username_type == "email" %}
        view.format_kwarg = {"pk": user.pk}
        {%- else %}
        view.format_kwarg = {"username": user.username}
        {%- endif %}
        response = view.me(request)
        assert response.data == {
                   "id": user.id,
                   "username": user.username,
                   "email": user.email,
                   "roles": [role.name for role in user.role_set.all()],
               }
