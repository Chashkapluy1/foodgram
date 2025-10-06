from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Добавляем RecipeViewSet в импорты
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

# Создаем роутер
router = DefaultRouter()

# Регистрируем вьюсеты
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes') # Добавляем эту строку

urlpatterns = [
    # Все URL, сгенерированные роутером, будут доступны по этому пути
    path('', include(router.urls)),
]
