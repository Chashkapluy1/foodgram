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
            count_before = Ingredient.objects.count()

            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                Ingredient.objects.bulk_create(
                    [Ingredient(**row) for row in reader],
                    ignore_conflicts=True
                )

            count_after = Ingredient.objects.count()
            added_count = count_after - count_before

            self.stdout.write(self.style.SUCCESS(
                f'Загрузка завершена. Добавлено {added_count} новых записей.'
            ))

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке: {e}')
            )
