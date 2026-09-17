from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'pontuacao'

urlpatterns = [
    path('', views.PublicHomeView.as_view(), name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='pontuacao:index'), name='logout'),
    path('perfil/', views.PerfilDesbravadorView.as_view(), name='perfil'),
]
