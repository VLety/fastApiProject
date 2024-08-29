from sql_app import auth
from util import get_setup

SUCCESSFUL_MESSAGE = "Password for User user_name successfully updated:"

for user in get_setup()["users"]:
    username = user["username"]
    plain_password = user["password"]
    hashed_password = auth.get_password_hash(plain_password)

    print(SUCCESSFUL_MESSAGE.replace("user_name", username) + ": " + plain_password)
