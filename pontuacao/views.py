from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from .models import Desbravador, Pontuacao, ConfiguracaoSistema

class PublicHomeView(TemplateView):
    """
    Página inicial pública. Exibe o Top 3 e/ou Ranking Geral estritamente
    de acordo com as configurações salvas no banco de dados pela Diretoria.
    """
    template_name = 'pontuacao/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = ConfiguracaoSistema.get_solo()
        context['config'] = config

        # TOP 3 — Omitido da view se desativado pela diretoria
        if config.top3_publico:
            top3_qs = Desbravador.objects.filter(ativo=True).select_related('unidade').annotate(
                total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
            ).order_by('-total_pontos_calc', 'nome')[:3]
            context['top3_list'] = list(top3_qs)
        else:
            context['top3_list'] = None

        # RANKING GERAL — Omitido da view se desativado pela diretoria
        if config.ranking_publico:
            ranking_qs = Desbravador.objects.filter(ativo=True).select_related('unidade').annotate(
                total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
            ).order_by('-total_pontos_calc', 'nome')
            context['ranking_list'] = list(ranking_qs)
        else:
            context['ranking_list'] = None

        return context


class PerfilDesbravadorView(LoginRequiredMixin, TemplateView):
    """
    Perfil privado do desbravador logado.
    REGRA DE SEGURANÇA NO BACKEND: Desbravadores comuns só podem visualizar
    o seu próprio perfil. Tentativas de acessar dados de terceiros são bloqueadas.
    """
    template_name = 'pontuacao/perfil.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Diretoria (staff/superuser) possui permissão de consulta ampla
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Desbravador comum deve obrigatoriamente possuir perfil associado
        if not hasattr(request.user, 'desbravador') or not request.user.desbravador.ativo:
            return HttpResponseForbidden("Acesso restrito: Sua conta não está vinculada a um perfil de desbravador ativo.")

        # Impedir tentativa de passagem de ID de terceiros na URL/Query String
        target_id = request.GET.get('id')
        if target_id and str(target_id) != str(request.user.desbravador.id):
            return HttpResponseForbidden("Segurança: Você não tem permissão para visualizar o perfil de outro desbravador.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Se for Diretoria e informou id na query string
        if (user.is_staff or user.is_superuser) and self.request.GET.get('id'):
            desbravador_id = self.request.GET.get('id')
            desbravador = get_object_or_404(Desbravador, pk=desbravador_id)
        elif hasattr(user, 'desbravador'):
            desbravador = user.desbravador
        else:
            # Caso seja staff sem perfil de desbravador associado
            desbravador = Desbravador.objects.filter(ativo=True).first()

        context['desbravador'] = desbravador
        if desbravador:
            context['historico'] = desbravador.pontuacoes.select_related('criado_por').order_by('-data_hora', '-created_at')
            context['total_pontos'] = desbravador.total_pontos
        else:
            context['historico'] = []
            context['total_pontos'] = 0

        return context


class CustomLoginView(LoginView):
    """
    Tela de login responsiva para Desbravadores e Diretoria.
    """
    template_name = 'pontuacao/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return '/admin/'
        return '/perfil/'
