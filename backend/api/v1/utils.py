from django.db.models import Sum
from rest_framework.pagination import PageNumberPagination

from recipes.models import (Ingredient, RecipeIngredient)

PAGE_NUMBERS = 6


class CustomPagination(PageNumberPagination):
    page_size = PAGE_NUMBERS


def create_shopping_list_report(shopping_cart):
    recipes = shopping_cart.values_list('recipe_id', flat=True)
    buy_list = RecipeIngredient.objects.filter(
        recipe__in=recipes
    ).values(
        'ingredient'
    ).annotate(
        amount=Sum('amount')
    )
    buy_list_text = 'Foodgram\nСписок покупок:\n'
    for item in buy_list:
        ingredient = Ingredient.objects.get(pk=item['ingredient'])
        amount = item['amount']
        buy_list_text += (
            f'{ingredient.name}, {amount} '
            f'{ingredient.measurement_unit}\n'
        )
    return buy_list_text
