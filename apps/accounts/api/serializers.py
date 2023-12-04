from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


User = get_user_model()

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "This email is already registered.")

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        return User.objects.create_user(email=email,password=password)
