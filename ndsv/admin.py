from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ApiUser

# Register your models here.

admin.site.register(ApiUser, UserAdmin)
