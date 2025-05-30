from django.contrib import admin
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
    list_display = (
        '__str__', 'fecha', 'liga', 'equipo_local', 'equipo_visitante', 'gol_ht'
    )
    readonly_fields = ('gol_ht',)

admin.site.register(Partido, PartidoAdmin)
