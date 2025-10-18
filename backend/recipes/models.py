from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import (MAX_LENGTH_INGREDIENT_NAME, MAX_LENGTH_INGREDIENT_UNIT,
                        MAX_LENGTH_RECIPE_NAME, MAX_LENGTH_TAG_NAME,
                        MAX_LENGTH_TAG_SLUG, MIN_COOKING_TIME,
                        MIN_INGREDIENT_AMOUNT)


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(
        'Адрес электронной почты', unique=True, max_length=254
    )
    username = models.CharField(
        'Юзернейм',
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель для подписок пользователей друг на друга."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        'Название', max_length=MAX_LENGTH_TAG_NAME, unique=True
    )
    color = models.CharField('Цвет в HEX', max_length=7, unique=True)
    slug = models.SlugField(
        'Уникальный слаг', max_length=MAX_LENGTH_TAG_SLUG, unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента (продукта)."""
    name = models.CharField(
        'Название', max_length=MAX_LENGTH_INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_LENGTH_INGREDIENT_UNIT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Название', max_length=MAX_LENGTH_RECIPE_NAME)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Время должно быть не меньше {MIN_COOKING_TIME}'
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи Recipe и Ingredient."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент',
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=(
                    f'Количество должно быть не меньше {MIN_INGREDIENT_AMOUNT}'
                )
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} в "{self.recipe.name}"'


class UserRecipeList(models.Model):
    """Абстрактная модель для списков пользователь-рецепт."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}"'


class Favorite(UserRecipeList):
    """Модель для избранных рецептов."""
    class Meta(UserRecipeList.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeList):
    """Модель для списка покупок."""
    class Meta(UserRecipeList.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
