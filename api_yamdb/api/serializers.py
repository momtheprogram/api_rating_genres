from rest_framework import serializers

from users.models import User, Roles


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для юзера
    """
    role = serializers.CharField(default=Roles.USER)

    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role', 'confirmation_code')
        model = User
        extra_kwargs = {'confirmation_code': {'write_only': True},
                        'username': {'required': True},
                        'email': {'required': True}}
