from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор для создания пользователя (регистрации).
    """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    """
    Кастомный сериализатор для просмотра профиля пользователя.
    Добавляет поле is_subscribed.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        """
        Проверяет, подписан ли текущий пользователь на данного автора.
        """
        user = self.context.get('request').user
        if user.is_anonymous or user == author:
            return False
        return Follow.objects.filter(user=user, author=author).exists()
