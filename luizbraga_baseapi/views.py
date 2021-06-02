from django.shortcuts import render

# Create your views here.
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView

from luizbraga_baseapi import serializers


class LoginAuthToken(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = ApiUserSerializer(instance=user, read_only=True)
            data = {
                'token': token.key,
                'data': user_serializer.data
            }

            login(request, user)

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)