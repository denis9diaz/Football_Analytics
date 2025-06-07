from django.contrib import admin
from .models import Suscripcion

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plan', 'fecha_inicio', 'fecha_fin', 'cancelada', 'esta_activa')

    def esta_activa(self, obj):
        return obj.esta_activa()
    esta_activa.boolean = True
