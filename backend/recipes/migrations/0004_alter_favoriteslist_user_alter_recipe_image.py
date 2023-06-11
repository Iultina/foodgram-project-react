# Generated by Django 4.2.2 on 2023-06-11 09:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_rename_hexcolor_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoriteslist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_favorites', to=settings.AUTH_USER_MODEL, verbose_name='владелец списка избранных рецептов'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/media', verbose_name='Изображение'),
        ),
    ]
