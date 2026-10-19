from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_device_id
from ..schemas import MessageOut

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("", response_model=list[MessageOut])
def list_messages(device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    # the saved conversation, so the chat is still there after a refresh
    return crud.get_recent_messages(db, device_id)