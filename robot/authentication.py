from rest_framework.authentication import BaseAuthentication
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from . import serializers
from . import models


class AppAuthentication(BaseAuthentication):

    def authenticate(self, request):
        serializer = serializers.AppModel(data=request.GET)
        if serializer.is_valid():
            app: models.AppModel = serializer.validated_data
            if app.bind_user is not None:
                return app.bind_user, app
            raise AuthenticationFailed(detail='该app未激活')
        raise AuthenticationFailed(serializer.errors)

