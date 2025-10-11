from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Все API-запросы теперь идут через единую точку входа
    path('api/', include('api.urls')),
]
