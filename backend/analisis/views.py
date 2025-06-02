from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status

from .models import Liga, Partido, PartidoAnalisis, Favorito
from .serializers import (
    LigaSerializer,
    PartidoSerializer,
    PartidoAnalisisSerializer,
    FavoritoSerializer,
)

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
