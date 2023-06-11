from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, IngridientViewSet, TagViewSet, RecipeViewSet

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('ingridients', IngridientViewSet, basename='ingridients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
