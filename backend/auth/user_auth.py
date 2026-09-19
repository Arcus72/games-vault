
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.orm import Session
from fastapi import Request, Depends, HTTPException, Response
from database.models import UserSession
from database.database import get_db

def authenticate_session(request: Request, response: Response, db: Session = Depends(get_db)):
    session_id = request.cookies.get("user_session_id")
    if not session_id:
        return create_new_session(response, db)
    db_session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    if db_session and db_session.expires_at > datetime.now():
        return db_session
    if db_session:
        db.delete(db_session)
        db.commit()
        return create_new_session(response, db)
    return create_new_session(response, db)

def authenticate_user(request: Request, usersession: UserSession = Depends(authenticate_session)):
    if usersession.user_id is not None:
        return usersession
    raise HTTPException(status_code=401, detail="Użytkownik nie jest zalogowany lub sesja wygasła.")

def create_new_session(response: Response, db: Session, user_id: int = None):
    session_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    new_session = UserSession(session_id=session_id, user_id=user_id, created_at=datetime.now(timezone.utc), expires_at=expires_at)
    db.add(new_session)
    db.commit() 
    response.set_cookie(key="user_session_id", value=session_id, httponly=True, expires=expires_at)
    return new_session

def attach_user_to_session(session_id: str, user_id: int, db: Session):
    db_session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    if db_session:
        db_session.user_id = user_id
        db.commit()
        return db_session
    raise HTTPException(status_code=404, detail="Session not found")