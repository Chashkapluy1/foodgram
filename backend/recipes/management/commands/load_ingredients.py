import csv

from recipes.models import Ingredient

from .base_loader import BaseLoader


class Command(BaseLoader):
    """Загрузка ингредиентов из CSV файла."""
    model = Ingredient
    file_path = 'data/ingredients.csv'
    help = f'Загрузка ингредиентов из {file_path}'

    def load_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            items = (
                self.model(name=row[0], measurement_unit=row[1])
                for row in reader if row
            )
            return self.model.objects.bulk_create(items)
