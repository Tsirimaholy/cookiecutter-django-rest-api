from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from .utils import encode_uid


class ActivationEmail(BaseEmailMessage):
    template_name = "email/activation.html"

    def get_context_data(self):
        # ActivationEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        activation_url = "#/activate/{uid}/{token}"
        context["url"] = activation_url.format(**context)
        return context


class ConfirmationEmail(BaseEmailMessage):
    template_name = "email/confirmation.html"
