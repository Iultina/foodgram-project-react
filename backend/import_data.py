import csv
import os
import random
import requests
from faker import Faker
from rest_framework.authtoken.models import Token


from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import User

fake = Faker(['ru_RU'])

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
TOKEN_ENDPOINT = 'http://127.0.0.1/api/auth/token/login/'


class Command(BaseCommand):
    help = 'Create demo data'

    def handle(self, *args, **options):

        def create_objects_from_csv(file_path, create_func):
            with open(file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    create_func(*row)

        def create_ingredient(name, measurement_unit):
            Ingredient.objects.update_or_create(
                name=name, measurement_unit=measurement_unit)

        def create_tag(name, color, slug):
            Tag.objects.update_or_create(name=name, color=color, slug=slug)

        create_objects_from_csv(
            os.path.join(DATA_DIR, 'ingredients.csv'),
            create_ingredient
        )
        create_objects_from_csv(os.path.join(DATA_DIR, 'tags.csv'), create_tag)

        if not User.objects.filter(email__startswith='user').exists():
            all_ingredients = Ingredient.objects.all()
            all_tags = Tag.objects.all()
            PHOTO_PATH = os.path.join(DATA_DIR, 'photo')

            for i in range(4):
                user, created = User.objects.get_or_create(
                    email=f'user{i}@example.com',
                    defaults={
                        'email': f'user{i}@example.com',
                        'username': f'User{i}',
                        'first_name': fake.first_name_male(),
                        'last_name': fake.last_name_male(),
                        'password': make_password('password1'),
                    },
                )
                token, created = Token.objects.get_or_create(user=user)
                for j in range(2):
                    ingredients = random.sample(list(all_ingredients), 4)
                    tags = random.sample(list(all_tags), 2)

                    image_file_path = os.path.join(
                        PHOTO_PATH, f'{j + 1}.jpg')
                    with open(image_file_path, 'rb') as image_file:
                        recipe = Recipe(
                            author=user,
                            name=fake.sentence(
                                nb_words=2, variable_nb_words=False),
                            text=fake.paragraph(
                                nb_sentences=5, variable_nb_sentences=False),
                            cooking_time=random.randint(20, 120),
                            image=ImageFile(image_file, name=f'{j + 1}.jpg'),
                        )
                        recipe.save()
                        RecipeIngredient.objects.bulk_create(
                            [
                                RecipeIngredient(
                                    recipe=recipe,
                                    ingredient=ingredient,
                                    amount=random.randint(1, 100)
                                ) for ingredient in ingredients
                            ]
                        )
                        recipe.ingredients.set(ingredients)
                        recipe.tags.set(tags)

        else:
            print("Demo users already exist. Skipping demo data creation.")

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
