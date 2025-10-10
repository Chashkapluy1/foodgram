from django.db.models import Prefetch, Sum
from django.http import HttpResponse
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
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            return queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags",
        Prefetch(
            "recipeingredient_set",
            queryset=RecipeIngredient.objects.select_related("ingredient"),
        ),
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_or_remove_from_list(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        instance_exists = model.objects.filter(
            user=request.user, recipe=recipe
        ).exists()

        if request.method == "POST":
            if instance_exists:
                return Response(
                    {"errors": "Рецепт уже добавлен в список."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSerializer(recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not instance_exists:
            return Response(
                {"errors": "Рецепта нет в списке."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._add_or_remove_from_list(Favorite, request, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove_from_list(ShoppingCart, request, pk)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_cart__user=user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        shopping_list_content = "Список покупок для Foodgram:\n\n"
        for item in ingredients:
            name = item["ingredient__name"]
            unit = item["ingredient__measurement_unit"]
            amount = item["total_amount"]
            shopping_list_content += f"● {name} ({unit}) — {amount}\n"

        response = HttpResponse(
            shopping_list_content, content_type="text/plain"
        )
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
