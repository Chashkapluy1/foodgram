from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Подключаем наши новые URL из приложения recipes
    path('api/', include('recipes.urls')),
    # Эндпоинты для пользователей (должны идти после, чтобы не было конфликтов)
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
]
