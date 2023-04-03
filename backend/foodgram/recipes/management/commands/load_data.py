from django.core.management import BaseCommand
from csv import DictReader

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Loads data from csv"

    def handle(self, *args, **options):

        print("Loading ingredients data")
        for row in DictReader(
                open('/app/recipes/data/ingredients.csv', encoding='utf-8')
        ):
            try:
                ingredient = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                ingredient.save()
            except Exception as err:
                continue
