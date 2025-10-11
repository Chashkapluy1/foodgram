from django.shortcuts import get_object_or_404, redirect
from .models import Recipe


def recipe_short_link_redirect(request, recipe_id):
    """Редиректит с короткой ссылки /r/<id>/ на полную страницу рецепта."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect(f'/recipes/{recipe.id}/')
