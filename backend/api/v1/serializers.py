import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers

from recipes.models import (CustomRecipeIngredient, FavoritesList, Ingredient,
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


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'name',
            'text',
            'image',
            'ingredients',
            'amount',
            'measurement_unit',
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


class ShoppingDownloadSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingList
        fields = ('ingredient', 'amount', 'measurement_unit')

    def get_ingredient(self, obj):
        if obj.recipe:
            return obj.recipe.ingredients.name
        else:
            return obj.ingredient.name

    def get_amount(self, obj):
        if obj.recipe:
            return obj.recipe.amount
        else:
            return obj.amount

    def get_measurement_unit(self, obj):
        if obj.recipe:
            return obj.recipe.measurement_unit
        else:
            return obj.measurement_unit
