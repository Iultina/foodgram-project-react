from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from recipes.models import Ingridient, Tag, Recipe

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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


class IngridientSerializer(serializers.ModelSerializer):
    '''Серилизатор для работы с ингридиентами'''
    class Meta:
        model = Ingridient()
        fields = ('id', 'name', 'measurement_unit')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag()
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer): 
    is_favorited = serializers.SerializerMethodField() 
 
    class Meta:
        model = Recipe
        fields = ( 
            'author', 
            'name', 
            'description', 
            'image', 
            'ingridients', 
            'tags', 
            'cooking_duration', 
            'pub_date', 
            'is_favorited' 
        ) 
 
    def get_is_favorited(self, obj): 
        request = self.context.get('request') 
        if request: 
            user = request.user 
            if user.is_authenticated: 
                return obj.favorites.filter(user=user).exists() 
        return False