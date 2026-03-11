from django.urls import path
from . import views

urlpatterns = [
    path('', views.solicitacao_list, name='solicitacao_list'),
    path('solicitacao/new/', views.solicitacao_create, name='solicitacao_create'),
    path('solicitacao/<int:pk>/', views.solicitacao_detail, name='solicitacao_detail'),
]
