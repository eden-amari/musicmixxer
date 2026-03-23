from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)

        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")

        return email

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)

        data = form.cleaned_data

        user.email = data.get("email")
        user.username = data.get("username")

        if commit:
            user.save()

        return user