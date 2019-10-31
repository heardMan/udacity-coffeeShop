import json
from flask import request, _request_ctx_stack, abort, Response
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-y5wb70ja.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'drinks'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def check_permissions(permission, payload):
    '''this is a test payload with no permissions property'''

    permissions = []
    
    if type(permission) is not str:
        _permissions_ = permission.split(',')
        for _permission_ in _permissions_:
            permissions.append(_permission_)

    if payload.get('permissions') is None and payload.get('gty') is None:
        raise AuthError({
            'code': 'no_permissions_found_on_jwt_payload',
            'description': 'Expected a permissions property on the payload but one was not found'
        }, 401)

    elif payload.get('gty') == 'client-credentials':
        permissions.append('testing')
        return True

    elif payload.get('permissions') is not None:
        
        acceptable_permissions = [
            'get:drinks',
            'get:drinks-detail',
            'post:drinks',
            'delete:drinks',
            'patch:drinks'
        ]
        

        user_permissions = payload['permissions']
        for user_permission in user_permissions:
            if user_permission not in acceptable_permissions:
                abort(401)
            permissions.append(user_permission)
        if len(permissions) <= 0:
            raise AuthError({
                'code': 'no_permissions_found',
                'description': 'Expected to find some user permission but found none'
            }, 401)
        return True
        
    elif payload.get('gty') == 'client-credentials':
        permissions.append('testing')
        return True
    
    return False

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as err:
                abort(401, err.error)
            
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator