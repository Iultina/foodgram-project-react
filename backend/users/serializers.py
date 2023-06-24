from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Follow

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с пользователями.'''

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        )


class SetPasswordSerializer(serializers.Serializer):
    '''Сериализатор для смены пароля.'''
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)


class SubscriptionSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('author',)
