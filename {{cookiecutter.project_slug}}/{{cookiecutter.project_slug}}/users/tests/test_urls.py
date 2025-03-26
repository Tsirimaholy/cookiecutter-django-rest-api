from django.urls import resolve
from django.urls import reverse

from {{ cookiecutter.project_slug }}.users.models import User


def test_detail(user: User):
    {%- if cookiecutter.username_type == "email" %}
    assert reverse("users:detail", kwargs={"pk": user.pk}) == f"/users/{user.pk}/"
    assert resolve(f"/users/{user.pk}/").view_name == "users:detail"
    {%- else %}
    assert (
        reverse("users:detail", kwargs={"username": user.username})
        == f"/users/{user.username}/"
    )
    assert resolve(f"/users/{user.username}/").view_name == "users:detail"
    {%- endif %}
