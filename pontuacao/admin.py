from django.contrib import admin
from django.utils.html import format_html
from .models import Unidade, Desbravador, Pontuacao

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
    list_display = ('nome', 'unidade', 'total_pontos_display', 'ativo', 'created_at')
    list_filter = ('unidade', 'ativo')
    search_fields = ('nome', 'unidade__nome')
    inlines = [PontuacaoInline]
    ordering = ('nome',)

    def total_pontos_display(self, obj):
        total = obj.total_pontos
        if total > 0:
            color = "#198754" # green
        elif total < 0:
            color = "#dc3545" # red
        else:
            color = "#6c757d" # grey
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
