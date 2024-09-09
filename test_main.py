"""
Project name: REST API server solution based on FastAPI framework with RBAC model
Author: Volodymyr Letiahin
Contact: https://www.linkedin.com/in/volodymyr-letiahin-0208a5b2/
License: MIT
"""
from pytest_assert_utils import util as pt_util
from fastapi.testclient import TestClient
from main import app, APP_CONFIG
import util

TestApiServer = TestClient(app)
api_root_path = APP_CONFIG["root_path"]

valid_admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6W10sImV4cCI6MTcyNTg4Njk5Mn0._l-zoVntv746x7sS0aUkh8A4IL3krvsJV_Dj1bGOcjM"
expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6W10sImV4cCI6MTcyNTg3MzIyNX0.BnQ0CRDKkKUzvlkkeF_J3_QeipIIR9BkuAQpoz7ZJ0Y"
wrong_token = "Wrong Token!!!"

valid_admin_header = {"accept": "application/json", "Authorization": "Bearer " + valid_admin_token}
expired_header = {"accept": "application/json", "Authorization": "Bearer " + expired_token}
wrong_header = {"accept": "application/json", "Authorization": "Bearer " + wrong_token}
valid_manager_header = {"accept": "application/json", "Authorization": "Bearer "}

new_manager_user = {
    "username": "IAmManager",
    "first_name": "Jones",
    "last_name": "Smith",
    "phone": "+380504430000",
    "email": "user@gmail.com",
    "role": [
        "manager"
    ],
    "disabled": False,
    "login_denied": False
}
new_manager_user_password = "passWord@8"

new_employee = {
    "first_name": "Marry",
    "last_name": "Fox",
    "nick_name": "Bravo",
    "phone": "+380504430000",
    "email": "user@gmail.com",
    "birthday": "1998-06-01",
    "country": "Ukraine",
    "city": "Kyiv",
    "address": "Khreschatyk St, 14, UA 01001"
}

new_ticket = {
    "title": "Network problem",
    "description": "The employee cannot access network resources.",
    "status": "New"
}


def print_response(response):
    print("\n" + "Response:")
    util.print_json(response.json())


def test_read_me_wrong_token():
    response = TestApiServer.get(api_root_path + "/me", headers=wrong_header)
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["could_not_validate_credentials"]["status_code"]
    assert response.json() == {
        "detail": APP_CONFIG["raise_error"]["could_not_validate_credentials"]["detail"]
    }


def test_read_me_expired_token():
    response = TestApiServer.get(api_root_path + "/me", headers=expired_header)
    print_response(response)

    assert response.status_code == APP_CONFIG["raise_error"]["token_has_expired"]["status_code"]
    assert response.json() == {
        "detail": APP_CONFIG["raise_error"]["token_has_expired"]["detail"]
    }


def test_create_new_support_user():
    # Add password
    new_support_user_with_password = new_manager_user.copy()
    new_support_user_with_password["password"] = new_manager_user_password

    response = TestApiServer.post(api_root_path + "/user/",
                                  headers=valid_admin_header,
                                  json=new_support_user_with_password)
    print_response(response)

    new_manager_user["id"] = response.json()["id"]
    new_manager_user["created"] = response.json()["created"]
    new_manager_user["updated"] = response.json()["updated"]

    assert response.status_code == 200
    assert response.json() == new_manager_user


def test_get_new_manager_user_token():
    response = TestApiServer.post(api_root_path + "/token", data={
        "username": new_manager_user["username"],
        "password": new_manager_user_password
    })
    print_response(response)

    valid_manager_header["Authorization"] = valid_manager_header["Authorization"] + response.json()["access_token"]

    assert response.status_code == 200
    assert response.json() == {
        "access_token": pt_util.Any(str),
        "token_type": "bearer"
    }


def test_read_me():
    response = TestApiServer.get(api_root_path + "/me", headers=valid_manager_header)
    print_response(response)

    assert response.status_code == 200
    assert response.json() == new_manager_user


def test_read_status():
    response = TestApiServer.get(api_root_path + "/status", headers=valid_manager_header)
    print_response(response)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_employee():
    response = TestApiServer.post(api_root_path + "/employee", headers=valid_manager_header, json=new_employee)
    print_response(response)

    new_employee["id"] = response.json()["id"]
    new_employee["created"] = response.json()["created"]
    new_employee["updated"] = response.json()["updated"]
    new_employee["tickets"] = response.json()["tickets"]

    assert response.status_code == 200
    assert response.json() == new_employee
