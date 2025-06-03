from django.db import models
from django.contrib.auth.models import User

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

    gol_ht = models.BooleanField(null=True, blank=True)
    codigo_api = models.CharField(max_length=30, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Actualizar campos derivados
        if self.goles_local_ht is not None and self.goles_visitante_ht is not None:
            self.gol_ht = (self.goles_local_ht + self.goles_visitante_ht) > 0

        if self.goles_local_ft is not None:
            self.marco_local = self.goles_local_ft > 0

        if self.goles_visitante_ft is not None:
            self.marco_visitante = self.goles_visitante_ft > 0

        super().save(*args, **kwargs)

        # Actualizar rachas
        from analisis.utils.actualizar_rachas import actualizar_rachas
        actualizar_rachas()

        # =====================
        # GOL HT
        # =====================
        if self.gol_ht is not None:
            for equipo, contexto in [
                (self.equipo_local, 'local'),
                (self.equipo_local, 'ambos'),
                (self.equipo_visitante, 'visitante'),
                (self.equipo_visitante, 'ambos')
            ]:
                self._actualizar_racha_equipo(equipo, contexto, self.gol_ht, 'gol_ht')

        # =====================
        # TTS
        # =====================
        if self.goles_local_ft is not None and self.goles_visitante_ft is not None:
            for equipo, goles, contextos in [
                (self.equipo_local, self.goles_local_ft, ['local', 'ambos']),
                (self.equipo_visitante, self.goles_visitante_ft, ['visitante', 'ambos'])
            ]:
                for contexto in contextos:
                    self._actualizar_racha_equipo(equipo, contexto, goles > 0, 'tts')

        # =====================
        # BTTS
        # =====================
        if self.btts is not None:
            for equipo, contextos in [
                (self.equipo_local, ['local', 'ambos']),
                (self.equipo_visitante, ['visitante', 'ambos'])
            ]:
                for contexto in contextos:
                    self._actualizar_racha_equipo(equipo, contexto, self.btts, 'btts')

        # =====================
        # HOME TO WIN
        # =====================
        if self.goles_local_ft is not None and self.goles_visitante_ft is not None:
            gano_local = self.goles_local_ft > self.goles_visitante_ft
            for equipo, cumplido, contextos in [
                (self.equipo_local, gano_local, ['local', 'ambos']),
                (self.equipo_visitante, not gano_local, ['visitante', 'ambos'])
            ]:
                for contexto in contextos:
                    self._actualizar_racha_equipo(equipo, contexto, cumplido, 'ganar')

        # =====================
        # OVER 1.5 HOME
        # =====================
        if self.goles_local_ft is not None:
            cumple_local = self.goles_local_ft >= 2
            for contexto in ['local', 'ambos']:
                self._actualizar_racha_equipo(self.equipo_local, contexto, cumple_local, 'over_1_5_marcados')

            cumple_visitante = self.goles_local_ft >= 2
            for contexto in ['visitante', 'ambos']:
                self._actualizar_racha_equipo(self.equipo_visitante, contexto, cumple_visitante, 'over_1_5_recibidos')

        # =====================
        # OVER 1.5 y OVER 2.5
        # =====================
        for condicion in [('over_1_5', self.over_1_5), ('over_2_5', self.over_2_5)]:
            if condicion[1] is not None:
                for equipo, contexto in [
                    (self.equipo_local, 'ambos'),
                    (self.equipo_visitante, 'ambos')
                ]:
                    self._actualizar_racha_equipo(equipo, contexto, condicion[1], condicion[0])

    def _actualizar_racha_equipo(self, equipo, contexto, cumplido, condicion):
        if equipo is None:
            return

        # Obtener todos los partidos del equipo en orden cronológico
        partidos = Partido.objects.filter(
            models.Q(equipo_local=equipo) | models.Q(equipo_visitante=equipo)
        ).order_by('fecha')

        racha_actual, _ = RachaEquipo.objects.get_or_create(
            equipo=equipo,
            condicion=condicion,
            contexto=contexto,
            tipo='actual',
            defaults={'cantidad': 0}
        )

        racha_historica, _ = RachaEquipo.objects.get_or_create(
            equipo=equipo,
            condicion=condicion,
            contexto=contexto,
            tipo='historica',
            defaults={'cantidad': 0}
        )

        # Recalcular la racha actual en orden cronológico
        cantidad_actual = 0
        for partido in partidos:
            if partido.fecha <= self.fecha:  # Solo considerar partidos anteriores o el actual
                if cumplido:
                    cantidad_actual = 0
                else:
                    cantidad_actual += 1

        racha_actual.cantidad = cantidad_actual
        racha_actual.save()

        # Actualizar la racha histórica si la actual es más larga
        if racha_actual.cantidad > racha_historica.cantidad:
            racha_historica.cantidad = racha_actual.cantidad
            racha_historica.save()


# ========================
# 3. MÉTODOS FIJOS
# ========================

class MetodoAnalisis(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


# ========================
# 4. PARTIDOS ANALIZADOS
# ========================

class PartidoAnalisis(models.Model):
    metodo = models.ForeignKey(MetodoAnalisis, on_delete=models.CASCADE, related_name='partidos')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    cuota_estim_real = models.DecimalField(max_digits=5, decimal_places=2)
    cuota_casa_apuestas = models.DecimalField(max_digits=5, decimal_places=2)
    valor_estimado = models.DecimalField(max_digits=7, decimal_places=2)
    porcentaje_acierto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    favorito = models.BooleanField(default=False)

    equipo_destacado = models.CharField(
        max_length=10,
        choices=[('local', 'Local'), ('visitante', 'Visitante')],
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.metodo.nombre} - {self.partido}"


# ========================
# 5. RACHAS POR EQUIPO
# ========================

class RachaEquipo(models.Model):
    CONDICIONES = [
        ('gol_ht', 'Gol HT'),
        ('tts', 'Marcar Gol'),
        ('btts', 'Ambos Marcan'),
        ('over_1_5', 'Over 1.5'),
        ('over_2_5', 'Over 2.5'),
        ('over_1_5_marcados', 'Over 1.5 Marcados'),
        ('over_1_5_recibidos', 'Over 1.5 Recibidos'),
        ('ganar', 'Ganar'),
    ]

    CONTEXTOS = [
        ('local', 'Jugando de local'),
        ('visitante', 'Jugando de visitante'),
        ('ambos', 'Combinado')
    ]

    TIPO = [
        ('actual', 'Actual'),
        ('historica', 'Histórica')
    ]

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='rachas')
    condicion = models.CharField(max_length=30, choices=CONDICIONES)
    contexto = models.CharField(max_length=10, choices=CONTEXTOS)
    tipo = models.CharField(max_length=20, choices=TIPO)
    cantidad = models.PositiveIntegerField()
    temporada = models.CharField(max_length=9, null=True, blank=True)

    class Meta:
        unique_together = ('equipo', 'condicion', 'contexto', 'tipo', 'temporada')

    def __str__(self):
        return f"{self.equipo} - {self.condicion} ({self.tipo})"


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    partido_analisis = models.ForeignKey(PartidoAnalisis, on_delete=models.CASCADE, related_name="favoritos")
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'partido_analisis')

    def __str__(self):
        return f"{self.usuario.username} - {self.partido_analisis}"
