"""
https://fastapi.tiangolo.com/tutorial/sql-databases/#sql-relational-databases
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import util

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = f"sqlite:////{util.get_project_root()}{util.get_config()['sqlite_db_path']}"

# connect_args is needed only for SQLite. It's not needed for other databases!
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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