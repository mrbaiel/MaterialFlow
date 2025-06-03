from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.users.models import User
from telegram_bot.middleware import ALLOWED_ROLES


class TelegramVerifyView(APIView):
    permission_classes = [AllowAny]

    ALLOWED_ROLES = ["owner", "admin", "developer"]

    def post(self, request):
        telegram_id = request.data.get('telegram_id')

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"Ошибка": "Отказано в доступе"}, status=403)

        if user.role not in ALLOWED_ROLES:
            return Response({"Ошибка": "Нету доступа"})

        return Response({'status': 'success',
                         'user_id': user.id,
                         'role': user.role,
                         })
