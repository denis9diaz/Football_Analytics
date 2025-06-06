from rest_framework import serializers
from .models import Liga, Partido, PartidoAnalisis, Favorito, RachaEquipo, Equipo

class LigaSerializer(serializers.ModelSerializer):
    nivel = serializers.SerializerMethodField()

    def get_nivel(self, obj):
        return obj.nivel if obj.nivel is not None else 99

    class Meta:
        model = Liga
        fields = ['id', 'nombre', 'codigo_pais', 'pais', 'codigo_iso_pais', 'codigo_api', 'nivel']

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
            'marco_local', 'marco_visitante', 'over_1_5_local',
            'gol_ht',  # ✅ añadimos este campo
        ]
        read_only_fields = ['gol_ht']

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
            'favorito',
            'porcentaje_acierto',
            'equipo_destacado',
        ]

class FavoritoSerializer(serializers.ModelSerializer):
    partido_analisis = PartidoAnalisisSerializer(read_only=True)
    partido_analisis_id = serializers.PrimaryKeyRelatedField(
        queryset=PartidoAnalisis.objects.all(), source='partido_analisis', write_only=True
    )

    class Meta:
        model = Favorito
        fields = ['id', 'partido_analisis', 'partido_analisis_id']

class RachaEquipoSerializer(serializers.ModelSerializer):
    liga_id = serializers.IntegerField(source='liga.id', read_only=True)

    class Meta:
        model = RachaEquipo
        fields = ['condicion', 'contexto', 'cantidad', 'tipo', 'liga_id']

class EquipoSerializer(serializers.ModelSerializer):
    rachas_actuales = serializers.SerializerMethodField()
    rachas_historicas = serializers.SerializerMethodField()

    class Meta:
        model = Equipo
        fields = ['nombre', 'rachas_actuales', 'rachas_historicas']

    def get_rachas_actuales(self, obj):
        queryset = obj.rachas.filter(tipo='actual')
        return RachaEquipoSerializer(queryset, many=True).data

    def get_rachas_historicas(self, obj):
        queryset = obj.rachas.filter(tipo='historica')
        return RachaEquipoSerializer(queryset, many=True).data
