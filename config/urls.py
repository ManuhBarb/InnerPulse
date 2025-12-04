from django.contrib import admin
from django.urls import path
from app import views
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('cidade/', CidadesView.as_view(), name='cidade'),
    path('ocupacao/', OcupacoesView.as_view(), name='ocupacao'),
    path('usuario/', CadastroView.as_view(), name='cadastro'),
    path('evento/', EventosView.as_view(), name='evento'),
    # path('agendamento/', AgendamentosView.as_view(), name='agendamento'),
    path('relatorio/', RelatoriosView.as_view(), name='relatorio'),
    path('doenca/', DoencasView.as_view(), name='doenca'),
    path('calcule/', CalculeView.as_view(), name='calcule'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('comment/<int:comment_id>/like/', LikeCommentView.as_view(), name='like_comment'),
    path('comment/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete_comment'),
    path('salvar-resultado/', SalvarResultadoView.as_view(), name='salvar_resultado'),
    path('meus-resultados/', MeusResultadosView.as_view(), name='meus_resultados'),
    path('deletar-resultado/<int:resultado_id>/', DeletarResultadoView.as_view(), name='deletar_resultado'),
    path('add-comment/', add_comment, name='add_comment'),
    # path("salvar-agendamento/", salvar_agendamento, name="salvar_agendamento"),





    path('agendar/', views.agendar_view, name='agendamento'),
    path('agendar/<int:pk>/delete/', views.agendamento_delete, name='agendamento_delete'),
]