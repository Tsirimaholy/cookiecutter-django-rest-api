import cookiecutter.extensions
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from {{cookiecutter.project_slug}}.users.views import UserAccountViewSet
app_name = "users"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
# We need this in future in case we need to customise userviewsets
# NOTE: url registration orders matter when using a broader url prefix
router.register("", UserAccountViewSet, "user")

urlpatterns = router.urls
