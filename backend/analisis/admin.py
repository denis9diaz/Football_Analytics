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
    pass

admin.site.register(Partido, PartidoAdmin)
