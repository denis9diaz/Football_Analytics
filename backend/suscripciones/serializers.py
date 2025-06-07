from rest_framework import serializers
from .models import Suscripcion

class SuscripcionSerializer(serializers.ModelSerializer):
    esta_activa = serializers.SerializerMethodField()
    
    class Meta:
        model = Suscripcion
        fields = ['plan', 'fecha_inicio', 'fecha_fin', 'cancelada', 'esta_activa']

    def get_esta_activa(self, obj):
        return obj.esta_activa()

class ContratarSuscripcionSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=Suscripcion.PLANES)

    def validate_plan(self, value):
        planes_validos = [p[0] for p in Suscripcion.PLANES]
        if value not in planes_validos:
            raise serializers.ValidationError("Plan no válido.")
        return value
