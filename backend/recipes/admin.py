from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


class HasRecipesFilter(admin.SimpleListFilter):
    title = 'Наличие рецептов'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (('yes', 'Есть рецепты'), ('no', 'Нет рецептов'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(
                num_recipes=Count('recipes')
            ).filter(num_recipes__gt=0)
        if self.value() == 'no':
            return queryset.annotate(
                num_recipes=Count('recipes')
            ).filter(num_recipes=0)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомная админка для пользователей."""
    list_display = (
        'id', 'username', 'email', 'get_full_name', 'get_recipes_count',
        'get_followers_count', 'get_following_count'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active', HasRecipesFilter)
    empty_value_display = '-пусто-'

    @admin.display(description='Кол-во рецептов')
    def get_recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def get_followers_count(self, user):
        return user.following.count()

    @admin.display(description='Кол-во подписок')
    def get_following_count(self, user):
        return user.followers.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'get_favorites_count',
        'get_image_preview'
    )
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('get_favorites_count', 'get_image_preview',)

    @admin.display(description='В избранном')
    def get_favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Превью')
    def get_image_preview(self, recipe):
        if recipe.image:
            return mark_safe(f'<img src="{recipe.image.url}" width="100" />')
        return 'Нет изображения'

    get_favorites_count.short_description = 'В избранном (раз)'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite, ShoppingCart)
class UserRecipeListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
