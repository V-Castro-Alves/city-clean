from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('pontos-descarte/', views.pontos_descarte_view, name='pontos_descarte'),
    path('denuncia/', views.denuncia_create_view, name='denuncia_create'),
    path('solicitar-coleta/', views.agendamento_create_view, name='agendamento_create'),
    path('minhas-solicitacoes/', views.solicitacao_list, name='solicitacao_list'),
    path('solicitacao/<uuid:uuid>/', views.solicitacao_detail, name='solicitacao_detail'),
    path('solicitacao/<uuid:uuid>/cancelar/', views.solicitacao_cancel_view, name='solicitacao_cancel'),
    path('duvidas-frequentes/', views.faq_view, name='faq'),
]

