from django.conf import settings

def clube_settings(request):
    """
    Injeta o nome do clube e configurações públicas nos templates.
    """
    return {
        'NOME_DO_CLUBE': getattr(settings, 'NOME_DO_CLUBE', 'Clube de Desbravadores Águia Dourada'),
        'EXIBIR_HISTORICO_PUBLICO': getattr(settings, 'EXIBIR_HISTORICO_PUBLICO', True),
        'VERSAO_APP': getattr(settings, 'VERSAO_APP', 'v1.3'),
    }
