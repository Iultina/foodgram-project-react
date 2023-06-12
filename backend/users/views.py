from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .serializers import SetPasswordSerializer, UserSerializer, SubscriptionSerializer
from .models import Follow, User
from django.shortcuts import get_object_or_404


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    '''
    Просмотр списка пользователей.
    Регистрация пользователей.
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

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticatedOrReadOnly,),
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
    
    @action(
        methods=['get'],
        detail=False,
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        '''Список подписок пользователя.''' 
        user = self.request.user
        subscriptions = user.follower.all()
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'], 
        detail=True, 
        serializer_class=SubscriptionSerializer, 
        permission_classes=(IsAuthenticated,), 
    ) 
    def subscribe(self, request, pk=None): 
        '''Добавление и удаление подписок пользователя.'''
        user = request.user
        target_user = get_object_or_404(User, pk=pk)
        if user == target_user:
            return Response(
                {'error': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if user.following.filter(pk=target_user.pk).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                Follow.objects.create(user=user, author=target_user)
                return Response(
                    {'status': 'Вы успешно подписались на пользователя'},
                    status=status.HTTP_200_OK
                )
        elif request.method == 'DELETE':
            if user.following.filter(pk=target_user.pk).exists():
                Follow.objects.filter(user=user, author=target_user).delete()
                return Response({'status': 'Вы успешно отписались от пользователя'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Вы не подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)
# разобраться с user=user, author=target_user
