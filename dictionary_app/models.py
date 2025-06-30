from django.db import models
from django.conf import settings

class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    definition = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dictionary_words',
        null=True, # Keep null=True for existing data, consider changing for new projects
        blank=True
    )
    class Meta:
        ordering = ['word']
    def __str__(self):
        return self.word