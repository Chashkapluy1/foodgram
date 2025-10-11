from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import CustomUserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router_v1.urls)),
]
