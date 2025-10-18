from datetime import datetime
from django.db.models import Sum
from django.template.loader import render_to_string

from .models import Recipe, RecipeIngredient

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая",
    6: "июня", 7: "июля", 8: "августа", 9: "сентября", 10: "октября",
    11: "ноября", 12: "декабря"
}


def format_shopping_list(user):
    """Форматирует список покупок для пользователя."""
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_carts__user=user
    ).values(
        "ingredient__name", "ingredient__measurement_unit"
    ).annotate(total_amount=Sum("amount")).order_by("ingredient__name")

    recipes = Recipe.objects.filter(shopping_carts__user=user)

    now = datetime.now()
    context = {
        "date": f"{now.day} {MONTHS_RU[now.month]} {now.year}",
        "ingredients": ingredients,
        "recipes": recipes,
    }
    return render_to_string("shopping_list.txt", context)
