from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import sesame.utils

User = get_user_model()


def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            token = sesame.utils.get_token(user)
            link = request.build_absolute_uri(f'/accounts/auth/?sesame={token}')
            send_mail(
                subject='Seu link de acesso — CityClean',
                message=f'Olá, {user.first_name}!\n\nClique no link abaixo para acessar sua conta (válido por 15 minutos):\n\n{link}',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@cityclean.com',
                recipient_list=[user.email],
            )
            return render(request, 'accounts/login_sent.html', {'email': email})
        except User.DoesNotExist:
            error = 'Nenhuma conta encontrada com este e-mail.'
    return render(request, 'accounts/login.html', {'error': error})


def cadastro_view(request):
    error = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefone = request.POST.get('telefone', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        endereco = request.POST.get('endereco', '').strip()

        if not all([first_name, last_name, email, cpf, telefone, endereco]):
            error = 'Todos os campos marcados com * são obrigatórios.'
        elif User.objects.filter(email=email).exists():
            error = 'Já existe uma conta com este e-mail.'
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None,
            )
            user.telefone = telefone
            user.cpf = cpf
            user.endereco = endereco
            user.save()
            # Send magic link immediately after registration
            token = sesame.utils.get_token(user)
            link = request.build_absolute_uri(f'/accounts/auth/?sesame={token}')
            send_mail(
                subject='Bem-vindo ao CityClean — acesse sua conta',
                message=f'Olá, {first_name}!\n\nObrigado por se cadastrar. Clique abaixo para entrar:\n\n{link}',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@cityclean.com',
                recipient_list=[email],
            )
            return render(request, 'accounts/login_sent.html', {'email': email})
    return render(request, 'accounts/cadastro.html', {'error': error})


def logout_view(request):
    auth.logout(request)
    return redirect('home')

