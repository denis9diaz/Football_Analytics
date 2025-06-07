from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status
from datetime import datetime, timedelta
from django.utils.timezone import now

from .models import Liga, Partido, PartidoAnalisis, Favorito, Equipo
from .serializers import (
    LigaSerializer,
    PartidoSerializer,
    PartidoAnalisisSerializer,
    FavoritoSerializer,
)

def obtener_temporada(fecha):
    año = fecha.year
    return f"{año}-{año + 1}" if fecha.month >= 7 else f"{año - 1}-{año}"

# === LIGAS ===
class LigaListAPIView(APIView):
    def get(self, request):
        ligas = Liga.objects.all()
        serializer = LigaSerializer(ligas, many=True)
        return Response(serializer.data)

# === PARTIDOS ===
class PartidoListAPIView(APIView):
    def get(self, request):
        partidos = Partido.objects.all().order_by('fecha')
        serializer = PartidoSerializer(partidos, many=True)
        return Response(serializer.data)

# === PARTIDOS ANALIZADOS POR MÉTODO ===
@api_view(['GET'])
def partidos_analizados_por_metodo(request, metodo_nombre):
    partidos = PartidoAnalisis.objects.filter(
        metodo__nombre=metodo_nombre
    ).select_related('partido', 'partido__liga')
    serializer = PartidoAnalisisSerializer(partidos, many=True)
    return Response(serializer.data)

# === RANKING PARTIDOS ANALIZADOS ===
@api_view(['GET'])
def ranking_partidos_analizados(request):
    hoy = now().date()

    partidos_por_metodo = (
        PartidoAnalisis.objects.filter(
            partido__fecha__date=hoy,
            porcentaje_acierto__isnull=False
        )
        .select_related('partido', 'partido__liga', 'metodo')
        .order_by('-porcentaje_acierto')
    )

    ranking = {}
    for partido in partidos_por_metodo:
        metodo_nombre = partido.metodo.nombre
        if metodo_nombre not in ranking:
            ranking[metodo_nombre] = []
        if len(ranking[metodo_nombre]) < 5:
            ranking[metodo_nombre].append(partido)

    response_data = {
        metodo: PartidoAnalisisSerializer(partidos, many=True).data
        for metodo, partidos in ranking.items()
    }

    return Response(response_data)


# === FAVORITOS ===
class FavoritoListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorito.objects.filter(usuario=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoritoDeleteView(generics.DestroyAPIView):
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Favorito.objects.filter(usuario=self.request.user)

        
# === ELIMINAR FAVORITOS DEL DÍA ANTERIOR ===
class EliminarFavoritosDiaAnteriorView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        usuario = request.user
        ayer = now().date() - timedelta(days=1)
        Favorito.objects.filter(usuario=usuario, partido_analisis__partido__fecha__date=ayer).delete()
        return Response({"message": "Favoritos del día anterior eliminados."}, status=status.HTTP_200_OK)


# === EQUIPOS POR LIGA ===
@api_view(['GET'])
def equipos_por_liga(request, liga_id):
    try:
        liga = Liga.objects.get(id=liga_id)
        equipos = liga.equipos.prefetch_related('rachas')

        data = []
        for equipo in equipos:
            rachas_actuales = equipo.rachas.filter(tipo='actual').values(
                'condicion', 'contexto', 'cantidad', 'liga_id'
            )
            rachas_historicas = equipo.rachas.filter(tipo='historica').values(
                'condicion', 'contexto', 'cantidad', 'liga_id'
            )

            data.append({
                'equipo': equipo.nombre,
                'rachas_actuales': list(rachas_actuales),
                'rachas_historicas': list(rachas_historicas),
            })

        return Response(data, status=status.HTTP_200_OK)
    except Liga.DoesNotExist:
        return Response({'error': 'Liga no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def equipos_por_liga_y_temporada(request, liga_id):
    hoy = datetime.today()
    temporada_actual = obtener_temporada(hoy)

    # Filtra partidos de esa liga
    partidos = Partido.objects.filter(liga_id=liga_id).select_related('equipo_local', 'equipo_visitante')

    equipos_ids = set()

    for partido in partidos:
        temporada = obtener_temporada(partido.fecha)
        if temporada == temporada_actual:
            if partido.equipo_local:
                equipos_ids.add(partido.equipo_local.id)
            if partido.equipo_visitante:
                equipos_ids.add(partido.equipo_visitante.id)

    # Obtiene los equipos válidos y sus rachas
    equipos = Equipo.objects.filter(id__in=equipos_ids).prefetch_related('rachas')

    data = [{"equipo": equipo.nombre} for equipo in equipos]

    return Response(data, status=status.HTTP_200_OK)
