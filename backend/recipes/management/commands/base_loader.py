from django.core.management.base import BaseCommand


class BaseLoader(BaseCommand):
    """Базовый класс для загрузки данных."""
    model = None
    file_path = None

    def load_data(self):
        raise NotImplementedError("Метод `load_data` должен быть реализован.")

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS(f'Начинаю загрузку из {self.file_path}')
        )
        try:
            self.model.objects.all().delete()
            created_items = self.load_data()
            self.stdout.write(self.style.SUCCESS(
                f'Загрузка завершена. Добавлено {len(created_items)} записей.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при загрузке {self.file_path}: {e}'
            ))
