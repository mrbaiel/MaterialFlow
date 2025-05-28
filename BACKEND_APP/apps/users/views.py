from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.serializers import TelegramVerifySerializer


class TelegramVerifyView(APIView):
        permission_classes = [IsAuthenticated]

        def post(self, request):
            serializer = TelegramVerifySerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({'status': 'success',
                             'user_id': user.id
                             })
