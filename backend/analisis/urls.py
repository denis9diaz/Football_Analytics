from django.urls import path
from .views import LigaListAPIView, PartidoListAPIView, partidos_analizados_por_metodo

urlpatterns = [
    path('ligas/', LigaListAPIView.as_view(), name='ligas-list'),
    path('partidos/', PartidoListAPIView.as_view(), name='partidos-list'),
    path('partidos-analisis/<str:metodo_nombre>/', partidos_analizados_por_metodo),
]
