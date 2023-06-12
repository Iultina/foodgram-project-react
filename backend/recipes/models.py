from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'название ингредиента',
        max_length=255,
        blank=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'название тэга',
        max_length=54,
        blank=False,
        unique=True
    )
    color = models.CharField(
        'цвет',
        max_length=7,
        blank=False,
        default='#ffffff'
    )
    slug = models.SlugField(
        'Слаг тэга',
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name = 'recipes',
        verbose_name = 'Автор рецепта'
    )
    name = models.CharField(
        'название рецепта',
        max_length=200,
        blank=False
    )
    text = models.TextField(
        'описание рецепта',
        blank=False
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        related_name='recipes',
        verbose_name='ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes',
        verbose_name='тэги',
    )
    cooking_time = models.DurationField(blank=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
    
class CustomRecipeIngredient(models.Model): 
    '''Модель для добавления ингредиентов в рецепте.''' 
    recipe = models.ForeignKey( 
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='recipe_ingredient', 
        verbose_name = 'Рецепт', 
    ) 
    ingredient = models.ForeignKey( 
        Ingredient, 
        on_delete=models.CASCADE, 
        related_name='ingredient', 
        verbose_name= 'Ингредиент', 
    ) 
    amount = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name= 'Количество', 
    ) 
    measurement_unit = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Единица измерения'
    )
    
    class Meta: 
        constraints = ( 
            models.UniqueConstraint( 
                fields=('recipe', 'ingredient',), 
                name='recipe_ingredient_exists'), 
        ) 
        verbose_name = 'Ингредиент в рецепте', 
        verbose_name_plural = 'Ингредиенты в рецепте' 

class FavoritesList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name='владелец списка избранных рецептов'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorites',
        verbose_name='избранные рецепты'
    )

    class Meta:
        verbose_name = 'Список избранных рецептов'
        verbose_name_plural = 'Списки избранных рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            ),
        ]

    def __str__(self):
        return f'Избранный рецепт {self.user}'
    

class ShoppingList(models.Model): 
    user = models.ForeignKey( 
        User, 
        on_delete=models.CASCADE, 
        related_name='shopping_list', 
        verbose_name='владелец списка покупок' 
    ) 
    recipe = models.ForeignKey( 
        Recipe, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name='shopping_lists', 
        verbose_name='рецепт из списка покупок' 
    ) 
    class Meta: 
        verbose_name = 'Список покупок' 
        verbose_name_plural = 'Списки покупок' 
        constraints = [ 
            models.UniqueConstraint( 
                fields=['user', 'recipe'], 
                name='unique_recipe' 
            ), 
        ]

    def __str__(self):
        return f'Список покупок {self.user}'
