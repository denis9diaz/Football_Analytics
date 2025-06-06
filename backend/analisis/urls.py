from django.urls import path
from .views import (
    LigaListAPIView,
    PartidoListAPIView,
    partidos_analizados_por_metodo,
    FavoritoListCreateView,
    FavoritoDeleteView,
    ranking_partidos_analizados,
    equipos_por_liga,
    equipos_por_liga_y_temporada,
)

urlpatterns = [
    path('ligas/', LigaListAPIView.as_view(), name='ligas-list'),
    path('partidos/', PartidoListAPIView.as_view(), name='partidos-list'),
    path('partidos-analisis/<str:metodo_nombre>/', partidos_analizados_por_metodo, name='partidos-analisis'),
    path('favoritos/', FavoritoListCreateView.as_view(), name='favoritos-list-create'),
    path('favoritos/<int:id>/', FavoritoDeleteView.as_view(), name='favoritos-delete'),
    path('ranking-partidos-analizados/', ranking_partidos_analizados, name='ranking-partidos'),
    path('ligas/<int:liga_id>/equipos/', equipos_por_liga, name='equipos-por-liga'),
    path('ligas/<int:liga_id>/equipos-temporada/', equipos_por_liga_y_temporada),
]
