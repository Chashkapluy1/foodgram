from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers

from .models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, author):
        user = self.context.get("request").user
        if user.is_anonymous or user == author:
            return False
        return Follow.objects.filter(user=user, author=author).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes_count",
            "recipes",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        recipes_limit = self.context.get("request").query_params.get(
            "recipes_limit"
        )
        queryset = author.recipes.all()
        if recipes_limit:
            try:
                queryset = queryset[: int(recipes_limit)]
            except (TypeError, ValueError):
                pass
        return RecipeShortSerializer(queryset, many=True).data
