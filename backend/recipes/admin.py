from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


# Убираем стандартную модель
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомизация админ-панели для пользователей."""
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_image_preview'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    # Добавляем 'avatar', чтобы его можно было редактировать
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name',
                                                'email', 'avatar')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('get_image_preview', 'last_login', 'date_joined')

    @admin.display(description='Аватар')
    def get_image_preview(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" width="100" />')
        return 'Нет аватара'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Кастомизация админ-панели для ингредиентов."""
    list_display = ('name', 'measurement_unit', 'get_recipe_count')
    search_fields = ('name',)

    @admin.display(description='В рецептах')
    def get_recipe_count(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Кастомизация админ-панели для тегов."""
    # Убираем 'color' из списка.
    list_display = ('name', 'slug', 'get_recipe_count')
    search_fields = ('name', 'slug')

    @admin.display(description='В рецептах')
    def get_recipe_count(self, tag):
        return tag.recipes.count()


class RecipeIngredientInline(admin.TabularInline):
    """Вспомогательный класс для отображения ингредиентов в рецепте."""
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация админ-панели для рецептов."""
    list_display = (
        'name', 'author', 'get_cooking_time_display', 'get_favorites_count',
        'get_image_preview'
    )
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('get_favorites_count', 'get_image_preview',)

    @admin.display(description='Время (мин)')
    def get_cooking_time_display(self, recipe):
        return recipe.cooking_time

    @admin.display(description='В избранном')
    def get_favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Превью')
    def get_image_preview(self, recipe):
        if recipe.image:
            return mark_safe(f'<img src="{recipe.image.url}" width="100" />')
        return 'Нет изображения'


# Регистрируем остальные модели для управления
admin.site.register(Favorite)
admin.site.register(Follow)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredient)
