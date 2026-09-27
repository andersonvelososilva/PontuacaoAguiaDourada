from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView, ListView, UpdateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.contrib import messages
from django import forms
from .models import Desbravador, Unidade, Pontuacao, ConfiguracaoSistema

# --- MIXIN DE SEGURANÇA PARA A DIRETORIA ---

class DiretoriaRequiredMixin(UserPassesTestMixin):
    """Garante que apenas membros autenticados da Diretoria (is_staff) acessem a view."""
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('pontuacao:login')
        return HttpResponseForbidden("Acesso restrito à Diretoria do Clube.")


# --- VIEWS PÚBLICAS E AUTENTICAÇÃO ---

class PublicHomeView(TemplateView):
    """
    Página inicial pública limpa (http://127.0.0.1:8000/).
    Exibe o título 'Sistema de Pontos - Águia Dourada' e as opções: Ver Ranking e Entrar.
    """
    template_name = 'pontuacao/index.html'


class PublicRankingView(TemplateView):
    """
    Página pública dedicada de Ranking (http://127.0.0.1:8000/ranking/).
    Busca dinamicamente a última configuração salva pela Diretoria no banco de dados.
    """
    template_name = 'pontuacao/ranking_publico.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Busca dinamicamente do banco de dados na hora da requisição
        config = ConfiguracaoSistema.get_solo()
        context['config'] = config

        if config.ranking_modo == 'OCULTO':
            context['ranking_list'] = None
        else:
            qs = Desbravador.objects.filter(ativo=True).select_related('unidade').annotate(
                total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
            ).order_by('-total_pontos_calc', 'nome')

            if config.ranking_modo == 'PARCIAL':
                limite = max(1, config.ranking_limite_publico)
                qs = qs[:limite]

            context['ranking_list'] = list(qs)

        return context


class CustomLoginView(LoginView):
    """
    Login unificado. Redireciona Diretoria para /diretoria/ e Desbravador para /perfil/.
    """
    template_name = 'pontuacao/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return '/diretoria/'
        return '/perfil/'


