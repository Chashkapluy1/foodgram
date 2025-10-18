from recipes.models import Tag

from .base_loader import BaseLoader


class Command(BaseLoader):
    """Загрузка тегов из JSON файла."""
    model = Tag
    file_path = 'data/tags.json'
    help = 'Загрузка тегов из data/tags.json'
