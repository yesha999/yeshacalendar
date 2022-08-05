from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [path("core/", include("core.urls"))]
urlpatterns += [path('', include('social_django.urls'))]
