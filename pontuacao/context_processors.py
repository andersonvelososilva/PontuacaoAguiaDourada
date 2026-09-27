from django.conf import settings

def clube_settings(request):
    """
    Injeta o nome do clube, URL da logo e configurações públicas nos templates.
    """
    cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', '')
    if cloud_name:
        logo_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/static/logo_aguia_dourada.png"
    else:
        logo_url = "/static/images/logo.png"

    return {
        'NOME_DO_CLUBE': getattr(settings, 'NOME_DO_CLUBE', 'Clube de Desbravadores Águia Dourada'),
        'EXIBIR_HISTORICO_PUBLICO': getattr(settings, 'EXIBIR_HISTORICO_PUBLICO', True),
        'VERSAO_APP': getattr(settings, 'VERSAO_APP', 'v1.3'),
        'LOGO_URL': logo_url,
    }
