from django.db import models

# ========================
# 1. LIGAS Y EQUIPOS
# ========================

class Liga(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_pais = models.CharField(max_length=6)
    codigo_api = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name='equipos')
    codigo_api = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nombre


# ========================
# 2. PARTIDOS REALES
# ========================

class Partido(models.Model):
    liga = models.ForeignKey(Liga, on_delete=models.SET_NULL, null=True)
    equipo_local = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, related_name='partidos_local')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, related_name='partidos_visitante')

    fecha = models.DateTimeField()

    goles_local_ht = models.PositiveSmallIntegerField(null=True, blank=True)
    goles_visitante_ht = models.PositiveSmallIntegerField(null=True, blank=True)
    goles_local_ft = models.PositiveSmallIntegerField(null=True, blank=True)
    goles_visitante_ft = models.PositiveSmallIntegerField(null=True, blank=True)

    resultado_1x2 = models.CharField(
        max_length=2,
        choices=[('1', 'Local'), ('X', 'Empate'), ('2', 'Visitante')],
        null=True, blank=True
    )

    over_1_5 = models.BooleanField(null=True)
    over_2_5 = models.BooleanField(null=True)
    btts = models.BooleanField(null=True)
    marco_local = models.BooleanField(null=True)
    marco_visitante = models.BooleanField(null=True)
    over_1_5_local = models.BooleanField(null=True)

    codigo_api = models.CharField(max_length=30, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} ({self.fecha.date()})"


# ========================
# 3. MÉTODOS FIJOS
# ========================

class MetodoAnalisis(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


# ========================
# 4. PARTIDOS ANALIZADOS (derivan de partidos reales)
# ========================

class PartidoAnalisis(models.Model):
    metodo = models.ForeignKey(MetodoAnalisis, on_delete=models.CASCADE, related_name='partidos')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)

    cuota_estim_real = models.DecimalField(max_digits=5, decimal_places=2)
    cuota_casa_apuestas = models.DecimalField(max_digits=5, decimal_places=2)
    valor_estimado = models.DecimalField(max_digits=7, decimal_places=2)

    porcentaje_acierto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # nuevo campo

    favorito = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.metodo.nombre} - {self.partido}"


# ========================
# 5. RACHAS POR EQUIPO
# ========================

class RachaEquipo(models.Model):
    CONDICIONES = [
        ('gol_ht', 'Gol HT'),
        ('tts', 'Marcar Gol'),
        ('over_1_5', 'Over 1.5'),
        ('over_2_5', 'Over 2.5'),
        ('over_1_5_local', 'Over 1.5 Local'),
        ('ganar', 'Ganar'),
    ]

    CONTEXTOS = [
        ('local', 'Jugando de local'),
        ('visitante', 'Jugando de visitante'),
        ('ambos', 'Combinado'),
    ]

    TIPO = [
        ('actual', 'Actual'),
        ('historica', 'Histórica'),
    ]

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='rachas')
    condicion = models.CharField(max_length=20, choices=CONDICIONES)
    contexto = models.CharField(max_length=10, choices=CONTEXTOS)
    tipo = models.CharField(max_length=20, choices=TIPO)
    cantidad = models.PositiveIntegerField()

    temporada = models.CharField(max_length=9, null=True, blank=True)  # solo se usa si tipo == actual

    class Meta:
        unique_together = ('equipo', 'condicion', 'contexto', 'tipo', 'temporada')

    def __str__(self):
        return f"{self.equipo} - {self.condicion} ({self.tipo})"
