import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Загрузка ингредиентов из JSON файла в базу данных.
    Использует bulk_create с ignore_conflicts.
    """
    help = 'Загрузка ингредиентов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.json'
        self.stdout.write(
            self.style.SUCCESS(f'Начинаю загрузку из {file_path}')
        )

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ingredients_data = json.load(file)

            ingredients_to_create = [
                Ingredient(**item) for item in ingredients_data
            ]

            Ingredient.objects.bulk_create(
                ingredients_to_create,
                ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                'Загрузка ингредиентов завершена.'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл {file_path} не найден.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Произошла ошибка при загрузке {file_path}: {e}'
            ))
