import json
import os

import requests

from django.http import HttpResponse
from django.conf import settings
from rest_framework import permissions, generics, filters

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from neksio_api.tasks import activity_logs_task
from .keycloak import update_user, reset_password_user
from .models import RoleGroup, Users
from .permissions import HasUserAccountsRoles
from .serializer import KeycloakTokenSerializer, UserRoleSerializer, UsersSerializer, KeycloakRefreshTokenSerializer, \
    UsersDetailSerializer
from neksio_api.models import MediaFiles


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class GetKeycloakToken(ObtainAuthToken):
    permission_classes = ()
    serializer_class = KeycloakTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        base = settings.OIDC_HOST
        realm = settings.OIDC_REALM

        url = f"{base}/realms/{realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": settings.OIDC_RP_CLIENT_ID,
            "username": username,
            "password": password,
            "client_secret": settings.OIDC_RP_CLIENT_SECRET
        }

        response = requests.request("post", url, data=data)
        data = response.content.decode("utf-8")
        data = json.loads(data)

        token = data.get("access_token", None)
        refresh_token = data.get("refresh_token", None)
        if not token:
            return Response(data)
        return Response({
            "token": f"Bearer {token}",
            "refresh_token": refresh_token
        })


class GetKeycloakRefresh(ObtainAuthToken):
    permission_classes = ()
    serializer_class = KeycloakRefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # Use refresh token instead of username and password
        refresh_token = serializer.validated_data["refresh_token"]

        base = settings.OIDC_HOST
        realm = settings.OIDC_REALM

        url = f"{base}/realms/{realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "refresh_token",  # Changed grant_type to refresh_token
            "client_id": settings.OIDC_RP_CLIENT_ID,
            "refresh_token": refresh_token,
            "client_secret": settings.OIDC_RP_CLIENT_SECRET
        }
        response = requests.post(url, data=data)  # Changed to use requests.post for clarity
        data = response.json()  # Directly parsing JSON from response

        token = data.get("access_token", None)
        refresh_token = data.get("refresh_token", None)
        if not token:
            return Response(data)
        return Response({
            "token": f"Bearer {token}",
            "refresh_token": refresh_token
        })


class UserRolesView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserRoleSerializer

    def get_queryset(self):
        query = RoleGroup.objects.filter(visible=True)
        return query


class UserView(generics.ListCreateAPIView):
    permission_classes = [HasUserAccountsRoles]
    serializer_class = UsersSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']

    def get_queryset(self):
        query = Users.objects.filter(default_business_location=self.request.user.default_business_location,
                                     business_profile=self.request.user.business_profile)
        return query

    def perform_create(self, serializer):
        user = serializer.save(default_business_location=self.request.user.default_business_location,
                               business_profile=self.request.user.business_profile, collections=self.request.user.collections)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id, module="Users",
                                 action_type="create", description=f"Created new user",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasUserAccountsRoles]
    serializer_class = UsersDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        query = Users.objects.filter(default_business_location=self.request.user.default_business_location,
                                     business_profile=self.request.user.business_profile)
        return query

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = self.get_object()
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="User", action_type="update",
                                 description=f"Updated User {user.username}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="User", action_type="delete",
                                 description=f"Deleted User {user.username}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        user = Users.objects.filter(username=self.request.user.username).first()
        slz_data = UsersDetailSerializer(user, context={"request": request})
        return Response(data=slz_data.data, status=200)

    def patch(self, request, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = None

        if self.request.data['scope'] == 'update_profile':
            self.request.data.pop('scope')

            Users.objects.filter(username=self.request.user.username).update(**self.request.data)
            if "display_picture" in self.request.data:
                file = MediaFiles.objects.filter(id=self.request.data["display_picture"]).first().file
                self.request.data["display_picture"] = os.path.join("https://api.einvotca.com/", str(file))

            response = update_user(token, self.request.user.keycloak_uuid, **self.request.data)
            if response.status_code != 204:
                raise ValidationError(json.loads(response.text))
        elif self.request.data['scope'] == 'update_password':
            Users.objects.filter(username=self.request.user.username).first().update(**self.request.data)
            if 'password' not in self.request.data:
                raise ValidationError("Password fields is required for updating password")

            response = reset_password_user(token, self.request.user.keycloak_uuid, **self.request.data)
            if response.status_code != 204:
                raise ValidationError(json.loads(response.text))
        else:
            return Response(data={"message:invalid scope value", "status:200"}, status=400)
        return Response(data={"message:success", "status:200"}, status=200)
