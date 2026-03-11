import json
from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .forms import DenunciaForm, AgendamentoForm
from .models import Solicitacao, PontoDeColeta


def home_view(request):
    return render(request, 'core/home.html')


def pontos_descarte_view(request):
    pontos = PontoDeColeta.objects.prefetch_related('materiais_aceitos').all()
    pontos_json = json.dumps([
        {
            'id': p.id,
            'nome': p.nome,
            'endereco': p.endereco,
            'horario': p.horario,
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'materiais': [m.nome for m in p.materiais_aceitos.all()],
        }
        for p in pontos
    ])
    return render(request, 'core/pontos_descarte.html', {'pontos': pontos, 'pontos_json': pontos_json})


@login_required
def denuncia_create_view(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST, request.FILES)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.usuario = request.user
            solicitacao.tipo_solicitacao = Solicitacao.TipoSolicitacao.DENUNCIA
            solicitacao.save()
            form.save_m2m()
            _send_confirmation_email(request, solicitacao)
            return redirect('solicitacao_list')
    else:
        form = DenunciaForm()
    return render(request, 'core/denuncia_form.html', {'form': form})


@login_required
def agendamento_create_view(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, request.FILES)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.usuario = request.user
            solicitacao.tipo_solicitacao = Solicitacao.TipoSolicitacao.AGENDAMENTO
            # lat/lng set via hidden form fields — already on instance
            solicitacao.save()
            form.save_m2m()
            _send_confirmation_email(request, solicitacao)
            return redirect('solicitacao_list')
    else:
        form = AgendamentoForm()
    return render(request, 'core/agendamento_form.html', {'form': form})


@login_required
def solicitacao_list(request):
    qs = Solicitacao.objects.filter(usuario=request.user).order_by('-data_criacao')
    return render(request, 'core/solicitacao_list.html', {'solicitacoes': qs})


@login_required
def solicitacao_detail(request, uuid):
    s = get_object_or_404(Solicitacao, uuid=uuid, usuario=request.user)
    return render(request, 'core/solicitacao_detail.html', {'solicitacao': s})


def faq_view(request):
    return render(request, 'core/faq.html')


@login_required
def solicitacao_cancel_view(request, uuid):
    solicitacao = get_object_or_404(Solicitacao, uuid=uuid, usuario=request.user)
    if not solicitacao.can_cancel:
        return redirect('solicitacao_detail', uuid=solicitacao.uuid)
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        solicitacao.status = Solicitacao.Status.CANCELADA
        solicitacao.motivo_cancelamento = motivo
        solicitacao.save(update_fields=['status', 'motivo_cancelamento'])
        return redirect('solicitacao_detail', uuid=solicitacao.uuid)
    return render(request, 'core/agendamento_cancel.html', {'solicitacao': solicitacao})


# ---- helpers ----

def _send_confirmation_email(request, solicitacao):
    tipo = solicitacao.get_tipo_solicitacao_display()
    subject = f'Solicitação recebida — {tipo} #{solicitacao.uuid}'
    detail_url = request.build_absolute_uri(reverse('solicitacao_detail', args=[solicitacao.uuid]))
    message = (
        f'Olá, {solicitacao.usuario.first_name}!\n\n'
        f'Recebemos {tipo.lower()} (#{solicitacao.uuid}).\n'
        f'Status atual: {solicitacao.get_status_display()}\n\n'
        f'Você pode acompanhar o andamento em:\n{detail_url}'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cityclean.com')
    send_mail(subject, message, from_email, [solicitacao.usuario.email], fail_silently=True)


# Keep old generic create view for backwards compat (forms.SolicitacaoForm)
@login_required
def solicitacao_create(request):
    from .forms import SolicitacaoForm
    if request.method == 'POST':
        form = SolicitacaoForm(request.POST, request.FILES)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.usuario = request.user
            solicitacao.save()
            form.save_m2m()
            return redirect('solicitacao_list')
    else:
        form = SolicitacaoForm()
    return render(request, 'core/solicitacao_form.html', {'form': form})

