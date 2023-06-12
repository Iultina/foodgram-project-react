
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, Tag, FavoritesList

from .filters import IngredientFilter, RecipeFilter
from .serializers import (TagSerializer, IngredientSerializer, RecipeSerializer, FavoritesListSerializer)
from django.shortcuts import get_object_or_404


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
            return Response({'Рецепт успешно добавлен в избранное'}, status=status.HTTP_200_OK )
        elif request.method == 'DELETE':
            favorites = FavoritesList.objects.filter(user=request.user, recipe=recipe)
            favorites.delete()
            return Response({'Рецепт успешно удален из избранного'}, status=status.HTTP_200_OK)


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
