from django.urls import include, path
from rest_framework.routers import DefaultRouter

#from users.views import CustomUserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, CustomUserViewSet, SubscribeViewSet

app_name = 'api_v1'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingridients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('users/<int:pk>/subscribe/', SubscribeViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'}), name='subscribe'),
    path('', include(router.urls)),
]
