from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeWriteSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # OFF пагинацию


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для ингредиентов.
    Есть поиск по названию.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None  # OFF пагинацию

    def get_queryset(self):
        """
        Фильтрует ингредиенты по частичному вхождению в начале названия.
        """
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов.
    Предоставляет полный CRUD-функционал, а также кастомные
    действия для добавления в избранное и список покупок.
    """
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags',
        # Оптимизированный prefetch для ингредиентов вместе с их количеством
        Prefetch(
            'recipeingredient_set',
            queryset=RecipeIngredient.objects.select_related('ingredient')
        )
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """
        Возвращает класс сериализатора в зависимости от действия.
        Для записи используется RecipeWriteSerializer, для чтения - RecipeSerializer.
        """
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """
        При создании рецепта автором указывается текущий пользователь.
        """
        serializer.save(author=self.request.user)

    def _add_or_remove_from_list(self, model, request, pk):
        """
        Вспомогательный метод для добавления/удаления рецепта
        из списка (Избранное или Список покупок).
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        instance_exists = model.objects.filter(user=request.user, recipe=recipe).exists()

        if request.method == 'POST':
            if instance_exists:
                return Response(
                    {'errors': 'Рецепт уже добавлен в список.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSerializer(recipe)  # Используем короткий сериализатор
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Метод DELETE
        if not instance_exists:
            return Response(
                {'errors': 'Рецепта нет в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из избранного.
        """
        return self._add_or_remove_from_list(Favorite, request, pk)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из списка покупок.
        """
        return self._add_or_remove_from_list(ShoppingCart, request, pk)
