from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название тега', unique=True, max_length=200)
    color = ColorField('Цвет', unique=True, default='#FF0000')
    slug = models.SlugField('Слаг тега', unique=True, max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', unique=True, max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField('Название рецепта', unique=True, max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name="Автор отзыва"
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='backend-media/recipes/images/'
    )
    text = models.TextField('Рецепт')
    ingredients = models.ManyToManyField(Ingredient, verbose_name="Ингредиенты",
                                         through='IngredientInRecipe')
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    cooking_time = models.IntegerField(validators=[
        MinValueValidator(1,
                          "Время приготовления не может быть менее 1 минуты")
    ],
        verbose_name="Время приготовления, мин"
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[
        MinValueValidator(1,
                          "Количество должно быть числом более 1")
    ])


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='favorite_recipe',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='favorite_user',
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user', ],
                name='unique_favorite'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingList(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_to_shopping',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_shopping_list',
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user', ],
                name='unique_shopping_list'
            )
        ]
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='following',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author', ],
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
