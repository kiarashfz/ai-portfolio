# from ec_helpers.handlers import CustomHTTPException
# from fastapi import Depends, status, Header
# from .dependencies import get_session
# from sqlalchemy.ext.asyncio import AsyncSession
# from pydantic import BaseModel
# from typing import List
#
#
# class Profile(BaseModel):
#     username: str
#     phone_number: str
#     roles: List[str]
#
#
# class Authorization:
#     def __init__(self, permission: str | None = None):
#         self.permission = APIPermission(name=permission) if permission else None
#
#     async def __call__(
#         self,
#         authorization: str = Header(default=""),
#         session: AsyncSession = Depends(get_session),
#         auth_service: AuthService = Depends(get_auth_service),
#         user_management_service: UserService = Depends(get_user_service),
#     ) -> Profile:
#
#         if not authorization:
#             raise CustomHTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 type="/unauthorized",
#                 title="Unauthorized",
#                 details="Missing authorization header",
#             )
#
#         parts = authorization.split(" ")
#         if parts[0] != "Bearer":
#             raise CustomHTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 type="/unauthorized",
#                 title="Unauthorized",
#                 details="Invalid authorization header",
#             )
#
#         try:
#             token = parts[1]
#         except Exception:
#             raise CustomHTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 type="/unauthorized",
#                 title="Unauthorized",
#                 details="Invalid authorization header",
#             )
#
#         authorization_status = await auth_service.authorization(token=token)
#         if not authorization_status["is_authorized"]:
#             if authorization_status["error"] == "expired_token":
#                 raise CustomHTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     type="/unauthorized",
#                     title="Unauthorized",
#                     details="Expired token",
#                 )
#             else:
#                 raise CustomHTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     type="/unauthorized",
#                     title="Unauthorized",
#                     details="Invalid token",
#                 )
#         payload = authorization_status["payload"]
#
#         if self.permission and not await user_management_service.has_permission(
#             session=session, roles=payload["roles"], permission=self.permission.name
#         ):
#             raise CustomHTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 type="/forbidden",
#                 title="Forbidden",
#                 details="No permission",
#             )
#
#         return Profile(
#             username=payload["username"],
#             phone_number=payload["phone_number"],
#             roles=payload["roles"],
#         )
#
#
# class APIPermission:
#     _instance_names = set()
#
#     def __init__(self, name: str):
#         if not isinstance(name, str):
#             raise ValueError("Invalid name for API permission")
#
#         parts = name.split("-")
#         if 1 > len(parts) > 3:
#             raise ValueError("Invalid name for API permission.")
#         for part in parts:
#             if not part.isidentifier():
#                 raise ValueError("Invalid name for API permission..")
#
#         APIPermission._instance_names.add(name)
#         self.name = name
#
#     @classmethod
#     def get_instances_list(cls):
#         return list(cls._instance_names)
