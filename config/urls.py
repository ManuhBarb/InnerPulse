from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from app.views import *
from app.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('cidade/', CidadesView.as_view(), name='cidade'),
    path('ocupacao/', OcupacoesView.as_view(), name='ocupacao'),
    path('usuario/', CadastroView.as_view(), name='cadastro'),
    path('evento/', EventosView.as_view(), name='evento'),
    path('agendamento/', AgendamentosView.as_view(), name='agendamento'),
    path('relatorio/', RelatoriosView.as_view(), name='relatorio'),
    path('doenca/', DoencasView.as_view(), name='doenca'),
    path('calcule/', CalculeView.as_view(), name='calcule'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
]