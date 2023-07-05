
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoritesList, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follow

from .filters import RecipeFilter
from .mixins import CreateListRetrieveViewSet
from .serializers import (FavoritesListSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeGetSerializer,
                          SetPasswordSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, SubscriptionSerializer,
                          TagSerializer, UserCreateSerializer,
                          UserReadSerializer)
from .utils import CustomPagination

User = get_user_model()


class UserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'subscribe':
            return SubscribeSerializer
        return UserCreateSerializer

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        '''Информация о своем аккаунте.'''

        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('post',),
        detail=False,
        serializer_class=SetPasswordSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        '''Страница смены пароля.'''

        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        if not user.check_password(old_password):
            return Response(
                'Неверный пароль',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response('Пароль успешно изменен', status=status.HTTP_200_OK)

    @action(
        methods=('get',),
        detail=False,
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination,
    )
    def subscriptions(self, request):
        '''Просмотр подписок пользователя.'''

        user = request.user
        subscriptions = user.follower.all()
        users_id = [subscription_instance.author.id
                    for subscription_instance in subscriptions]
        users = User.objects.filter(id__in=users_id)
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.serializer_class(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=SubscribeSerializer,
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, pk=None):
        '''Добавление и удаление подписок пользователя.'''

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(response_data)
        elif request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=self.request.user,
                author=get_object_or_404(User, pk=pk)
            )
            subscription.delete()
            return Response(
                {'Успешная отписка'},
                status=status.HTTP_204_NO_CONTENT
            )


class RecipeViewSet(viewsets.ModelViewSet):
    '''Работа с рецептами.'''

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminUser, IsAuthenticatedOrReadOnly)
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        '''Определение серилизатора.'''

        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        elif self.action == 'favorite':
            return FavoritesListSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete',),
        detail=True,
        serializer_class=FavoritesListSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        '''Добавление/удаление рецептов из избранного.'''

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(
                {'message': 'Рецепт успешно добавлен в избранное.',
                 'data': response_data},
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            get_object_or_404(
                FavoritesList, user=self.request.user,
                recipe=get_object_or_404(Recipe, pk=pk)).delete()
            return Response(
                {'Рецепт успешно удален из избранного'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        methods=('post', 'delete',),
        detail=True,
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        '''Добавление/удаление рецепта из корзины.'''

        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(
                {'message': 'Рецепт успешно добавлен в список покупок',
                 'data': response_data}, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            get_object_or_404(
                ShoppingList, user=self.request.user,
                recipe=get_object_or_404(Recipe, pk=pk)).delete()
            return Response(
                {'Рецепт успешно удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        '''Скачать список покупок.'''

        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )
        buy_list_text = 'Foodgram\nСписок покупок:\n'
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            buy_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Получение списка ингридиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Получение списка тэгов.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
