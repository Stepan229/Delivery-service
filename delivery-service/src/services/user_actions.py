import logging
from typing import Optional
from uuid import UUID
from repositories.dals import UserSessionDAL

from h11 import Response

from fastapi import Request, Response


from domain.dto import UserSessionData

async def create_new_session_user(response: Response) -> UserSessionData:
    user_session_dal = UserSessionDAL()
    user = await user_session_dal.create_session()    
    return user

async def get_or_create_user(session_id: UUID) -> Optional[UUID]:
    "Возвращает идентификатор сессии"
    if not session_id:
        user_session = await create_new_session_user(response)
        return user_session.id_session

async def get_user(request: Request, response: Response) -> UserSessionData:
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        session_id = request.cookies.get("session_id")

    
    user_session_dal = UserSessionDAL()
    if session_id:
        user, created = await user_session_dal.get_or_create_user(UUID(session_id))
    else:
        user = await user_session_dal.create_session()
        created = True
    if created:
        response.set_cookie(key="session_id", 
                    value=str(user.id_session),
                    httponly=True,
                    samesite="lax")
    return user