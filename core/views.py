from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import SolicitacaoForm
from .models import Solicitacao


@login_required
def solicitacao_create(request):
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


@login_required
def solicitacao_list(request):
    qs = Solicitacao.objects.filter(usuario=request.user).order_by('-data_criacao')
    return render(request, 'core/solicitacao_list.html', {'solicitacoes': qs})


@login_required
def solicitacao_detail(request, pk):
    s = get_object_or_404(Solicitacao, pk=pk, usuario=request.user)
    return render(request, 'core/solicitacao_detail.html', {'solicitacao': s})
