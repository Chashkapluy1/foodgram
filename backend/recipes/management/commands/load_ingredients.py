from recipes.models import Ingredient

from .base_loader import BaseLoader


class Command(BaseLoader):
    """Загрузка ингредиентов из JSON файла."""
    model = Ingredient
    file_path = 'data/ingredients.json'
    help = 'Загрузка ингредиентов из data/ingredients.json'
