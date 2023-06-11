
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import filters, status, viewsets
from .serializers import UserSerializer, SetPasswordSerializer, IngridientSerializer, TagSerializer, RecipeSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from recipes.models import Ingridient, Tag, Recipe


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    '''
    Выводит список пользователей.
    Добавление пользователей.
    '''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    http_method_names = [
        'get',
        'post',
    ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)
    # lookup_field = 'username'

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        '''Информация о своем аккаунте.'''
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        methods=['post'],
        detail=False,
        serializer_class=SetPasswordSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        '''Страница смены пароля.'''
        print(request.data)
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        if not user.check_password(old_password):
            return Response('Неверный пароль', status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response('Пароль успешно изменен', status=status.HTTP_200_OK)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Получение списка ингридиентов.'''
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Получение списка тэгов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)


class RecipeViewSet(viewsets.ModelViewSet): 
    '''Работа с рецептами.''' 
    queryset = Recipe.objects.all() 
    serializer_class = RecipeSerializer 
    permission_classes = (IsAdminUser, IsAuthenticatedOrReadOnly) 
    filter_backends = (DjangoFilterBackend,) 
    filterset_class = RecipeFilter 
