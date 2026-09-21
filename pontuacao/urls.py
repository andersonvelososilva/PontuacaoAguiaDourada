from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'pontuacao'

urlpatterns = [
    # Rotas Públicas e Autenticação
    path('', views.PublicHomeView.as_view(), name='index'),
    path('ranking/', views.PublicRankingView.as_view(), name='public_ranking'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='pontuacao:index'), name='logout'),
    path('perfil/', views.PerfilDesbravadorView.as_view(), name='perfil'),

    # Rotas do Painel Administrativo da Diretoria
    path('diretoria/', views.DiretoriaDashboardView.as_view(), name='diretoria_dashboard'),
    path('diretoria/desbravadores/', views.DiretoriaDesbravadorListView.as_view(), name='diretoria_desbravadores'),
    path('diretoria/desbravadores/<int:pk>/', views.DiretoriaDesbravadorUpdateView.as_view(), name='diretoria_desbravador_edit'),
    path('diretoria/pontuacao/', views.DiretoriaLancarPontuacaoView.as_view(), name='diretoria_pontuacao'),
    path('diretoria/ranking/', views.DiretoriaRankingView.as_view(), name='diretoria_ranking'),
    path('diretoria/configuracoes/', views.DiretoriaConfiguracoesView.as_view(), name='diretoria_configuracoes'),
]
