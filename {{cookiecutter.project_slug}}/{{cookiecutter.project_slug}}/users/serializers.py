from rest_framework import serializers

from {{ cookiecutter.project_slug }}.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "username", "email", "roles", "user_profile_id"]
        {%- if cookiecutter.username_type == "email" %}
        extra_kwargs = {
            "url": {"lookup_field": "pk"},
        }
        {%- else %}
        extra_kwargs = {
            "url": {"lookup_field": "username"},
        }
        {%- endif %}

        def get_roles(self, obj):
            return [role.name for role in obj.role_set.all()]
