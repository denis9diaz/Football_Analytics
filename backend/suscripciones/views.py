from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Suscripcion
from .serializers import SuscripcionSerializer, ContratarSuscripcionSerializer
from django.utils.timezone import localdate, now
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


class SuscripcionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suscripcion = getattr(request.user, 'suscripcion', None)
        if suscripcion:
            serializer = SuscripcionSerializer(suscripcion)
            return Response(serializer.data)
        return Response({"detail": "El usuario no tiene suscripción."}, status=404)


class ContratarSuscripcionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContratarSuscripcionSerializer(data=request.data)
        if serializer.is_valid():
            plan = serializer.validated_data['plan']
            user = request.user
            hoy = localdate()

            suscripcion, creada = Suscripcion.objects.get_or_create(usuario=user, defaults={
                "plan": plan,
                "fecha_fin": hoy,  # se actualizará enseguida
            })

            suscripcion.contratar_o_renovar(plan)

            enviar_email_suscripcion(user, "contratada")

            return Response(SuscripcionSerializer(suscripcion).data)

        return Response(serializer.errors, status=400)


class CancelarSuscripcionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        suscripcion = getattr(request.user, 'suscripcion', None)
        if not suscripcion:
            return Response({"detail": "No tienes suscripción activa."}, status=400)

        suscripcion.cancelar()

        enviar_email_suscripcion(request.user, "cancelada")

        return Response({"detail": "Suscripción cancelada correctamente."})


class ReactivarSuscripcionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        suscripcion = getattr(request.user, 'suscripcion', None)
        if not suscripcion:
            return Response({"detail": "No tienes suscripción."}, status=400)

        try:
            suscripcion.reactivar()
            enviar_email_suscripcion(request.user, "reactivada")
            return Response({"detail": "Suscripción reactivada correctamente."})
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)


class SuscripcionEstadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suscripcion = getattr(request.user, 'suscripcion', None)
        if suscripcion and suscripcion.esta_activa:
            return Response({
                "activa": True,
                "tipo": suscripcion.plan,
                "fecha_fin": suscripcion.fecha_fin.strftime("%Y-%m-%d"),
            })
        return Response({"activa": False})


def enviar_email_suscripcion(usuario, tipo):
    subject_map = {
        "contratada": "¡Suscripción activada!",
        "cancelada": "Suscripción cancelada",
        "reactivada": "Suscripción reactivada",
    }

    template_map = {
        "contratada": "email/suscripcion_contratada.html",
        "cancelada": "email/suscripcion_cancelada.html",
        "reactivada": "email/suscripcion_reactivada.html",
    }

    subject = subject_map.get(tipo)
    template = template_map.get(tipo)

    if not subject or not template:
        return  # tipo inválido

    from_email = settings.DEFAULT_FROM_EMAIL
    to = [usuario.email]

    html_content = render_to_string(template, {
        "username": usuario.username,
        "subject": subject,
        "year": now().year,
        "fecha_fin": usuario.suscripcion.fecha_fin.strftime("%d/%m/%Y") if hasattr(usuario, 'suscripcion') else '',
    })

    text_content = f"Hola {usuario.username}, tu suscripción ha sido {tipo}."

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
