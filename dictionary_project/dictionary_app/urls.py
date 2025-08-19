# File: dictionary_project/myapp/urls.py
# This is your application's URL configuration.

from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    # Add other paths for your app here
    # For example:
    # path("home/", views.home, name="home"),
    path('', views.add_word, name='home'), # Redirects home to add_word
    path('add/', views.add_word, name='add_word'),
    path('search/', views.search_word, name='search_word'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('view/', views.view_all_words, name='view_all_words'),
    # NEW: Endpoint for AJAX definition fetching
    path('get_definition_ajax/', views.get_definition_ajax, name='get_definition_ajax'),
]