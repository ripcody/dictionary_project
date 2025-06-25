# dictionary_app/models.py
from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=200, unique=True)
    definition = models.TextField()

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word'] # Default ordering for querysets