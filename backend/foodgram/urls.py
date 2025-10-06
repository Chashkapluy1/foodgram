from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

router_v1 = DefaultRouter()
# Регистрируем наш вьюсет
router_v1.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recipes.urls")),
    # Подключаем JWT-эндпоинты
    path("api/auth/", include("djoser.urls.jwt")),
    # Наш роутер
    path("api/", include(router_v1.urls)),
]
