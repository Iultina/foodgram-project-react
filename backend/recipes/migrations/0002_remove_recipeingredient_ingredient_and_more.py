# Generated by Django 4.2.2 on 2023-06-23 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipeingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='recipeingredient',
            name='recipe',
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipes', to='recipes.ingredient', verbose_name='Ингредиент'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Рецепт'),
            preserve_default=False,
        ),
    ]