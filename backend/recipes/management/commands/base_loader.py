import json

from django.core.management.base import BaseCommand


class BaseLoader(BaseCommand):
    """Базовый класс для загрузки данных из JSON файлов."""
    model = None
    file_path = None

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS(f'Начинаю загрузку из {self.file_path}')
        )
        try:
            # Считаем, сколько записей было до вставки
            count_before = self.model.objects.count()

            with open(self.file_path, 'r', encoding='utf-8') as file:
                # Объединяем загрузку JSON и создание списка объектов
                self.model.objects.bulk_create(
                    [self.model(**item) for item in json.load(file)],
                    ignore_conflicts=True
                )

            # Считаем, сколько стало после, и выводим разницу
            count_after = self.model.objects.count()
            added_count = count_after - count_before

            self.stdout.write(self.style.SUCCESS(
                f'Загрузка завершена. Добавлено {added_count} новых записей.'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл {self.file_path} не найден.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при загрузке {self.file_path}: {e}'
            ))
