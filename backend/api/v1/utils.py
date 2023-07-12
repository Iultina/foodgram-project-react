from django.db.models import Sum

from recipes.models import Ingredient, RecipeIngredient


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
