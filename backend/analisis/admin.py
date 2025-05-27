from django.contrib import admin
from django.utils import timezone
from zoneinfo import ZoneInfo
from .models import (
    Liga, Equipo, Partido,
    MetodoAnalisis, PartidoAnalisis,
    RachaEquipo
)

admin.site.register(Liga)
admin.site.register(Equipo)
admin.site.register(MetodoAnalisis)
admin.site.register(PartidoAnalisis)
admin.site.register(RachaEquipo)

class PartidoAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if obj.fecha and timezone.is_naive(obj.fecha):
            # Convierte de hora española a UTC correctamente
            obj.fecha = timezone.make_aware(obj.fecha, ZoneInfo("Europe/Madrid")).astimezone(timezone.utc)
        super().save_model(request, obj, form, change)

admin.site.register(Partido, PartidoAdmin)
