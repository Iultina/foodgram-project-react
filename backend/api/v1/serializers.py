import re

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavoritesList, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from users.models import Follow, User


class UserReadSerializer(UserSerializer):
    """Серилизатор для вывода пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Серилизатор для создания пользователей."""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate_username(self, value):
        """Проверяем, что username не
        содержит недопустимые символы.
        """

        if not re.match(r'^[\w.@+-]+$', value):
            raise ValidationError(
                'Username содержит недопустимые символы'
            )
        return value


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""

    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)


class IngredientSerializer(serializers.ModelSerializer):
    """Серилизатор для работы с ингридиентами."""

    class Meta:
        model = Ingredient()
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Серилизатор для работы с тэгами."""

    class Meta:
        model = Tag()
        fields = ('id', 'name', 'color', 'slug')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор для краткого вывода рецептов."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Добавление ингредиентов в рецепт."""

    id = serializers.IntegerField(write_only=True)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurements_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        """Проверяем, что количество ингредиента больше 0."""

        if value <= 0:
            raise ValidationError(
                'Количество ингредиента должно быть больше 0'
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    """Получение списка рецептов."""

    author = UserReadSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=False)

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
        user = request.user
        if not request or not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if not request or not user.is_authenticated:
            return False
        shopping_list = ShoppingList.objects.filter(
            user=user, recipe=obj
        )
        return shopping_list.exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание и обновление рецептов."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)

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

    def validate_cooking_time(self, value):
        """Проверяем, что время приготовления больше 0."""

        if value <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return value

    def add_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            print('add_ingredients')
            print(ingredient_data)
            ingredient_id = ingredient_data.pop('id')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.update_or_create(
                recipe=recipe, ingredient=ingredient, **ingredient_data
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags_data)
        print('Тут смотрим ингредиенты в рецепте create')
        print(recipe.ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        print(validated_data)
        print(ingredients)
        tags = validated_data.pop('tags')
        if not ingredients:
            recipe.tags.set(tags)
            return super().update(recipe, validated_data)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)


class FavoritesListSerializer(serializers.Serializer):
    """
    Сериализатор для добавления рецепта в избранное.
    """

    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if FavoritesList.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        user = self.context['request'].user
        FavoritesList.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Просмотр списка подписок пользователя."""

    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = ShortRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = self.context['request'].user
        if not request or not user.is_authenticated:
            return False
        return obj.following.filter(user=user).exists()


class SubscribeSerializer(serializers.Serializer):
    """Добавление и удаление подписок пользователя."""

    def validate(self, data):
        user = self.context['request'].user
        print(self.context['id'])
        author = get_object_or_404(User, pk=self.context['id'])
        print(author)
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя'
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        author = get_object_or_404(User, pk=validated_data['id'])
        Follow.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(author)
        return serializer.data


class ShoppingCartSerializer(serializers.Serializer):
    """Добавление и удаление рецептов из корзины покупок."""

    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if ShoppingList.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        ShoppingList.objects.create(
            user=self.context['request'].user,
            recipe=recipe
        )
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data
