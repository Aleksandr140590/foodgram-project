from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from djoser.conf import settings
from djoser.views import UserViewSet
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

# from .filters import .
from .permissions import IsAuthor
from .serializers import (RecipeSerializer, TagSerializer, IngredientSerializer,
                          ShoppingCardSerializer, FavoriteSerializer,
                          FollowSerializer,
                          CustomUserSerializer, RecipeInputSerializer)
from .viewsets import ListRetriveViewSet, ListViewSet
from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingList,
                            Follow)
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
#    filter_backends = (DjangoFilterBackend, )
#    filterset_class = TitleFilter
    ordering = ('-pub_date',)
    permission_classes = (IsAuthor,)

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
            ),
            is_in_shopping_cart=Exists(
                ShoppingList.objects.filter(user=user, recipe=OuterRef('pk'))
            )
        ).all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeInputSerializer

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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    ordering = ('id',)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_shopping_card(request):
    # тут формируется файл
    return Response(status=status.HTTP_200_OK)

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
    if request.method == "DELETE":
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
    if request.method == "DELETE":
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


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def add_del_subscribe(request, user_id):
    try:
        author = User.objects.get(id=user_id)
    except:
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
    if request.method == "DELETE":
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
        elif self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password

        return self.serializer_class

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)