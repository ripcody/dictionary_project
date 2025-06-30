from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dictionary/', include('dictionary_app.urls', namespace='dictionary_app')),
    path('accounts/', include('django.contrib.auth.urls')), # This line
    path('', include('dictionary_app.urls', namespace='dictionary_app')),
]