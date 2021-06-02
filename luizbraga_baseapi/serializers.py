from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from rest_framework import serializers

from luizbraga_baseapi.models import ApiUser


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(
        label=_('Password'),
        style={'input_type': 'password'},
        trim_whitespace=False,
        max_length=255,
        write_only=True
    )

    def authenticate(self, **kwargs):
        return authenticate(self.context.get('request'), **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg)

        return user

    def _validate_username_email(self, username_email, password):
        msg = {}
        if not username_email:
            msg["username"] = _('required')

        if not password:
            msg["password"] = _('required')

        if len(msg) > 0:
            raise serializers.ValidationError([msg])

        try:
            validate_email(username_email)
            user = self.authenticate(email=username_email, password=password)
        except serializers.ValidationError:
            user = self.authenticate(user=username_email, password=password)

        return user

    def validate(self, data):
        user_email = data.get('username', None)
        password = data.get('password', None)

        user = self._validate_username_email(user_email, password)
        if not user:
            raise serializers.ValidationError(
                _('User not found'),
                code='authorization'
            )
        data['user'] = user
        return data


class ApiUserSerializer(DynamicFieldsModelSerializer):
    permissions = serializers.SerializerMethodField('list_permissions')
    # full_name = serializers.SerializerMethodField('')

    def get_full_name(self, user):
        return user.full_name

    def list_permissions(self, user):
        permissions = []
        for permission in user.get_group_permissions().union(user.get_user_permissions()):
            permissions.append(permission)
        return permissions

    class Meta:
        model = ApiUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'is_active', 'is_staff', 'is_superuser', 'permissions')
