import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponse
from django.views.static import serve

def service_worker_view(request):
    sw_path = os.path.join(settings.BASE_DIR, 'pontuacao', 'static', 'js', 'sw.js')
    with open(sw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pontuacao.urls', namespace='pontuacao')),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/manifest+json'), name='manifest'),
    path('sw.js', service_worker_view, name='service_worker'),
]

urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Customização do título do Django Admin
admin.site.site_header = "Painel Administrativo — Clube de Desbravadores"
admin.site.site_title = "Gestão de Pontuação"
admin.site.index_title = "Administração do Clube"
