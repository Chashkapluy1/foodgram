import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.constants import MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT
from recipes.models import (Follow, Ingredient, Recipe,
                            RecipeIngredient, Tag, User)


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для изображений в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f"temp.{ext}")
        return super().to_internal_value(data)


class UserReadSerializer(DjoserUserSerializer):
    """Сериализатор для пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "avatar"
        )

    def get_is_subscribed(self, author):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and user != author
            and Follow.objects.filter(user=user, author=author).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source="recipe_ingredients", many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, recipe):
        request = self.context.get("request")
        return (request and request.user.is_authenticated
                and recipe.favorites.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")
        return (request and request.user.is_authenticated
                and recipe.shopping_carts.filter(user=request.user).exists())


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

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
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = (
            "ingredients", "tags", "image", "name", "text", "cooking_time"
        )

    def _add_ingredients_and_tags(self, recipe, ingredients, tags):
        if tags is not None:
            recipe.tags.set(tags)
        if ingredients is not None:
            recipe.recipe_ingredients.all().delete()
            RecipeIngredient.objects.bulk_create(
                (RecipeIngredient(
                    recipe=recipe,
                    ingredient=item["id"],
                    amount=item["amount"]
                ) for item in ingredients)
            )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        self._add_ingredients_and_tags(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        super().update(instance, validated_data)
        self._add_ingredients_and_tags(instance, ingredients, tags)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для рецептов."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class AuthorSubscriptionSerializer(UserReadSerializer):
    """Сериализатор для отображения авторов в подписках с рецептами."""
    recipes_count = serializers.ReadOnlyField(source="recipes.count")
    recipes = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = (*UserReadSerializer.Meta.fields, "recipes_count", "recipes")

    def get_recipes(self, author):
        recipes_limit_str = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes = author.recipes.all()
        if recipes_limit_str and recipes_limit_str.isdigit():
            recipes = recipes[:int(recipes_limit_str)]
        return RecipeShortSerializer(recipes, many=True).data
