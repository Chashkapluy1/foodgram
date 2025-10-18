from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django import forms

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


class ImagePreviewWidget(forms.FileInput):
    """Кастомный виджет для отображения превью изображения."""
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        if value and hasattr(value, 'url'):
            preview_html = format_html(
                '<div><p style="margin-top: 10px;">'
                '<strong>Текущее изображение:</strong></p>'
                '<img src="{}" style="max-height: 150px; '
                'border-radius: 5px;" />'
                '</div>',
                value.url
            )
            return format_html('{}<p style="margin-top: 10px;">'
                               '<strong>Изменить:</strong></p>{}',
                               preview_html, html)
        return html


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомизация админ-панели для пользователей."""
    list_display = (
        'id', 'username', 'get_full_name', 'email', 'get_image_preview',
        'get_recipe_count', 'get_followers_count', 'get_following_count'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name',
                                                'email', 'avatar')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['avatar'].widget = ImagePreviewWidget()
        return form

    @admin.display(description='ФИО')
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()

    @admin.display(description='Аватар')
    def get_image_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width: 50px; '
                'border-radius: 50%;" />',
                obj.avatar.url
            )
        return "Нет аватара"

    @admin.display(description='Рецептов')
    def get_recipe_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Подписчиков')
    def get_followers_count(self, obj):
        return obj.following.count()

    @admin.display(description='Подписок')
    def get_following_count(self, obj):
        return obj.followers.count()


class RecipeIngredientInline(admin.TabularInline):
    """Вспомогательный класс для отображения ингредиентов в рецепте."""
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация админ-панели для рецептов."""
    list_display = (
        'id', 'name', 'author', 'get_tags_display', 'get_ingredients_display',
        'get_favorites_count', 'get_image_preview'
    )
    list_filter = ('author', 'tags', 'name')
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('get_favorites_count',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['image'].widget = ImagePreviewWidget()
        return form

    @admin.display(description='Теги')
    def get_tags_display(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients_display(self, obj):
        ingredients = obj.recipe_ingredients.select_related('ingredient')
        display_text = [
            f'{item.ingredient.name} '
            f'({item.amount} {item.ingredient.measurement_unit})'
            for item in ingredients[:3]
        ]
        if ingredients.count() > 3:
            display_text.append('...')
        return format_html("<br>".join(display_text))

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Превью')
    def get_image_preview(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="75"/>')
        return "Нет картинки"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Кастомизация админ-панели для ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


admin.site.register(Tag)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user__username", "author__username")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")


admin.site.unregister(Group)
