from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, IngredientViewSet, TagViewSet
from users.views import UserViewSet

app_name = 'api_v1'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingridients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
