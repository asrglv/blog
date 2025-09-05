from accounts.models import User
from django.contrib.auth import password_validation
from rest_framework import serializers


class UserReadSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Used for representing users.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'surname', 'email',
                  'is_active', 'is_staff', 'is_superuser',
                  'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Used for creating users.
    """
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'surname', 'email',
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
    """
    Serializer for the User model.
    Used for updating users.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'surname', 'email']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        new_password = attrs['new_password']
        confirm_password = attrs['confirm_password']
        password_validation.validate_password(new_password)
        if new_password != confirm_password:
            raise serializers.ValidationError('New password and confirmation password do not match.')
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user