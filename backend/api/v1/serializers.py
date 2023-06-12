import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers, exceptions
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, CustomRecipeIngredient, Tag, FavoritesList, ShoppingList
from users.serializers import UserSerializer

User = get_user_model


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
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


# class RecipeIngredientSerializer(serializers.ModelSerializer):  
#     id = serializers.SerializerMethodField(method_name='get_id')      
#     name = serializers.SerializerMethodField(method_name='get_name')  
     
#     def get_id(self, obj):   
#         return obj.id  
     
#     def get_name(self, obj): 
#         return obj.name   
     
#     class Meta:  
#         model = CustomRecipeIngredient          
#         fields = ('id', 'name', 'amount', 'measurement_unit') 

 
class RecipeSerializer(serializers.ModelSerializer):  
    is_favorited = serializers.SerializerMethodField() 
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True) 
    ingredients = serializers.SerializerMethodField()
  
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
        ingredients = CustomRecipeIngredient.objects.filter(recipe=obj)
        #serializer = RecipeIngredientSerializer(ingredients, many=True)
        return ingredients #serializer.data


class FavoritesListSerializer(serializers.Serializer):
    class Meta:
        model = FavoritesList
        fields = []
    