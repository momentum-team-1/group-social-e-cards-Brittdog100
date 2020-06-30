from django.contrib import admin

from .models import Card, User

admin.site.register(User)
admin.site.register(Card)
