
import re
import logging
from django.conf import settings
from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakInvalidTokenError,\
    raise_error_from_response, KeycloakGetError, KeycloakAuthenticationError
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
import json

logger = logging.getLogger(__name__)


class AuthentificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.config = settings.KEYCLOAK_IAM_CLIENT_CONFIG
        try:
            self.server_url = self.config['KEYCLOAK_SERVER_URL']
            self.client_id = self.config['KEYCLOAK_CLIENT_ID']
            self.realm = self.config['KEYCLOAK_REALM']
        except KeyError:
            raise Exception(
                "KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")

        self.client_secret_key = self.config.get(
            'KEYCLOAK_CLIENT_SECRET_KEY', None)
        self.client_public_key = self.config.get(
            'KEYCLOAK_CLIENT_PUBLIC_KEY', None)
        self.default_access = self.config.get(
            'KEYCLOAK_DEFAULT_ACCESS', "DENY")
        self.method_validate_token = self.config.get(
            'KEYCLOAK_METHOD_VALIDATE_TOKEN', "INTROSPECT")
        self.keycloak_authorization_config = self.config.get(
            'KEYCLOAK_AUTHORIZATION_CONFIG', None)

        self.keycloak = KeycloakOpenID(server_url=self.server_url,
                                       client_id=self.client_id,
                                       realm_name=self.realm,
                                       client_secret_key=self.client_secret_key)

    @property
    def keycloak(self):
        return self._keycloak

    @keycloak.setter
    def keycloak(self, value):
        self._keycloak = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def server_url(self):
        return self._server_url

    @server_url.setter
    def server_url(self, value):
        self._server_url = value

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def client_secret_key(self):
        return self._client_secret_key

    @client_secret_key.setter
    def client_secret_key(self, value):
        self._client_secret_key = value

    @property
    def client_public_key(self):
        return self._client_public_key

    @client_public_key.setter
    def client_public_key(self, value):
        self._client_public_key = value

    @property
    def realm(self):
        return self._realm

    @realm.setter
    def realm(self, value):
        self._realm = value

    @property
    def keycloak_authorization_config(self):
        return self._keycloak_authorization_config

    @keycloak_authorization_config.setter
    def keycloak_authorization_config(self, value):
        self._keycloak_authorization_config = value

    @property
    def method_validate_token(self):
        return self._method_validate_token

    @method_validate_token.setter
    def method_validate_token(self, value):
        self._method_validate_token = value

    def __call__(self, request):
        print("queryString",  request.META.get('QUERY_STRING', ''))
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(settings, 'KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS'):
            path = request.path_info.lstrip('/')

            if any(re.match(m, path) for m in
                   settings.KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS):
                logger.debug('** exclude path found, skipping')
                return None
        if 'HTTP_AUTHORIZATION' not in request.META:
            token_request = request.META.get('QUERY_STRING' , "")
            print('token_request' , token_request)
            print("init =====" ,  request.GET , request.META)
            initToken = token_request.split('init=')[-1].split("&")[0]
            request_type = request.META.get('CONTENT_TYPE' , '')
            print('text/html' == request_type , 'text/plain' == request_type)
            if not initToken and not 'text/html' == request_type and not 'text/plain' == request_type:
                return JsonResponse({"detail": NotAuthenticated.default_detail},
                                    status=NotAuthenticated.status_code)
            else:
                token = initToken
        else:
            auth_header = request.META.get('HTTP_AUTHORIZATION').split()
            token = auth_header[1] if len(auth_header) == 2 else auth_header[0]

        try:
            user = self.keycloak.userinfo(token)
            request.authUser = user

        except KeycloakInvalidTokenError:
            return JsonResponse({"detail": AuthenticationFailed.default_detail,
                                 "code": settings.CUSTOM_ERRORS_TEXT['AUTHENTIFICATION_FAILLED']},
                                status=AuthenticationFailed.status_code)
        except KeycloakAuthenticationError as e:
            return JsonResponse({"detail": "Token Expiré veuillez refresh",
                                 "code": settings.CUSTOM_ERRORS_TEXT['REFRESH_TOKEN']},
                                status=AuthenticationFailed.status_code)

        return None
