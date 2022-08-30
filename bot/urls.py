from django.urls import path

from bot import views

urlpatterns = []

urlpatterns += [
    path("verify", views.VerificationView.as_view()),
]