from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'username')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorites_count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Число добавлений в избранное')
    def get_favorites_count(self, obj):
        return obj.in_favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
