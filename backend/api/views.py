from datetime import datetime

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Favorite, Follow, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
    User
)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AuthorSubscriptionSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeShortSerializer, RecipeWriteSerializer, TagSerializer,
    UserReadSerializer
)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = [AllowAny]

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        if request.method == 'DELETE':
            deleted_count, _ = Follow.objects.filter(
                user=request.user, author_id=id
            ).delete()
            if not deleted_count:
                raise ValidationError({'errors': 'Вы не были подписаны.'})
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = get_object_or_404(User, id=id)

        if request.user == author:
            raise ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )
        _, created = Follow.objects.get_or_create(user=request.user,
                                                  author=author)
        if not created:
            raise ValidationError(
                {'errors': f'Вы уже подписаны на {author.username}.'}
            )
        return Response(
            AuthorSubscriptionSerializer(
                author, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан текущий пользователь."""
        queryset = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = AuthorSubscriptionSerializer(
            queryset, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'patch', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Метод для управления аватаром пользователя."""
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов с поиском."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to_list(self, model, user, pk):
        """Вспомогательный метод для добавления в список."""
        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            list_names = {
                Favorite: 'избранное',
                ShoppingCart: 'список покупок'
            }
            list_name = list_names.get(model, 'этот список')
            raise ValidationError(
                {'errors':
                 f'Рецепт "{recipe.name}" уже в списке ({list_name})'}
            )
        return Response(
            RecipeShortSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    def _remove_from_list(self, model, user, pk):
        """Вспомогательный метод для удаления из списка."""
        get_object_or_404(model, user=user, recipe_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_list(Favorite, request.user, pk)
        return self._remove_from_list(Favorite, request.user, pk)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_list(ShoppingCart, request.user, pk)
        return self._remove_from_list(ShoppingCart, request.user, pk)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Отдает пользователю .txt файл со списком покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

        recipes_in_cart = Recipe.objects.filter(
            shopping_carts__user=request.user
        ).select_related('author')

        today = datetime.today()
        context = {
            'date': today.strftime('%d.%m.%Y'),
            'ingredients': ingredients,
            'recipes': recipes_in_cart
        }

        shopping_list_text = render_to_string(
            'shopping_list.txt', context
        )
        return FileResponse(
            shopping_list_text,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )
