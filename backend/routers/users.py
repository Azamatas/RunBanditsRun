from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.activity import Activity, SportType, Visibility
from backend.models.friendship import Friendship, FriendshipStatus
from backend.schemas.user import UserOut, UserUpdate
from backend.schemas.activity import ActivityOut
from backend.services import auth_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(body: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if body.username is not None and body.username != current_user.username:
        existing = auth_service.get_user_by_username(db, body.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/followers", response_model=list[UserOut])
def list_followers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    requester_ids = db.query(Friendship.requester_id).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == FriendshipStatus.ACCEPTED
    ).subquery()
    return db.query(User).filter(User.id.in_(requester_ids)).all()


@router.get("/me/following", response_model=list[UserOut])
def list_following(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    addressee_ids = db.query(Friendship.addressee_id).filter(
        Friendship.requester_id == current_user.id,
        Friendship.status == FriendshipStatus.ACCEPTED
    ).subquery()
    return db.query(User).filter(User.id.in_(addressee_ids)).all()


@router.get("/me/pending", response_model=list[UserOut])
def list_pending_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    requester_ids = db.query(Friendship.requester_id).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == FriendshipStatus.PENDING
    ).subquery()
    return db.query(User).filter(User.id.in_(requester_ids)).all()


@router.get("/me/requests")
def list_pending_requests_detailed(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendships = db.query(Friendship).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == FriendshipStatus.PENDING
    ).all()
    return [{"id": f.id, "requester_id": f.requester_id, "requester": UserOut.model_validate(db.query(User).filter(User.id == f.requester_id).first()), "status": f.status.value, "created_at": f.created_at.isoformat() if f.created_at else None} for f in friendships]


@router.get("/me/sent-requests")
def list_sent_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendships = db.query(Friendship).filter(
        Friendship.requester_id == current_user.id,
        Friendship.status == FriendshipStatus.PENDING
    ).all()
    return [{"id": f.id, "addressee_id": f.addressee_id, "status": f.status.value} for f in friendships]


@router.get("/search")
def search_users(q: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(User).filter(User.id != current_user.id)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    return query.limit(50).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/activities", response_model=list[ActivityOut])
def list_user_activities(
    user_id: int,
    sport_type: Optional[SportType] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    from sqlalchemy import or_, and_
    if user_id == current_user.id:
        visibility_filter = Activity.owner_id == current_user.id
    else:
        is_friend = db.query(Friendship).filter(
            Friendship.status == FriendshipStatus.ACCEPTED,
            ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
            ((Friendship.addressee_id == current_user.id) & (Friendship.requester_id == user_id))
        ).first() is not None
        if is_friend:
            visibility_filter = or_(
                Activity.visibility == Visibility.PUBLIC,
                Activity.visibility == Visibility.FRIENDS,
            ) & (Activity.owner_id == user_id)
        else:
            visibility_filter = (Activity.visibility == Visibility.PUBLIC) & (Activity.owner_id == user_id)
    query = db.query(Activity).filter(visibility_filter)
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return [{**a.__dict__, "kudos_count": len(a.kudos)} for a in activities]


@router.post("/{user_id}/follow", status_code=201)
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    existing = db.query(Friendship).filter(
        Friendship.requester_id == current_user.id,
        Friendship.addressee_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")
    db.add(Friendship(requester_id=current_user.id, addressee_id=user_id))
    db.commit()
    return {"status": "pending"}


@router.post("/{user_id}/accept", status_code=200)
def accept_follow(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendship = db.query(Friendship).filter(
        Friendship.requester_id == user_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == FriendshipStatus.PENDING
    ).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="No pending request")
    friendship.status = FriendshipStatus.ACCEPTED
    db.commit()
    return {"status": "accepted"}


@router.delete("/{user_id}/unfollow", status_code=204)
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendship = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
        ((Friendship.addressee_id == current_user.id) & (Friendship.requester_id == user_id))
    ).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="No friendship found")
    db.delete(friendship)
    db.commit()