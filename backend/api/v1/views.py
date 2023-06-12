
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import FavoritesList, Ingredient, Recipe, Tag, ShoppingList

from .filters import IngredientFilter, RecipeFilter
from .serializers import (FavoritesListSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, ShoppingDownloadSerializer)
from django.db.models import Sum

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    '''Работа с рецептами.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminUser, IsAuthenticatedOrReadOnly)
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete'
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=FavoritesListSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            FavoritesList.objects.create(user=request.user, recipe=recipe)
            return Response(
                {'Рецепт успешно добавлен в избранное'},
                status=status.HTTP_200_OK
            )
        elif request.method == 'DELETE':
            favorites = FavoritesList.objects.filter(
                user=request.user, recipe=recipe
            )
            favorites.delete()
            return Response(
                {'Рецепт успешно удален из избранного'},
                status=status.HTTP_200_OK
            )

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if ShoppingList.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise ValidationError(
                    'Вы уже добавили этот рецепт в список покупок'
                )
            ShoppingList.objects.create(user=user, recipe=recipe)
            return Response(
                {'Рецепт успешно добавлен в список покупок'},
                status=status.HTTP_201_CREATED
            )
        if self.request.method == 'DELETE':
            if not ShoppingList.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise ValidationError(
                    'Вы не добавляли этот рецепт в список покупок'
                )
            shopping_cart = get_object_or_404(
                ShoppingList,
                user=user,
                recipe=recipe
            )
            shopping_cart.delete()
            return Response(
                {'Рецепт удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart_list(self, request):
        user = self.request.user
        shopping_list = ShoppingList.objects.filter(user=user)
        serializer = ShoppingDownloadSerializer(
            shopping_list, many=True, context={'request': request}
        )
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Получение списка ингридиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Получение списка тэгов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)
