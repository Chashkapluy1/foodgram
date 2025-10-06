from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import SubscriptionSerializer


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для пользователей."""

    queryset = User.objects.all()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Подписаться или отписаться от автора."""
        author = get_object_or_404(User, id=id)

        if request.user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription_exists = Follow.objects.filter(
            user=request.user, author=author
        ).exists()

        if request.method == "POST":
            if subscription_exists:
                return Response(
                    {"errors": "Вы уже подписаны на этого автора."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.create(user=request.user, author=author)
            serializer = SubscriptionSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscription_exists:
            return Response(
                {"errors": "Вы не были подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан текущий пользователь."""
        authors = User.objects.filter(following__user=request.user)
        paginated_authors = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            paginated_authors, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
