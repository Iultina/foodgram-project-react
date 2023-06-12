from django.contrib import admin

from .models import FavoritesList, Ingredient, Recipe, ShoppingList, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count') 
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'Количество подписанных пользователей на рецепт'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',) 
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug') 
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoritesList)
admin.site.register(ShoppingList)