class PerfilDesbravadorView(LoginRequiredMixin, TemplateView):
    """
    Perfil privado do desbravador. Exibe foto, nome, unidade, total de pontos,
    extrato de lançamentos e CLASSIFICAÇÃO INDIVIDUAL no ranking.
    REGRA DE SEGURANÇA: Desbravadores comuns só acessam seu próprio perfil.
    """
    template_name = 'pontuacao/perfil.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not hasattr(request.user, 'desbravador') or not request.user.desbravador.ativo:
            return HttpResponseForbidden("Sua conta não está vinculada a um perfil de desbravador ativo.")

        target_id = request.GET.get('id')
        if target_id and str(target_id) != str(request.user.desbravador.id):
            return HttpResponseForbidden("Segurança: Você não tem permissão para visualizar o perfil de outro desbravador.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if (user.is_staff or user.is_superuser) and self.request.GET.get('id'):
            desbravador = get_object_or_404(Desbravador, pk=self.request.GET.get('id'))
        elif hasattr(user, 'desbravador'):
            desbravador = user.desbravador
        else:
            desbravador = Desbravador.objects.filter(ativo=True).first()

        context['desbravador'] = desbravador

        if desbravador:
            context['historico'] = desbravador.pontuacoes.select_related('criado_por').order_by('-data_hora', '-created_at')
            context['total_pontos'] = desbravador.total_pontos

            # CÁLCULO DA CLASSIFICAÇÃO INDIVIDUAL NO BACKEND (Ex: 4º Lugar)
            todos_ativos = list(Desbravador.objects.filter(ativo=True).annotate(
                total_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
            ).order_by('-total_calc', 'nome'))

            try:
                posicao = [d.id for d in todos_ativos].index(desbravador.id) + 1
                context['posicao_ranking'] = posicao
            except ValueError:
                context['posicao_ranking'] = None
        else:
            context['historico'] = []
            context['total_pontos'] = 0
            context['posicao_ranking'] = None

        return context


# --- FORMULÁRIOS E VIEWS DO PAINEL DA DIRETORIA (/diretoria/) ---

class FormLancarPontuacao(forms.Form):
    TIPO_CHOICES = [
        ('ADICIONAR', 'Adicionar Pontos (+)'),
        ('REMOVER', 'Remover Pontos (-)'),
    ]
    desbravador = forms.ModelChoiceField(
        queryset=Desbravador.objects.filter(ativo=True),
        label="Desbravador",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label="Tipo de Lançamento",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade de Pontos",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10'})
    )
    motivo = forms.CharField(
        max_length=255,
        required=True,
        label="Motivo (Obrigatório)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Presença na reunião / Atraso na formação'})
    )


class FormConfiguracoesRanking(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = ['ranking_modo', 'ranking_limite_publico', 'mostrar_nomes_ranking', 'mostrar_pontos_ranking', 'mostrar_fotos_ranking']
        widgets = {
            'ranking_modo': forms.Select(attrs={'class': 'form-select'}),
            'ranking_limite_publico': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'mostrar_nomes_ranking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_pontos_ranking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_fotos_ranking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DiretoriaDashboardView(DiretoriaRequiredMixin, TemplateView):
    """
    Dashboard principal da Diretoria com estatísticas e atalhos rápidos.
    """
    template_name = 'diretoria/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_desbravadores_ativos'] = Desbravador.objects.filter(ativo=True).count()
        context['total_desbravadores'] = Desbravador.objects.count()
        context['total_unidades'] = Unidade.objects.filter(ativo=True).count()
        context['total_lancamentos'] = Pontuacao.objects.count()
        context['config'] = ConfiguracaoSistema.get_solo()
        return context


class DiretoriaDesbravadorListView(DiretoriaRequiredMixin, ListView):
    """
    Listagem de desbravadores para consulta e edição pela Diretoria.
    """
    model = Desbravador
    template_name = 'diretoria/desbravadores.html'
    context_object_name = 'desbravadores'

    def get_queryset(self):
        qs = Desbravador.objects.select_related('unidade', 'user').annotate(
            total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
        )
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(Q(nome__icontains=query) | Q(unidade__nome__icontains=query))

        unidade_id = self.request.GET.get('unidade')
        if unidade_id and unidade_id.isdigit():
            qs = qs.filter(unidade_id=int(unidade_id))

        status = self.request.GET.get('status')
        if status == 'ativos':
            qs = qs.filter(ativo=True)
        elif status == 'inativos':
            qs = qs.filter(ativo=False)

        return qs.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unidades'] = Unidade.objects.all()
        context['query_q'] = self.request.GET.get('q', '')
        context['unidade_sel'] = self.request.GET.get('unidade', '')
        context['status_sel'] = self.request.GET.get('status', '')
        return context


class DiretoriaDesbravadorUpdateView(DiretoriaRequiredMixin, UpdateView):
    """
    Edição dos dados cadastrais do desbravador (Nome, Foto, Unidade, Status, Conta de Usuário).
    """
    model = Desbravador
    template_name = 'diretoria/desbravador_form.html'
    fields = ['nome', 'foto', 'unidade', 'ativo', 'user']
    success_url = '/diretoria/desbravadores/'

    def form_valid(self, form):
        messages.success(self.request, f"Dados do desbravador '{form.instance.nome}' atualizados com sucesso!")
        return super().form_valid(form)


class DiretoriaLancarPontuacaoView(DiretoriaRequiredMixin, TemplateView):
    """
    Formulário para lançar adição (+) ou remoção (-) de pontos individualmente ou em massa (por grupo/unidade).
    """
    template_name = 'diretoria/pontuacao_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['desbravadores'] = Desbravador.objects.filter(ativo=True).select_related('unidade').order_by('unidade__nome', 'nome')
        context['unidades'] = Unidade.objects.filter(ativo=True).order_by('nome')
        context['form_individual'] = FormLancarPontuacao()
        return context

    def post(self, request, *args, **kwargs):
        modo = request.POST.get('modo', 'INDIVIDUAL')

        if modo == 'MASSA':
            desbravadores_ids = request.POST.getlist('desbravadores_ids')
            unidade_id = request.POST.get('unidade_id', '')
            tipo = request.POST.get('tipo', 'ADICIONAR')
            try:
                qtd = int(request.POST.get('quantidade', 0))
            except (ValueError, TypeError):
                qtd = 0

            motivo = request.POST.get('motivo', '').strip()

            if not motivo:
                messages.error(request, "O campo Motivo / Justificativa é obrigatório.")
                return self.get(request, *args, **kwargs)

            if qtd <= 0:
                messages.error(request, "A quantidade de pontos deve ser um número positivo maior que zero.")
                return self.get(request, *args, **kwargs)

            # Determina os desbravadores alvo
            if unidade_id == 'TODAS':
                desbravadores = list(Desbravador.objects.filter(ativo=True))
            elif unidade_id and unidade_id.isdigit():
                desbravadores = list(Desbravador.objects.filter(unidade_id=int(unidade_id), ativo=True))
            elif desbravadores_ids:
                desbravadores = list(Desbravador.objects.filter(id__in=desbravadores_ids, ativo=True))
            else:
                desbravadores = []

            if not desbravadores:
                messages.error(request, "Nenhum desbravador foi selecionado para o lançamento em massa.")
                return self.get(request, *args, **kwargs)

            pontos_finais = -abs(qtd) if tipo == 'REMOVER' else abs(qtd)
            
            pontuacoes_objs = [
                Pontuacao(
                    desbravador=d,
                    pontos=pontos_finais,
                    motivo=motivo,
                    criado_por=request.user
                )
                for d in desbravadores
            ]
            Pontuacao.objects.bulk_create(pontuacoes_objs)

            sinal_txt = f"{pontos_finais}" if pontos_finais < 0 else f"+{pontos_finais}"
            messages.success(
                request,
                f"Lançamento em massa efetuado com sucesso! {sinal_txt} pontos lançados para {len(desbravadores)} desbravador(es) ('{motivo}')."
            )
            return redirect('pontuacao:diretoria_pontuacao')

        else:
            form = FormLancarPontuacao(request.POST)
            if form.is_valid():
                desbravador = form.cleaned_data['desbravador']
                tipo = form.cleaned_data['tipo']
                qtd = form.cleaned_data['quantidade']
                motivo = form.cleaned_data['motivo']

                pontos_finais = -abs(qtd) if tipo == 'REMOVER' else abs(qtd)

                Pontuacao.objects.create(
                    desbravador=desbravador,
                    pontos=pontos_finais,
                    motivo=motivo,
                    criado_por=request.user
                )

                sinal_txt = f"{pontos_finais}" if pontos_finais < 0 else f"+{pontos_finais}"
                messages.success(request, f"Lançamento efetuado: {sinal_txt} pontos para {desbravador.nome} ('{motivo}').")
                return redirect('pontuacao:diretoria_pontuacao')
            else:
                context = self.get_context_data(**kwargs)
                context['form_individual'] = form
                return self.render_to_response(context)


class DiretoriaRankingView(DiretoriaRequiredMixin, ListView):
    """
    Ranking administrativo completo (visível 100% para a diretoria, independente das regras públicas).
    """
    model = Desbravador
    template_name = 'diretoria/ranking.html'
    context_object_name = 'ranking'

    def get_queryset(self):
        return Desbravador.objects.filter(ativo=True).select_related('unidade').annotate(
            total_pontos_calc=Coalesce(Sum('pontuacoes__pontos'), 0)
        ).order_by('-total_pontos_calc', 'nome')


class DiretoriaConfiguracoesView(DiretoriaRequiredMixin, UpdateView):
    """
    Configuração das regras públicas de exibição do ranking pela diretoria.
    """
    model = ConfiguracaoSistema
    form_class = FormConfiguracoesRanking
    template_name = 'diretoria/configuracoes.html'
    success_url = '/diretoria/configuracoes/'

    def get_object(self, queryset=None):
        return ConfiguracaoSistema.get_solo()

    def form_valid(self, form):
        messages.success(self.request, "Configurações de visibilidade do ranking atualizadas com sucesso!")
        return super().form_valid(form)


class DiretoriaHistoricoGeralView(DiretoriaRequiredMixin, ListView):
    """
    Exibe o histórico geral de todos os lançamentos e remoções de pontuações,
    identificando qual membro da diretoria efetuou a alteração.
    """
    model = Pontuacao
    template_name = 'diretoria/historico.html'
    context_object_name = 'historico'
    paginate_by = 50

    def get_queryset(self):
        qs = Pontuacao.objects.select_related('desbravador', 'desbravador__unidade', 'criado_por')

        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(desbravador__nome__icontains=query) |
                Q(motivo__icontains=query) |
                Q(criado_por__username__icontains=query) |
                Q(criado_por__first_name__icontains=query)
            )

        unidade_id = self.request.GET.get('unidade')
        if unidade_id and unidade_id.isdigit():
            qs = qs.filter(desbravador__unidade_id=int(unidade_id))

        return qs.order_by('-data_hora', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unidades'] = Unidade.objects.all()
        context['query_q'] = self.request.GET.get('q', '')
        context['unidade_sel'] = self.request.GET.get('unidade', '')
        return context
