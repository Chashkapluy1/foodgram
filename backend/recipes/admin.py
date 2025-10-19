from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django import forms

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


class ImagePreviewWidget(forms.FileInput):
    """Кастомный виджет для отображения превью изображения."""
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        if value and hasattr(value, 'url'):
            preview_html = (
                '<div><p style="margin-top: 10px;">'
                '<strong>Текущее изображение:</strong></p>'
                '<img src="{}" style="max-height: 150px; '
                'border-radius: 5px;" /></div>'
            ).format(value.url)
            return mark_safe(
                '{}<p style="margin-top: 10px;"><strong>'
                'Изменить:</strong></p>{}'.format(preview_html, html)
            )
        return html


class RecipeCountAdminMixin:
    @admin.display(description="В рецептах")
    def get_recipe_count(self, obj):
        return obj.recipes.count()


@admin.register(User)
class UserAdmin(BaseUserAdmin, RecipeCountAdminMixin):
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
    def get_full_name(self, user):
        return f'{user.first_name} {user.last_name}'.strip()

    @admin.display(description='Аватар')
    def get_image_preview(self, user):
        if user.avatar:
            return mark_safe(
                '<img src="{}" style="max-width: 50px; '
                'border-radius: 50%;" />'.format(user.avatar.url)
            )
        return ""

    @admin.display(description='Подписчиков')
    def get_followers_count(self, user):
        return user.following.count()

    @admin.display(description='Подписок')
    def get_following_count(self, user):
        return user.followers.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin, RecipeCountAdminMixin):
    list_display = ('id', 'name', 'measurement_unit', 'get_recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin, RecipeCountAdminMixin):
    list_display = ('id', 'name', 'slug', 'get_recipe_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'get_tags_display', 'get_ingredients_display',
        'get_favorites_count', 'get_image_preview'
    )
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('get_favorites_count',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['image'].widget = ImagePreviewWidget()
        return form

    @admin.display(description='Теги')
    def get_tags_display(self, recipe):
        return ", ".join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Ингредиенты')
    def get_ingredients_display(self, recipe):
        return mark_safe("<br>".join(
            f'{item.ingredient.name} '
            f'({item.amount} {item.ingredient.measurement_unit})'
            for item in recipe.recipe_ingredients.select_related('ingredient')
        ))

    @admin.display(description='В избранном')
    def get_favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Превью')
    def get_image_preview(self, recipe):
        if recipe.image:
            return mark_safe(f'<img src="{recipe.image.url}" width="75"/>')
        return ""


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
