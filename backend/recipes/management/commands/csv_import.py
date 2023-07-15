from csv import DictReader
import os

from django.core.management import BaseCommand
from api_yamdb.settings import BASE_DIR
from reviews.models import (
    Category,
    Comment,
    Genre,
    Title,
    Review,
    User,
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('Data download completed')
        for row in DictReader(
            open(os.path.join(BASE_DIR, 'static\\data\\users.csv'))
        ):
            user = User(
                id=row['id'], username=row['username'],
                email=row['email'], role=row['role'],
                bio=row['bio'], first_name=row['first_name'],
                last_name=row['last_name']
            )
            user.save()
        for row in DictReader(
            open(os.path.join(BASE_DIR, 'static\\data\\category.csv'))
        ):
            category = Category(
                id=row['id'], name=row['name'], slug=row['slug']
            )
            category.save()
        for row in DictReader(
            open(os.path.join(BASE_DIR, 'static\\data\\genre.csv'))
        ):
            genre = Genre(id=row['id'], name=row['name'], slug=row['slug'])
            genre.save()
        for row in DictReader(
            open(os.path.join(BASE_DIR, 'static\\data\\titles.csv'))
        ):
            title = Title(
                id=row['id'], name=row['name'],
                year=row['year'], category_id=row['category']
            )
            title.save()
        for row in DictReader(
            open(os.path.join(BASE_DIR, 'static\\data\\review.csv'))
        ):
            review = Review(
                id=row['id'], title_id=row['title_id'],
                text=row['text'], author_id=row['author'],
                score=row['score'], pub_date=row['pub_date']
            )
            review.save()
        for row in DictReader(
            open(os.path.join(BASE_DIR, 'static\\data\\comments.csv'))
        ):
            comment = Comment(
                id=row['id'], review_id=row['review_id'],
                text=row['text'], author_id=row['author'],
                pub_date=row['pub_date']
            )
            comment.save()
