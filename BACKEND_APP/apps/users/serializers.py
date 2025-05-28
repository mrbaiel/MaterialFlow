from rest_framework import serializers

from apps.users.models import User


class TelegramVerifySerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    telegram_id = serializers.CharField(max_length=50)

    def validate(self, data):
        username = data.get("username")
        telegram_id = data.get("telegram_id")
        roles = ['owner', 'developer']
        try:
            user = User.objects.get(username=username)
            is_exists = User.objects.filter(telegram_id=telegram_id).exclude(username=username).exists()
            if user.role not in roles:
                raise serializers.ValidationError("У вас нет прав")
            if is_exists:
                raise serializers.ValidationError("Телеграм id уже связан")
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        return data

    def save(self):
        user = User.objects.get(username=self.validated_data["username"])
        user.telegram_id = self.validated_data['telegram_id']
        user.save()
        return user