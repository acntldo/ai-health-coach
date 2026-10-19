from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_device_id

router = APIRouter(prefix="/api/entries", tags=["entries"])


@router.delete("/{entry_id}", status_code=204)
def remove_entry(
    entry_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    if not crud.delete_entry(db, device_id, entry_id):
        # same answer for "doesn't exist" and "belongs to someone else", so ids can't be probed
        raise HTTPException(status_code=404, detail="Entry not found")