import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON файла в базу данных'

    def handle(self, *args, **kwargs):
        file_path = '../data/ingredients.json'  # Путь к файлу относительно manage.py
        self.stdout.write(self.style.SUCCESS(f'Начинаю загрузку из {file_path}'))

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ingredients_data = json.load(file)

            ingredients_to_create = []
            for item in ingredients_data:
                # Проверяем, нет ли уже такого ингредиента (по имени и ед. изм.)
                if not Ingredient.objects.filter(name=item['name'], measurement_unit=item['measurement_unit']).exists():
                    ingredients_to_create.append(
                        Ingredient(name=item['name'], measurement_unit=item['measurement_unit'])
                    )
            # Используем bulk_create для эффективной вставки множества объектов
            Ingredient.objects.bulk_create(ingredients_to_create)

            self.stdout.write(self.style.SUCCESS(f'Успешно загружено {len(ingredients_to_create)} новых ингредиентов.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))
