import json

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    """
    Загрузка тегов из JSON файла в базу данных.
    Использует bulk_create с ignore_conflicts.
    """
    help = 'Загрузка тегов из data/tags.json'

    def handle(self, *args, **kwargs):
        file_path = 'data/tags.json'
        self.stdout.write(self.style.SUCCESS(f'Начинаю загрузку из {file_path}'))

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tags_data = json.load(file)

            tags_to_create = [
                Tag(**item) for item in tags_data
            ]

            Tag.objects.bulk_create(
                tags_to_create,
                ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                f'Загрузка тегов завершена.'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл {file_path} не найден.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Произошла ошибка при загрузке {file_path}: {e}'
            ))
