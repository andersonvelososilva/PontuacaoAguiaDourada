from django.urls import path
from . import views

app_name = 'pontuacao'

urlpatterns = [
    path('', views.DesbravadorListView.as_view(), name='index'),
    path('desbravador/<int:pk>/', views.DesbravadorDetailView.as_view(), name='detalhe'),
    path('ranking/', views.RankingView.as_view(), name='ranking'),
]
