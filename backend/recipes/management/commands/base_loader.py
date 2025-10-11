import json

from django.core.management.base import BaseCommand


class BaseLoader(BaseCommand):
    """Базовый класс для загрузки данных из JSON файлов."""
    model = None
    file_path = None
    unique_fields = []

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS(f'Начинаю загрузку из {self.file_path}')
        )
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            self.model.objects.bulk_create(
                [self.model(**item) for item in data],
                ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS('Загрузка успешно завершена.')
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл {self.file_path} не найден.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при загрузке {self.file_path}: {e}'
            ))
