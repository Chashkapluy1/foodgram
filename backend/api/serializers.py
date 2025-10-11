from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.constants import MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT
from recipes.fields import Base64ImageField
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag, User)


class UserReadSerializer(DjoserUserSerializer):
    """Сериализатор для просмотра профиля пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )
        read_only_fields = fields

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user != author
            and Follow.objects.filter(user=user, author=author).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = fields

    def _is_in_list(self, model, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and model.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        return self._is_in_list(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self._is_in_list(ShoppingCart, obj)


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        error_messages={
            'min_value': (
                f'Количество должно быть не меньше {MIN_INGREDIENT_AMOUNT}.'
            )
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        error_messages={
            'min_value': (
                'Время приготовления должно быть не меньше '
                f'{MIN_COOKING_TIME}.'
            )
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def _add_ingredients_and_tags(self, recipe, ingredients, tags):
        """Вспомогательный метод для добавления тегов и ингредиентов."""
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self._add_ingredients_and_tags(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.recipe_ingredients.all().delete()
        self._add_ingredients_and_tags(instance, ingredients, tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для рецептов (например, в подписках)."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class FollowSerializer(UserReadSerializer):
    """Сериализатор для отображения авторов в подписках."""
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = fields

    def get_recipes(self, author):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        recipes = author.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (TypeError, ValueError):
                pass
        return RecipeShortSerializer(recipes, many=True).data
