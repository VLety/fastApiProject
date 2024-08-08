from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from . import models, schemas
import util


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(first_name=user.first_name,
                          last_name=user.last_name,
                          nick_name=user.nick_name,
                          phone=user.phone,
                          email=user.email,
                          birthday=user.birthday,
                          country=user.country,
                          city=user.city,
                          address=user.address,
                          created=util.get_current_time_utc("TIME"))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user, user):
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.nick_name = user.nick_name
    db_user.phone = user.phone
    db_user.email = user.email
    db_user.birthday = user.birthday
    db_user.country = user.country
    db_user.city = user.city
    db_user.address = user.address
    db_user.updated = util.get_current_time_utc("TIME")

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user):
    db.delete(db_user)
    db.commit()

    # Response Model - Return Type
    # https://fastapi.tiangolo.com/tutorial/response-model/?h=#response-model-return-type
    return JSONResponse(content={"message": "User deleted successfully"})


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
