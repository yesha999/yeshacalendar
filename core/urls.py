from django.urls import path

from core import views

urlpatterns = [
    path('signup', views.UserCreateView.as_view()),
    path('login', views.UserLoginView.as_view()),
    path('profile', views.UserDetailView.as_view()),
    path('update_password', views.ChangePasswordView.as_view()),
]
