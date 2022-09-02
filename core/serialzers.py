from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from core.models import User

User: User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """дефолтный сериалайзер"""

    class Meta:
        model = User
        id = serializers.IntegerField(read_only=True)
        fields = ("id",
                  "username",
                  "first_name",
                  "last_name",
                  "email",
                  )


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True)

    def validate(self, attrs: dict):
        password = attrs.get("password")
        password_repeat = attrs.pop("password_repeat", None)

        if password_repeat == password:
            return attrs
        else:
            raise ValidationError("Введенные пароли не одинаковы")

    def create(self, validated_data: dict):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data["password"])

        user.save()
        return user

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_repeat', 'username')


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs: dict):
        self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
        if self.user:
            return attrs
        else:
            raise serializers.ValidationError("Введенные данные неверны")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('old_password', "new_password")

    def validate(self, attrs: dict):
        old_password = attrs.get("old_password")
        user = self.instance
        if not user.check_password(old_password):
            raise ValidationError("Введен неверный старый пароль")
        return attrs

    def update(self, instance: User, validated_data: dict):
        instance.set_password(validated_data["new_password"])
        instance.save(update_fields=["password"])
        return instance
