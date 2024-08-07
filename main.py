from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get('/favicon.ico', include_in_schema=False)  # Exclude request from DOCS schema
def favicon():
    # https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
    return FileResponse("./static/favicon.ico")


# Dependency -> We need to have an independent database session/connection (SessionLocal) per request, use the same
# session through all the request and then close it after the request is finished. And then a new session will be
# created for the next request.
#
# Also, we can add "Alternative DB session" with middleware function (with relevant + and -)
# A "middleware" is basically a function that is always executed for each request,
# with some code executed before, and some code executed after the endpoint function.
# https://fastapi.tiangolo.com/tutorial/sql-databases/#alternative-db-session-with-middleware
# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         request.state.db = SessionLocal()
#         response = await call_next(request)
#     finally:
#         request.state.db.close()
#     return response
#
# # Dependency
# def get_db(request: Request):
#     return request.state.db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if unique User's identification attributes already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
