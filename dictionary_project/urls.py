# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('dictionary/', include('dictionary_app.urls', namespace='dictionary_app')),
#     path('accounts/', include('django.contrib.auth.urls')), # This line
#     path('', include('dictionary_app.urls', namespace='dictionary_app')),
# ]


# File: dictionary_project/urls.py
# This is your project's main URL configuration file.

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # This line tells Django to look for URLs in your app's urls.py
    path("", include('dictionary_app.urls')),
    path("admin/", admin.site.urls),
    path('dictionary/', include('dictionary_app.urls', namespace='dictionary_app')),
    path('accounts/', include('django.contrib.auth.urls')), # This line
    path('', include('dictionary_app.urls', namespace='dictionary_app')),
]