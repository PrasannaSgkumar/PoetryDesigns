# backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Clients

class ClientBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            client = Clients.objects.get(username=username)
            if client and client.check_password(password):
                return client
        except Clients.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Clients.objects.get(pk=user_id)
        except Clients.DoesNotExist:
            return None
