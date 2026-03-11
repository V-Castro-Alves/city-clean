from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=300, blank=True)

    # AbstractUser already provides: id, email, first_name (use as nome), last_name (use as sobrenome), password, etc.
    # Set email as the login identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']