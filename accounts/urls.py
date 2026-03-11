from django.urls import path
import sesame.views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/', sesame.views.LoginView.as_view(), name='sesame-login'),
]
