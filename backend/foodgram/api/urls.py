from django.urls import path, include
from rest_framework import routers

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    get_shopping_card, add_del_shopping_card, favorite_view,
                    ListSubscribeViewSet, add_del_subscribe, CustomUserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'users/subscriptions', ListSubscribeViewSet,
                   basename='get_subscribe')
router_v1.register("users", CustomUserViewSet)

add_urls = [
    path('recipes/download_shopping_cart/', get_shopping_card,
         name='get_shopping_cart'),
    path('recipes/<int:recipe_id>/shopping_cart/', add_del_shopping_card,
         name='add_del_shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/', favorite_view, name='favorite'),
    path('users/<int:user_id>/subscribe/', add_del_subscribe, name='subscribe')
]


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include(add_urls)),
    path('', include('djoser.urls')),  # Работа с пользователями
    path('auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]