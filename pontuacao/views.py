from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.views.generic import ListView, DetailView
from django.conf import settings
from .models import Desbravador, Unidade, Pontuacao

class DesbravadorListView(ListView):
    """
    Página inicial pública com busca em tempo real/filtro e lista de desbravadores.
    """
    model = Desbravador
    template_name = 'pontuacao/index.html'
    context_object_name = 'desbravadores'

    def get_queryset(self):
        # Apenas desbravadores ativos são exibidos publicamente por padrão
        queryset = Desbravador.objects.filter(ativo=True).select_related('unidade').annotate(
            total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
        )
        
        # Filtro por busca textual (nome ou nome da unidade)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) | Q(unidade__nome__icontains=query)
            )

        # Filtro por unidade específica
        unidade_id = self.request.GET.get('unidade')
        if unidade_id and unidade_id.isdigit():
            queryset = queryset.filter(unidade_id=int(unidade_id))

        return queryset.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unidades'] = Unidade.objects.filter(ativo=True)
        context['query_q'] = self.request.GET.get('q', '')
        context['unidade_selecionada'] = self.request.GET.get('unidade', '')
        return context


class DesbravadorDetailView(DetailView):
    """
    Página de detalhes públicos do desbravador e seu histórico de pontuação.
    """
    model = Desbravador
    template_name = 'pontuacao/detalhe.html'
    context_object_name = 'desbravador'

    def get_queryset(self):
        return Desbravador.objects.filter(ativo=True).select_related('unidade')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        desbravador = self.object
        
        # Exibe o histórico se a configuração permitir
        if getattr(settings, 'EXIBIR_HISTORICO_PUBLICO', True):
            context['historico'] = desbravador.pontuacoes.select_related('criado_por').order_by('-data_hora', '-created_at')
        else:
            context['historico'] = None
            
        return context


class RankingView(ListView):
    """
    Visualização simples e opcional de ranking por pontuação.
    """
    model = Desbravador
    template_name = 'pontuacao/ranking.html'
    context_object_name = 'ranking'

    def get_queryset(self):
        return Desbravador.objects.filter(ativo=True).select_related('unidade').annotate(
            total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
        ).order_by('-total_pontos_calc', 'nome')
