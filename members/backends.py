from django.contrib.auth.backends import ModelBackend
from .models import User


class EmailBackend(ModelBackend):
    """
    Allows users to authenticate with their email address.

    Uses filter().first() instead of get() so that if duplicate email rows
    somehow exist in the database, authentication degrades gracefully rather
    than raising MultipleObjectsReturned.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 'username' field carries the email value from the login form
        user = User.objects.filter(email=username).first()
        if user is None:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None