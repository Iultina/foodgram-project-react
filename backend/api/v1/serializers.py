import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers

from recipes.models import (RecipeIngredient, FavoritesList, Ingredient,
                            Recipe, ShoppingList, Tag)
from users.serializers import UserSerializer

User = get_user_model


class Base64ImageField(serializers.ImageField):
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
        fields = ('id', 'name',)


class TagSerializer(serializers.ModelSerializer):
    '''Серилизатор для работы с тэгами.'''
    class Meta:
        model = Tag()
        fields = ('id', 'name', 'color', 'slug')

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.StringRelatedField()
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = (
            'author',
            'name',
            'text',
            'image',
            'ingredients',
            'tags',
            'cooking_time',
            'pub_date',
            'is_favorited'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                return obj.favorites.filter(user=user).exists()
        return False
    
    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['ingredient']['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount'],
                measurement_unit=ingredient_data['measurement_unit']
            )
        return recipe


class FavoritesListSerializer(serializers.Serializer):
    class Meta:
        model = FavoritesList
        fields = []


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = []


class ShoppingDownloadSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingList
        fields = ('ingredient', 'amount', 'measurement_unit')


# class ShoppingDownloadSerializer(serializers.ModelSerializer):
#     ingredient = serializers.SerializerMethodField()
#     amount = serializers.SerializerMethodField()
#     measurement_unit = serializers.SerializerMethodField()

#     class Meta:
#         model = ShoppingList
#         fields = ('ingredient', 'amount', 'measurement_unit')

#     def get_ingredient(self, obj):
#         return obj.recipe.ingredients.name
 
#     def get_amount(self, obj):
#         return obj.recipe.amount

#     def get_measurement_unit(self, obj):
#         return obj.recipe.measurement_unit
