from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'telefone', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Dados adicionais', {'fields': ('telefone', 'cpf', 'endereco')}),
    )
