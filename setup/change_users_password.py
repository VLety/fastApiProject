from sqlalchemy.orm import Session
from passlib.context import CryptContext
import sys
import pathlib

# SET PYTHONPATH based on the directory from which the program is run
PROJECT_ROOT = str(pathlib.Path().resolve())
sys.path.append(PROJECT_ROOT)  #  Add to PYTHONPATH

# Add Project Package(s) based on PYTHONPATH
try:
    from util import get_setup, get_config, get_current_time_utc
    from sql_app.models import User
    from sql_app.database import get_db
except Exception as error:
    print("Exception:", error)
    print("Current PROJECT_ROOT:", PROJECT_ROOT)
    print("This program should be run from the root folder of the project!")

APP_CONFIG = get_config()
SUCCESSFUL_MESSAGE = "Password for Username 'user_name' successfully updated: "
FAILURE_MESSAGE = "Password for Username 'user_name' NOT updated!"
PWD_CONTEXT = CryptContext(schemes=APP_CONFIG["auth"]["PWD_CONTEXT"]["schemes"],
                           deprecated=APP_CONFIG["auth"]["PWD_CONTEXT"]["deprecated"])


def get_password_hash(plain_password: str) -> str:
    return PWD_CONTEXT.hash(plain_password)


def get_user_by_name(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def update_users_passwords(db: Session = get_db):
    print("We are starting to update user passwords >>>")
    for user in get_setup()["default_users"]:
        username = user["username"]
        plain_password = user["password"]
        hashed_password = get_password_hash(plain_password)

        # Check if User exists
        db_user = get_user_by_name(db=db, username=username)
        if db_user is None:
            print(FAILURE_MESSAGE)
        else:
            # Set new password
            db_user.hashed_password = hashed_password

            # Set update time-date
            db_user.updated = get_current_time_utc("TIME")

            # Update database
            db.commit()
            db.refresh(db_user)

            print(SUCCESSFUL_MESSAGE.replace("user_name", username) + plain_password)

    print(">>> User password update completed successfully!")


# calling next() on your generator to get a session out of the generator - FastAPI do this initially
update_users_passwords(db=next(get_db()))
