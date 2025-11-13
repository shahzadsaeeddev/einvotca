import json

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .keycloak import create_user, update_user, update_role, deactivate_user, reset_password_user
from .models import RoleGroup, Users


class KeycloakTokenSerializer(serializers.Serializer):
    """
    KeycloakTokenSerializer
    Used to retrieve a token from keycloak using basic auth
    """

    username = serializers.CharField(max_length=200, required=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class KeycloakRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=2500, required=True)


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleGroup
        fields = ['id', 'group_name']


class UsersSerializer(serializers.ModelSerializer):
    access_role = serializers.CharField(source='user_roles', read_only=True)
    uuid = serializers.CharField(source='slug', read_only=True)

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email','default_business_location', 'password', 'access_role', 'status', 'user_roles', 'username',
                  'uuid']
        extra_kwargs = {
            'user_roles': {'write_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'META'):
            auth_token = request.META.get('HTTP_AUTHORIZATION')
        else:
            auth_token = None
        if auth_token and auth_token.startswith('Bearer '):
            auth_token = auth_token.split(' ')[1]

            response, code = create_user(auth_token, **validated_data)
            if response.status_code != 201:
                raise ValidationError(json.loads(response.text))
            else:
                Users.objects.create(**validated_data, keycloak_uuid=code)
        return validated_data


class UsersDetailSerializer(serializers.ModelSerializer):
    access_role = serializers.CharField(source='user_roles', read_only=True)
    uuid = serializers.CharField(source='slug', read_only=True)
    scope = serializers.CharField(write_only=True)
    filter=serializers.CharField(source='user_roles.id', read_only=True)
    display_picture = serializers.FileField(source='display_picture.thumbnail', read_only=True)

    # def get_display_picture(self, obj):
    #     request = self.context.get('request')
    #     if obj.display_picture and obj.display_picture.thumbnail:
    #         return request.build_absolute_uri(obj.display_picture.thumbnail.url)
    #     return None


    class Meta:
        model = Users
        fields = ['scope', 'first_name', 'last_name','default_business_location', 'email', 'status', 'access_role', 'user_roles','password',
                  'uuid','filter', 'display_picture']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):

        request = self.context.get('request')
        if request and hasattr(request, 'META'):
            auth_token = request.META.get('HTTP_AUTHORIZATION')
        else:
            auth_token = None
        if auth_token and auth_token.startswith('Bearer '):
            auth_token = auth_token.split(' ')[1]
            scope = validated_data.pop('scope')
            # print(scope)
            if scope == 'update_profile':
                response = update_user(auth_token, instance.keycloak_uuid, **validated_data)
                if response.status_code != 204:
                    raise ValidationError(json.loads(response.text))
            elif scope == 'update_password':
                # print(validated_data)
                response = reset_password_user(auth_token, instance.keycloak_uuid, **validated_data)
                if response.status_code != 204:
                    raise ValidationError(json.loads(response.text))

            elif scope == 'update_role':
                assigned = validated_data['user_roles'].group_code
                default = instance.user_roles.group_code

                update_role(auth_token, instance.keycloak_uuid, default, assigned)

            elif scope == 'update_status':
                response = deactivate_user(auth_token, instance.keycloak_uuid, validated_data['status'])
                if response.status_code != 204:
                    raise ValidationError(json.loads(response.text))
            else:
                raise ValidationError({"errorMessage": "invalid scope value"})
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            return validated_data
