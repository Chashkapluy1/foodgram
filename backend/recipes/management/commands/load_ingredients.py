import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка ингредиентов из CSV файла."""
    help = 'Загрузка ингредиентов из data/ingredients.csv'

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.csv'
        self.stdout.write(
            self.style.SUCCESS(f'Начинаю загрузку из {file_path}')
        )
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                ingredients_to_create = [
                    Ingredient(
                        name=row['name'],
                        measurement_unit=row['measurement_unit']
                    ) for row in reader
                ]
                Ingredient.objects.bulk_create(
                    ingredients_to_create,
                    ignore_conflicts=True
                )
            self.stdout.write(
                self.style.SUCCESS('Ингредиенты успешно загружены.')
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке: {e}')
            )
