# dictionary_app/admin.py
from django.contrib import admin
from .models import Word

admin.site.register(Word)