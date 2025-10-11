from django.urls import path
from .views import recipe_short_link_redirect

urlpatterns = [
    path('r/<int:recipe_id>/', recipe_short_link_redirect, name='short-link'),
]
