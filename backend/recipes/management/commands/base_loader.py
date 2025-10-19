import json

from django.core.management.base import BaseCommand


class BaseLoader(BaseCommand):
    """Базовый класс для загрузки данных из JSON файлов."""
    model = None
    file_path = None

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS(f'Начинается загрузка из {self.file_path}')
        )
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                created_items = self.model.objects.bulk_create(
                    (self.model(**item) for item in json.load(file)),
                    ignore_conflicts=True
                )
            self.stdout.write(self.style.SUCCESS(
                (f'Загрузка завершена. Добавлено {len(created_items)} '
                 'новых записей.')
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при загрузке {self.file_path}: {e}'
            ))
