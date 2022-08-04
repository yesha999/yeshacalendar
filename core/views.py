from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import User
from core.serialzers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer, ChangePasswordSerializer


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            login(request, user=user)
            user_serializer = UserSerializer(instance=user)
            return Response(user_serializer.data)
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user
