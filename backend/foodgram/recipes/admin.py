from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 3


class IngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author'
    )
    inlines = (
        TagsInline,
        IngredientsInline
    )
    fields = ('name', 'author', 'image', 'text', 'cooking_time')

@admin.register(Tag)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )

@admin.register(Ingredient)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )