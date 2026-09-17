from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pontuacao.urls', namespace='pontuacao')),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json'), name='manifest'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customização do título do Django Admin
admin.site.site_header = "Painel Administrativo — Clube de Desbravadores"
admin.site.site_title = "Gestão de Pontuação"
admin.site.index_title = "Administração do Clube"
