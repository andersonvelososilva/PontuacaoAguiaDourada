from django.contrib import admin
from django.utils.html import format_html
from .models import Unidade, Desbravador, Pontuacao, ConfiguracaoSistema

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ranking_modo', 'ranking_limite_publico', 'mostrar_nomes_ranking', 'mostrar_pontos_ranking', 'updated_at')

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'total_desbravadores', 'ativo', 'created_at')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    ordering = ('nome',)

    def total_desbravadores(self, obj):
        return obj.desbravadores.count()
    total_desbravadores.short_description = "Nº de Desbravadores"


class PontuacaoInline(admin.TabularInline):
    model = Pontuacao
    extra = 1
    fields = ('pontos', 'motivo', 'data_hora', 'criado_por')
    readonly_fields = ('criado_por',)

    def save_new_instance(self, request, form, commit=True):
        obj = form.save(commit=False)
        if not obj.criado_por_id:
            obj.criado_por = request.user
        if commit:
            obj.save()
        return obj


@admin.register(Desbravador)
class DesbravadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'unidade', 'user_status', 'total_pontos_display', 'ativo', 'created_at')
    list_filter = ('unidade', 'ativo')
    search_fields = ('nome', 'unidade__nome', 'user__username')
    raw_id_fields = ('user',)
    inlines = [PontuacaoInline]
    ordering = ('nome',)

    def user_status(self, obj):
        if obj.user:
            return format_html('<span style="color: #198754; font-weight: bold;">👤 {}</span>', obj.user.username)
        return format_html('<span style="color: #6c757d; font-style: italic;">Sem usuário</span>')
    user_status.short_description = "Conta de Usuário"

    def total_pontos_display(self, obj):
        total = obj.total_pontos
        if total > 0:
            color = "#198754"
        elif total < 0:
            color = "#dc3545"
        else:
            color = "#6c757d"
        return format_html('<b style="color: {}; font-size: 1.05rem;">{} pts</b>', color, total)
    total_pontos_display.short_description = "Pontuação Total"

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Pontuacao) and not instance.criado_por_id:
                instance.criado_por = request.user
            instance.save()
        formset.save_m2m()


@admin.register(Pontuacao)
class PontuacaoAdmin(admin.ModelAdmin):
    list_display = ('desbravador', 'get_unidade', 'pontos_formatados', 'motivo', 'data_hora', 'criado_por')
    list_filter = ('desbravador__unidade', 'data_hora', 'criado_por')
    search_fields = ('desbravador__nome', 'motivo')
    autocomplete_fields = ('desbravador',)
    readonly_fields = ('criado_por', 'created_at')
    ordering = ('-data_hora',)

    def get_unidade(self, obj):
        return obj.desbravador.unidade.nome
    get_unidade.short_description = "Unidade"

    def pontos_formatados(self, obj):
        if obj.pontos > 0:
            return format_html('<span style="color: #198754; font-weight: bold;">+{}</span>', obj.pontos)
        elif obj.pontos < 0:
            return format_html('<span style="color: #dc3545; font-weight: bold;">{}</span>', obj.pontos)
        return format_html('<span>0</span>')
    pontos_formatados.short_description = "Pontos"

    def save_model(self, request, obj, form, change):
        if not change or not obj.criado_por_id:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
