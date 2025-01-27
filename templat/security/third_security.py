from functools import wraps
from typing import Any
from typing import Dict
from typing import List

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from templat.core.dependencies import get_async_client
from templat.core.exceptions import AuthError
from templat.core.exceptions import BadRequestError
from templat.core.settings import settings


def authorize(roles: List[str], allow_same_id: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_role = kwargs.get("current_user")["role"]
            have_authorization = user_role in roles
            if allow_same_id:
                is_same_id = kwargs.get("current_user")["id"] == kwargs.get("user_id")
                if not is_same_id and not have_authorization:
                    raise AuthError("Not enough permissions")
                return await func(*args, **kwargs)
            if not have_authorization:
                raise AuthError("Not enough permissions")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Dict[str, Any]:  # type: ignore
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise AuthError(detail="Invalid authorization code")

        if credentials.scheme != "Bearer":
            raise AuthError(detail="Invalid authentication scheme")

        async for client in get_async_client():
            status_code, data = await self.get_data_from_token(credentials.credentials, client)
            if status_code != 200:
                raise AuthError(detail=data["detail"])
            return data

    async def get_data_from_token(self, token: str, client: ClientSession) -> tuple[int, Dict[str, Any]]:
        token = f"Bearer {token}"

        try:
            async with client.get(f"{settings.AUTH_SERVICE_ENDPOINT}", headers={"Authorization": token}) as response:
                status_code = response.status
                data = await response.json()
                if status_code != 200:
                    raise AuthError(detail=data["detail"])

                return status_code, data
        except ClientConnectionError as _:
            raise BadRequestError(detail="Auth Service not available")
