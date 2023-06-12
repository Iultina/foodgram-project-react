from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username',)
    list_filter = ('username', 'email',)

admin.site.register(User, UserAdmin)
admin.site.register(Follow)