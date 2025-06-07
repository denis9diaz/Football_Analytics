from django.urls import path
from .views import SuscripcionView, ContratarSuscripcionView, CancelarSuscripcionView, ReactivarSuscripcionView

urlpatterns = [
    path('', SuscripcionView.as_view(), name='suscripcion-estado'),
    path('contratar/', ContratarSuscripcionView.as_view(), name='suscripcion-contratar'),
    path('cancelar/', CancelarSuscripcionView.as_view(), name='suscripcion-cancelar'),
    path('reactivar/', ReactivarSuscripcionView.as_view(), name='suscripcion-reactivar'),
]
