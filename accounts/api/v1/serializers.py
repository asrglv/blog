from accounts.models import User
from django.contrib.auth import password_validation
from rest_framework import serializers


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'surname', 'email',
                  'is_active', 'is_staff', 'is_superuser',
                  'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'name', 'surname', 'email',
                  'password', 'password2']

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except password_validation.ValidationError as e:
            raise serializers.ValidationError(e)
        return value

    def validate_password2(self, value):
        password = self.initial_data.get('password')
        if value != password:
            raise serializers.ValidationError('Passwords do not match.')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'name', 'surname', 'email']