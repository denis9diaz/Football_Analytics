from rest_framework import serializers
from .models import Liga, Partido, PartidoAnalisis

class LigaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liga
        fields = ['id', 'nombre', 'codigo_pais']

class PartidoSerializer(serializers.ModelSerializer):
    equipo_local = serializers.StringRelatedField()
    equipo_visitante = serializers.StringRelatedField()
    liga = LigaSerializer()

    class Meta:
        model = Partido
        fields = [
            'id', 'fecha', 'liga', 'equipo_local', 'equipo_visitante',
            'goles_local_ht', 'goles_visitante_ht',
            'goles_local_ft', 'goles_visitante_ft',
            'resultado_1x2', 'over_1_5', 'over_2_5', 'btts',
            'marco_local', 'marco_visitante', 'over_1_5_local'
        ]

class PartidoAnalisisSerializer(serializers.ModelSerializer):
    partido = PartidoSerializer()  # anidamos partido con liga ya expandida
    metodo = serializers.StringRelatedField()  # devuelve el nombre del método

    class Meta:
        model = PartidoAnalisis
        fields = [
            'id',
            'partido',
            'metodo',
            'cuota_estim_real',
            'cuota_casa_apuestas',
            'valor_estimado',
            'favorito'
        ]
