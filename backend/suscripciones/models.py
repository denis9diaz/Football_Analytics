from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

class Suscripcion(models.Model):
    PLANES = [
        ('prueba', 'Prueba gratuita'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="suscripcion")
    plan = models.CharField(max_length=20, choices=PLANES)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField()
    cancelada = models.BooleanField(default=False)

    def esta_activa(self):
        return not self.cancelada and self.fecha_fin >= now().date()

    def contratar_o_renovar(self, nuevo_plan: str):
        """Contrata o renueva sumando tiempo al plan actual o anterior."""

        # Usar la fecha actual si la suscripción ya expiró
        hoy = now().date()
        fecha_base = self.fecha_fin if self.fecha_fin >= hoy else hoy

        # Determinar cuánto tiempo sumar
        if nuevo_plan == 'prueba':
            nueva_fecha_fin = fecha_base + relativedelta(days=3)
        elif nuevo_plan == 'mensual':
            nueva_fecha_fin = fecha_base + relativedelta(months=1)
        elif nuevo_plan == 'trimestral':
            nueva_fecha_fin = fecha_base + relativedelta(months=3)
        elif nuevo_plan == 'anual':
            nueva_fecha_fin = fecha_base + relativedelta(years=1)
        else:
            raise ValueError("Plan no válido")

        self.plan = nuevo_plan
        self.fecha_fin = nueva_fecha_fin
        self.cancelada = False
        self.save()

    def cancelar(self):
        """Cancela la suscripción sin eliminarla, manteniendo fecha_fin."""
        self.cancelada = True
        self.save()

    def reactivar(self):
        """Reactiva una suscripción cancelada (si aún no ha expirado)."""
        if self.fecha_fin >= now().date():
            self.cancelada = False
            self.save()
        else:
            raise ValueError("La suscripción ya ha expirado. No se puede reactivar.")

    def __str__(self):
        estado = "Activa" if self.esta_activa() else "Inactiva"
        return f"{self.usuario.username} - {self.plan} - {estado}"
