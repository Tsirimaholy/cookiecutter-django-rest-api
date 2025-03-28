from http import HTTPStatus

import pytest
from django.test.client import Client
from django.urls import reverse


def test_api_docs_accessible_by_admin(client: Client, admin_user):
    # Create a token for admin user
    jwt_create_url = reverse("jwt-create")
    response = client.post(
        jwt_create_url,
        {"username": admin_user.username, "password": "password"},
    )
    token = response.data["access"]

    # Use token to access API docs
    url = reverse("api-docs")
    response = client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_api_docs_not_accessible_by_anonymous_users(client):
    url = reverse("api-docs")
    response = client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_schema_generated_successfully(client: Client, admin_user):
    # Create a token for admin user
    jwt_create_url = reverse("jwt-create")
    response = client.post(
        jwt_create_url,
        {"username": admin_user.username, "password": "password"},
    )
    token = response.data["access"]

    # Use token to access API schema
    url = reverse("api-schema")
    response = client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.OK
