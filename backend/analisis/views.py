from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Liga, Partido, PartidoAnalisis
from .serializers import LigaSerializer, PartidoSerializer, PartidoAnalisisSerializer

class LigaListAPIView(APIView):
    def get(self, request):
        ligas = Liga.objects.all()
        serializer = LigaSerializer(ligas, many=True)
        return Response(serializer.data)

class PartidoListAPIView(APIView):
    def get(self, request):
        partidos = Partido.objects.all().order_by('fecha')
        serializer = PartidoSerializer(partidos, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def partidos_analizados_por_metodo(request, metodo_nombre):
    partidos = PartidoAnalisis.objects.filter(metodo__nombre=metodo_nombre).select_related('partido', 'partido__liga')
    serializer = PartidoAnalisisSerializer(partidos, many=True)
    return Response(serializer.data)
