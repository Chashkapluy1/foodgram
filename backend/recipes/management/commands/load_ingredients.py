import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Загрузка ингредиентов из CSV файла без заголовков.
    """
    help = 'Загрузка ингредиентов из data/ingredients.csv'

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.csv'
        self.stdout.write(
            self.style.SUCCESS(f'Начинаю загрузку из {file_path}')
        )
        try:
            # Очищаем таблицу перед загрузкой, чтобы избежать дубликатов
            # при повторном запуске.
            Ingredient.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Старые ингредиенты удалены.')
            )

            with open(file_path, 'r', encoding='utf-8') as file:
                # Используем обычный csv.reader, а не DictReader
                reader = csv.reader(file)

                # Готовим список объектов для массового создания
                ingredients_to_create = [
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in reader if row
                ]

            # Создаем все объекты одним запросом к БД
            Ingredient.objects.bulk_create(ingredients_to_create)

            self.stdout.write(self.style.SUCCESS(
                f'Загрузка завершена. '
                f'Добавлено {len(ingredients_to_create)} новых записей.'
            ))

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке: {e}')
            )
