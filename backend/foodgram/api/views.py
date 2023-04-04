from django.db.models import Exists, OuterRef, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import IsAuthor
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          TagSerializer, RecipeInputSerializer,
                          RecipeSerializer, ShoppingCardSerializer)
from .viewsets import ListRetriveViewSet, ListViewSet
from recipes.models import (Favorite, Follow, IngredientInRecipe, Ingredient,
                            Recipe, ShoppingList, Tag)
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingList.objects.filter(user=user,
                                                recipe=OuterRef('pk'))
                )
            ).all()
        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
        ).all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeInputSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAuthor(),)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    ordering = ('id',)


class IngredientViewSet(ListRetriveViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    ordering = ('id',)

    def get_queryset(self):
        name_filter = self.request.query_params.get('name')
        if name_filter:
            queryset_1 = Ingredient.objects.filter(
                name__istartswith=name_filter).annotate(rank=Value(1))
            queryset_2 = Ingredient.objects.filter(
                name__icontains=name_filter).annotate(rank=Value(2))
            return queryset_1.union(queryset_2).order_by('rank')[:10]
        return Ingredient.objects.all()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_shopping_card(request):
    ingredients = IngredientInRecipe.objects.filter(
        recipe__recipe_to_shopping__user=request.user
    )
    shopping_data = {}
    for ingredient in ingredients:
        if str(ingredient.ingredient) in shopping_data:
            shopping_data[f'{str(ingredient.ingredient)}'] += ingredient.amount
        else:
            shopping_data[f'{str(ingredient.ingredient)}'] = ingredient.amount
    filename = "shopping-list.txt"
    content = ''
    for ingredient, amount in shopping_data.items():
        content += f"{ingredient} - {amount};\n\n"
    response = HttpResponse(content, content_type='text/plain',
                            status=status.HTTP_200_OK)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return response


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def add_del_shopping_card(request, recipe_id):
    if request.method == "POST":
        serializer = ShoppingCardSerializer(
            data=request.data,
            context={'request': request, 'recipe_id': recipe_id}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user,
                            recipe=get_object_or_404(Recipe, id=recipe_id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response("Ошибка введенных данных",
                        status=status.HTTP_400_BAD_REQUEST)
    ShoppingList.objects.get(
        user=request.user,
        recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def favorite_view(request, recipe_id):
    if request.method == "POST":
        serializer = FavoriteSerializer(
            data=request.data,
            context={'request': request, 'recipe_id': recipe_id}
        )
        if serializer.is_valid(raise_exception=True):
            recipe = get_object_or_404(Recipe, id=recipe_id)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response("Ошибка введенных данных",
                        status=status.HTTP_400_BAD_REQUEST)
    Favorite.objects.get(
        user=request.user,
        recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ListSubscribeViewSet(ListViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('id',)

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def add_del_subscribe(request, user_id):
    try:
        author = User.objects.get(id=user_id)
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "POST":
        serializer = FollowSerializer(
            data=request.data,
            context={'request': request, 'user_id': user_id}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response("Ошибка введенных данных",
                        status=status.HTTP_400_BAD_REQUEST)
    serializer = FollowSerializer(
        data=request.data,
        context={'request': request, 'user_id': user_id}
    )
    if serializer.is_valid(raise_exception=True):
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        if self.action == "create":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        if self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        return self.serializer_class

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)
