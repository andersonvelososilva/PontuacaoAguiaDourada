from django.conf import settings

def clube_settings(request):
    """
    Injeta o nome do clube, URL da logo, ícones PWA e configurações públicas nos templates.
    """
    cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', '')
    if cloud_name:
        logo_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/static/logo_aguia_dourada.png"
        icon_192_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/static/icon_192.png"
        icon_512_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/static/icon_512.png"
        apple_icon_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/static/apple_touch_icon.png"
    else:
        logo_url = "/static/images/logo.png"
        icon_192_url = "/static/icons/icon-192.png"
        icon_512_url = "/static/icons/icon-512.png"
        apple_icon_url = "/static/icons/apple-touch-icon.png"

    return {
        'NOME_DO_CLUBE': getattr(settings, 'NOME_DO_CLUBE', 'Clube de Desbravadores Águia Dourada'),
        'EXIBIR_HISTORICO_PUBLICO': getattr(settings, 'EXIBIR_HISTORICO_PUBLICO', True),
        'VERSAO_APP': getattr(settings, 'VERSAO_APP', 'v1.6'),
        'LOGO_URL': logo_url,
        'ICON_192_URL': icon_192_url,
        'ICON_512_URL': icon_512_url,
        'APPLE_ICON_URL': apple_icon_url,
    }
