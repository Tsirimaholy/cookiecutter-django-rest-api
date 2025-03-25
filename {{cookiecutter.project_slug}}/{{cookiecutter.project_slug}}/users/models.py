import uuid

{%- if cookiecutter.username_type == "email" %}
from typing import ClassVar

{% endif -%}
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, UniqueConstraint

{%- if cookiecutter.username_type == "email" %}
from django.db.models import EmailField
{%- endif %}
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
{%- if cookiecutter.username_type == "email" %}

from .managers import UserManager
{%- endif %}

class User(AbstractUser):
    """
    Default custom user model for {{cookiecutter.project_name}}.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    {%- if cookiecutter.username_type == "email" %}
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()
    {%- endif %}

    def has_role(self, role_name):
        return Role.objects.filter(user=self, name=role_name).exists()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        {%- if cookiecutter.username_type == "email" %}
        return reverse("users:detail", kwargs={"pk": self.id})
        {%- else %}
        return reverse("users:detail", kwargs={"username": self.username})
        {%- endif %}

class Role(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        null=False,
    )
    ADMIN = "ADMIN"
    INSTRUCTOR = "INSTRUCTOR"
    CUSTOMER = "CUSTOMER"
    STUDENT = "STUDENT"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (INSTRUCTOR, "Instructor"),
        (CUSTOMER, "Customer"),
        (STUDENT, "Student"),
    ]

    name = models.CharField(choices=ROLE_CHOICES, max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "name"), name="unique_together_role_user"),
        ]

    def __str__(self):
        return self.name
