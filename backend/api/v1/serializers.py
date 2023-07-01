import base64
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers

from recipes.models import (FavoritesList, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from users.models import Follow, User

# class CustomUserSerializer(serializers.ModelSerializer):
#     '''Сериализатор для работы с пользователями.'''

#     class Meta:
#         model = User
#         fields = (
#             'username',
#             'password',
#             'first_name',
#             'last_name',
#             'email',
#         )

#     def validate_username(self, value):
#         '''Проверяем, что username не содержит недопустимые символы.'''
#         print('Аутентификация серилизатор')
#         username = value
#         if not re.match(r'^[\w.@+-]+$', username):
#             ValidationError(
#                 'Username содержит недопустимые символы'
#             )
#         return value

class UserReadSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    print('Работает гет серилизатор')

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                return Follow.objects.filter(
                    user=user, author=obj).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(
        style={
            'input_type': 'password'
        },
        write_only=True,
    )
    print('Работает криэйт серилизатор')

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password')


class SetPasswordSerializer(serializers.Serializer):
    '''Сериализатор для смены пароля.'''

    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)


class SubscriptionSerializer(serializers.ModelSerializer):
    '''Сериализатор для получения списка подписок пользователя.'''

    author = UserReadSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('author',)


class Base64ImageField(serializers.ImageField):
    '''Преобразование данных изображения base64 в объект файла.'''

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    '''Серилизатор для работы с ингридиентами.'''

    class Meta:
        model = Ingredient()
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    '''Серилизатор для работы с тэгами.'''

    class Meta:
        model = Tag()
        fields = ('id', 'name', 'color', 'slug')

class ShortRecipeSerializer(serializers.ModelSerializer):
    '''Серилизатор для краткого вывода рецептов.'''

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',    
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Добавление ингредиентов в рецепт.'''

    id = serializers.IntegerField(write_only=True)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurements_unit'
    )
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    '''Получение списка рецептов.'''

    author = UserReadSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',               
            'cooking_time',    
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                shopping_list = ShoppingList.objects.filter(user=user, recipe=obj)
                return shopping_list.exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Создание и обновление рецептов.'''

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, **ingredient_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data): 
        ingredients_data = validated_data.pop('ingredients', None) 
        tags_data = validated_data.pop('tags', None) 
 
        if ingredients_data: 
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=instance) 
            recipe_ingredients_ids = [recipe_ingredient.id for recipe_ingredient in recipe_ingredients] 
            for ingredient_data in ingredients_data: 
                if 'id' in ingredient_data: 
                    recipe_ingredient_id = ingredient_data.pop('id') 
                    if recipe_ingredient_id in recipe_ingredients_ids: 
                        RecipeIngredient.objects.filter(id=recipe_ingredient_id).update(**ingredient_data) 
                        recipe_ingredients_ids.remove(recipe_ingredient_id) 
                else: 
                    ingredient = Ingredient.objects.get(id=ingredient_data['ingredient']) 
                    RecipeIngredient.objects.create(recipe=instance, ingredient=ingredient, **ingredient_data)
        if tags_data: 
            instance.tags.set(tags_data) 
        instance.image = validated_data.get('image', instance.image) 
        instance.name = validated_data.get('name', instance.name) 
        instance.text = validated_data.get('text', instance.text) 
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time) 
        instance.save() 
        return instance


class FavoritesListSerializer(serializers.Serializer): 
    '''Серилизатор для добавления рецепта в избранное.''' 

    id = serializers.IntegerField()

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        try:
            FavoritesList.objects.create(user=self.context['request'].user, recipe=recipe)
        except IntegrityError:
            raise serializers.ValidationError('Этот рецепт уже есть в избранном')
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    '''Просмотр списка подписок пользователя.'''

    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = ShortRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name','is_subscribed', 'recipes', 'recipes_count')
 
    def get_recipes_count(self, obj):
        print(obj)
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        return True


class SubscribeSerializer(serializers.Serializer):
    '''Добавление и удаление подписок пользователя.'''

    id = serializers.IntegerField()

    def create(self, validated_data):
        user = self.context['request'].user
        author = get_object_or_404(User, pk=validated_data['id'])
        if user == author:
            raise serializers.ValidationError('Вы не можете подписаться на себя')
        try:
            Follow.objects.create(user=user, author=author)
        except IntegrityError:
            raise serializers.ValidationError('Вы уже подписаны на этого пользователя')
        serializer = SubscriptionSerializer(author)
        return serializer.data
    

class ShoppingCartSerializer(serializers.Serializer):
    '''Добавление и удаление рецептов из корзины покупок.'''

    id = serializers.IntegerField()

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        #try:
        ShoppingList.objects.create(user=self.context['request'].user, recipe=recipe)
        # except IntegrityError:
        #     raise serializers.ValidationError('Этот рецепт уже есть в избранном')
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data
    
class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = RecipeGetSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = ('recipe',)
