from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
from .utils import account_activation_token
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail, EmailMultiAlternatives
import random
import string
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generar token y enlace
        token = account_activation_token.make_token(user)
        uid = user.pk
        activation_link = f"{settings.FRONTEND_URL}/verificar?uid={uid}&token={token}"

        subject = 'Activa tu cuenta'
        message = f"Hola {user.username},\n\nHaz clic en el siguiente enlace para activar tu cuenta:\n{activation_link}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print("❌ Error al enviar el correo:", e)

        return Response(
            {"detail": "Usuario creado. Revisa tu correo para activar la cuenta."},
            status=status.HTTP_201_CREATED
        )


class ActivateUserView(APIView):
    def get(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return Response({'error': 'Parámetros inválidos'}, status=400)

        user = get_object_or_404(User, pk=uid)

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            # Enviar correo de bienvenida
            send_mail(
                subject="¡Bienvenido!",
                message=f"Hola {user.username}, tu cuenta ha sido activada correctamente.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response({'detail': 'Cuenta activada'}, status=200)
        else:
            return Response({'error': 'Token inválido o expirado'}, status=400)


class ValidateTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'valid': True})


class SendTempPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'No existe ningún usuario con ese email'}, status=status.HTTP_404_NOT_FOUND)

        # Generar contraseña temporal
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        user.set_password(temp_password)
        user.save()

        # Enlace a la página de cambio
        enlace_cambio = f"{settings.FRONTEND_URL}/cambiar-temporal"

        # Contenido del correo
        subject = "Recuperación de contraseña"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]

        text_content = (
            f"Hola {user.username},\n\n"
            f"Tu nueva contraseña temporal es: {temp_password}\n\n"
            f"Debes cambiarla cuanto antes. Hazlo aquí: {enlace_cambio}"
        )

        html_content = f"""
            <p>Hola <strong>{user.username}</strong>,</p>
            <p>Tu nueva contraseña temporal es:</p>
            <p style="font-size: 18px; font-weight: bold;">{temp_password}</p>
            <p>Por seguridad, debes cambiarla cuanto antes.</p>
            <p>
                Haz clic en el siguiente enlace para establecer una nueva contraseña:<br>
                <a href="{enlace_cambio}" style="color: #1d4ed8;">{enlace_cambio}</a>
            </p>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return Response({'detail': 'Contraseña temporal enviada'}, status=200)


class ForceChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_password = request.data.get('temp_password')
        new_password = request.data.get('new_password')

        if not temp_password or not new_password:
            return Response({'detail': 'Todos los campos son obligatorios'}, status=400)

        # Buscar un usuario con esa contraseña (temporal)
        for user in User.objects.filter(is_active=True):
            if user.has_usable_password() and check_password(temp_password, user.password):
                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Contraseña actualizada correctamente'}, status=200)

        return Response({'detail': 'Contraseña temporal incorrecta'}, status=400)

