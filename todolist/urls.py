from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [path("core/", include("core.urls"))]
urlpatterns += [path("goals/", include("goals.urls"))]
urlpatterns += [path('oauth/', include('social_django.urls', namespace="social"))]
