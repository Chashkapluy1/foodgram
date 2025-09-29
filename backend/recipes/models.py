from django.db import models
from django.conf import settings

# Получаем нашу кастомную модель User
User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    """
    Модель тега.
    """
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет в HEX', max_length=7, unique=True)
    slug = models.SlugField('Уникальный слаг', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиента.
    """
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецепта.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    cooking_time = models.PositiveSmallIntegerField('Время приготовления (в минутах)')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)  # Сортировка по умолчанию, новые рецепты - сверху

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи Recipe и Ingredient.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_ingredient_in_recipe')
        ]

    def __str__(self):
        return f'{self.ingredient.name} в "{self.recipe.name}"'


class Favorite(models.Model):
    """
    Модель для избранных рецептов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite_recipe')
        ]


class ShoppingCart(models.Model):
    """
    Модель для списка покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_recipe_in_cart')
        ]
