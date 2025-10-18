from django.http import Http404
from django.shortcuts import redirect

from .models import Recipe


def recipe_short_link_redirect(request, recipe_id):
    """Редиректит с короткой ссылки на полную страницу рецепта."""
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise Http404(f'Рецепт с id={recipe_id} не найден.')
    return redirect(f'/recipes/{recipe_id}/')
