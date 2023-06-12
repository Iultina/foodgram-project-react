# Generated by Django 4.2.2 on 2023-06-12 12:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_remove_favoriteslist_unique_favorites_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': ('Ингредиент в рецепте',), 'verbose_name_plural': 'Ингредиенты в рецепте'},
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=255, verbose_name='название ингредиента'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', to='recipes.ingredient', verbose_name='ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
    ]
