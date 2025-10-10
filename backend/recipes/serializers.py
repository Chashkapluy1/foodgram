from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .fields import Base64ImageField
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, recipe):
        """Получаем ингредиенты для рецепта из предзагруженных данных."""
        return [
            {
                "id": item.ingredient.id,
                "name": item.ingredient.name,
                "measurement_unit": item.ingredient.measurement_unit,
                "amount": item.amount,
            }
            for item in recipe.recipeingredient_set.all()
        ]

    def _is_in_list(self, recipe, model):
        """Вспомогательный метод для проверки наличия рецепта в списке."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return model.objects.filter(user=user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        """Проверяем, добавлен ли рецепт в избранное."""
        return self._is_in_list(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        """Проверяем, добавлен ли рецепт в список покупок."""
        return self._is_in_list(recipe, ShoppingCart)


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для данных об ингредиенте при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data["id"],
                amount=ingredient_data["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", None)
        if tags_data is not None:
            instance.tags.set(tags_data)
        ingredients_data = validated_data.pop("ingredients", None)
        if ingredients_data is not None:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
