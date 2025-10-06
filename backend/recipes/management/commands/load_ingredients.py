import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из JSON файла в базу данных"

    def handle(self, *args, **kwargs):
        file_path = "../data/ingredients.json"
        start_message = f"Начинаю загрузку из {file_path}"
        self.stdout.write(self.style.SUCCESS(start_message))

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                ingredients_data = json.load(file)

            ingredients_to_create = []
            for item in ingredients_data:
                if not Ingredient.objects.filter(
                    name=item["name"],
                    measurement_unit=item["measurement_unit"],
                ).exists():
                    ingredients_to_create.append(
                        Ingredient(
                            name=item["name"],
                            measurement_unit=item["measurement_unit"],
                        )
                    )
            Ingredient.objects.bulk_create(ingredients_to_create)

            count = len(ingredients_to_create)
            success_message = (
                f"Успешно загружено {count} новых ингредиентов."
            )
            self.stdout.write(self.style.SUCCESS(success_message))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не найден."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка: {e}"))
