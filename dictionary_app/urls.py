from django.urls import path
from . import views # Import views from the current directory

app_name = 'dictionary_app' # Namespace for your app's URLs

urlpatterns = [
    path('', views.add_word, name='home'), # Redirects home to add_word
    path('add/', views.add_word, name='add_word'),
    path('search/', views.search_word, name='search_word'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('view/', views.view_all_words, name='view_all_words'),
]