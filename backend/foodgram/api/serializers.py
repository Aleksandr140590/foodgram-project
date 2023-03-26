import base64
import json

from django.core.files.base import ContentFile
from django.forms import model_to_dict
from rest_framework import serializers
from djoser.serializers import UserSerializer

from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingList,
                            Follow, IngredientInRecipe)
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField
from users.models import User


class CustomPrimaryKeyRelatedField(PrimaryKeyRelatedField):
    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value)
        dict_obj = model_to_dict(value)
        return dict_obj

class ShortRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    image = serializers.ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientInRecipe




class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientInRecipe


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()


    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientInRecipeSerializer(source='ingredientinrecipe_set',
                                               many=True, read_only=True)

    class Meta:
        exclude = ('pub_date', )
        model = Recipe



class ShoppingCardSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = ShoppingList

    def validate(self, data):
        if (self.context['request'].method == "POST" and
                ShoppingList.objects.filter(
                    user=self.context['request'].user,
                    recipe_id=self.context['recipe_id']
                ).exists()):
            raise serializers.ValidationError(
                'Вы уже добавили в список покупок!'
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Favorite

    def validate(self, data):
        if self.context['request'].method == "POST" and Favorite.objects.filter(
                user=self.context['request'].user,
                recipe_id=self.context['recipe_id']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили в избранное!'
            )
        return data


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()


    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = Follow

    def validate(self, data):
        if self.context['request'].method == "POST" and Follow.objects.filter(
                user=self.context['request'].user,
                author_id=self.context['user_id']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на автора!'
            )
        elif (self.context['request'].method == "POST" and
              self.context['request'].user.id == self.context['user_id']):
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!'
            )
        elif (self.context['request'].method == "DELETE" and not
              Follow.objects.filter(
                user=self.context['request'].user,
                author_id=self.context['user_id']
        ).exists()):
            raise serializers.ValidationError(
                'Вы не подписаны на этого автора!'
            )
        return data

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        queryset = obj.author.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(queryset, many=True)
        return serializer.data


    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj.author).exists()

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeInputSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(
        read_only=True, default=CurrentUserDefault())
    tags = CustomPrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    ingredients = IngredientInRecipeWriteSerializer(
        many=True,
        source='ingredientinrecipe_set',
    )

    class Meta:
        exclude = ('pub_date',)
        read_only_fields = ('author', )
        model = Recipe

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(user=self.context['request'].user,
                                     recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(user=self.context['request'].user,
                                           recipe=obj).exists()

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            obj = IngredientInRecipe.objects.create(recipe=recipe, ingredient=ingredient['ingredient']['id'], amount=ingredient['amount'])
            obj.save()
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        ingredients = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')
        tags_lst = []
        for tag in tags:
            tags_lst.append(tag)
        instance.tags.set(tags_lst)
        instance.ingredients.set([])
        instance.save()
        for ingredient in ingredients:
            obj = IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
            obj.save()
        return instance
